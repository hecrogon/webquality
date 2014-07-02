# -*- coding: utf-8 -*-
from scrapy import log
from scrapy.http import Response
from scrapy.selector import Selector
from urlparse import urlparse
from tidylib import tidy_document
from urlparse import urlparse

from twisted.internet import reactor
from twisted.internet.defer import Deferred
from twisted.internet.protocol import Protocol
from twisted.web.client import Agent
from twisted.web.http_headers import Headers

from PIL import ImageFile

import enchant
from enchant.checker import SpellChecker
from lxml.html.clean import clean_html, Cleaner

from time import time

import webquality.settings

import sys, os
sys.path.append('/home/hector/develop/webquality')
os.environ['DJANGO_SETTINGS_MODULE'] ='webquality.settings'
from admin_wq.models import Execution, Page, Result, Website
from django.core.exceptions import ObjectDoesNotExist

class PageMiddleware(object):
    def process_request(self, request, spider):
#        log.msg("Request " + request.url, level=log.INFO)
        parts = urlparse(request.url)
        if parts[1] in spider.allow_domains:
            try:
                page = Page.objects.get(url=request.url)
            except Page.DoesNotExist:
                page = Page(url=request.url, user=spider.user, website=spider.website)
                page.save()

            if not request.url in spider.pages:
                spider.pages[request.url] = page

        return None

"""
    ValidatorMiddlewareBase
"""

class ValidatorMiddlewareBase(object):
    page = None
#    def __init__(self, *args, **kwargs):
#        log.msg("R1", level=log.INFO)

"""
    W3C Validator to check HTML
"""
class W3CValidatorMiddleware(ValidatorMiddlewareBase):
#    w3c_validator = 'http://validator.w3.org/'

    def process_response(self, request, response, spider):
        domain = urlparse(response.url).netloc
        if 'W3CValidator' in spider.validators and domain in spider.allow_domains:
            validator = spider.validators['W3CValidator']
            page = spider.pages.get(response.url)

            errors_json = { "page": response.url, "errors": [] }

            document, errors = tidy_document(response.body, options={ 'numeric-entities': 1 })
            for error in errors.split('\n'):
#                if error not in spider.errors:
                errors_json['errors'].append({ "error": error })
#                    spider.errors[error] = True

            result = Result(description=errors_json, execution=spider.execution, page=page, validator=validator)
            result.save()

        return response

"""
    BrokenLinksValidator
"""
class BrokenLinksMiddleware(ValidatorMiddlewareBase):
    def process_response(self, request, response, spider):
        if 'BrokenLinksValidator' in spider.validators:
            validator = spider.validators['BrokenLinksValidator']
            page = spider.pages.get(request.url)

        return response

    def process_exception(self, request, exception, spider):
        if 'BrokenLinksValidator' in spider.validators:
            validator = spider.validators['BrokenLinksValidator']
            page = spider.pages.get(request.headers['Referer'])
            try:
                result = Result.objects.get(execution=spider.execution, page=page, validator=validator)
            except ObjectDoesNotExist:
                errors_json = { "page": request.url, "errors": [] }
                result = Result(description=errors_json, execution=spider.execution, page=page, validator=validator)

            result.description['errors'].append({ "error": str(exception) })
            result.save()

        return None

"""
    Image Validator
"""
class CheckImage(Protocol):
    def __init__(self, finished, filesize, spider, page, validator, url):
        self.finished = finished
        self.filesize = filesize
        self.url = url
        self.spider = spider 
        self.page = page
        self.validator = validator
        self.width = None
        self.height = None

    def dataReceived(self, body):
        p = ImageFile.Parser()
        p.feed(body)
        (self.width, self.height) = p.image.size
#        log.msg("B1 " + " " + self.url + " " + str(self.filesize) + " " + str(p.image.size), level=log.INFO)
        try:
            result = Result.objects.get(execution=self.spider.execution, page=self.page, validator=self.validator)
        except ObjectDoesNotExist:
            errors_json = { "page": self.page.url, "errors": [] }
            result = Result(description=errors_json, execution=self.spider.execution, page=self.page, validator=self.validator)

        width = int(self.spider.parameters["ImagesValidator"]["fields"]["width"])
        height = int(self.spider.parameters["ImagesValidator"]["fields"]["height"])
        size = int(self.spider.parameters["ImagesValidator"]["fields"]["size"])

        if self.filesize > size * 1024:
            result.description['errors'].append({ "url": self.url, "error": "Tamaño del fichero demasiado grande." })
        if self.width > width or self.height > height:
            result.description['errors'].append({ "url": self.url, "error": "Imagen demasiado grande." })

        if len(result.description["errors"]) > 0:
            result.save()

    def connectionLost(self, reason):
        self.finished.callback(None)

class ImagesValidatorMiddleware(ValidatorMiddlewareBase):
    def handleResponse(self, response, spider, page, validator, url):
        finished = Deferred()
        response.deliverBody(CheckImage(finished, response.length, spider, page, validator, url))
        return finished

    def handleError(self, reason, url):
        log.msg("Error in Images Validator: " + url + " " + str(reason), level=log.INFO)
        pass

    def process_response(self, request, response, spider):
        domain = urlparse(response.url).netloc
        if 'ImagesValidator' in spider.validators and domain in spider.allow_domains:
            validator = spider.validators['ImagesValidator']
            page = spider.pages.get(response.url)

            try:
                sel = Selector(response)
                for url in sel.xpath('//img/@src').extract():
                    if url.startswith('/'):
                        url = "http://" + page.website.domain + url

                    if len(url) > 0:
                        agent = Agent(reactor)
                        d = agent.request('GET', str(url), Headers({'User-Agent': [webquality.settings.SCRAPY_USER_AGENT]}), None)
                        d.addCallback(self.handleResponse, spider, page, validator, url)
                        d.addErrback(self.handleError, url)

            except AttributeError:
                pass

        return response

"""
    SpellingValidator
"""
class SpellingMiddleware(ValidatorMiddlewareBase):
    def check_errors(self, langs, text):
        errors = []
        for lang in langs:
            if lang in enchant.list_languages():
                chkr = SpellChecker(lang)
                chkr.set_text(text)

                errors_set = set()
                for err in chkr:
                    errors_set.add(err.word)
                errors.append(errors_set)

        return set.intersection(*errors)

    def process_response(self, request, response, spider):
        domain = urlparse(response.url).netloc
        if 'SpellingValidator' in spider.validators and domain in spider.allow_domains:
            if 'text/html' in response.headers['Content-Type']:
                validator = spider.validators['SpellingValidator']
                page = spider.pages.get(response.url)

                cleaner = Cleaner(scripts=True, embedded=True, meta=True, page_structure=True, links=True, style=True, processing_instructions=True, annoying_tags=True,
                        remove_tags = ['a', 'ul', 'li', 'table', 'tr', 'td', 'div', 'span', 'img', 'p', 'h1', 'h2', 'h3', 'strong', 'body', 'br'])
                text = cleaner.clean_html(response.body) 

                lang = spider.parameters["SpellingValidator"]["fields"]["language"]
                errors = self.check_errors({lang, "en_GB"}, text)
                errors_json = { "page": response.url, "errors": [] }
                for error in errors:
                    errors_json['errors'].append({ "error": error })

                result = Result(description=errors_json, execution=spider.execution, page=page, validator=validator)
                result.save()

        return response

"""
    DownloadValidator
"""
class DownloadTimeMiddleware(ValidatorMiddlewareBase):
    def process_request(self, request, spider):
        request.meta['__start_time'] = time()
        return None

    def process_response(self, request, response, spider):
        domain = urlparse(response.url).netloc
        if 'DownloadTimeValidator' in spider.validators and domain in spider.allow_domains:
            validator = spider.validators['DownloadTimeValidator']
            page = spider.pages.get(response.url)

            start_time = request.meta['__start_time']
            end_time = time()

            limit_time = float(spider.parameters["DownloadTimeValidator"]["fields"]["time"])
            if end_time - start_time > limit_time:
                log.msg("R1 " + request.url + "   " + str(end_time) + " - " + str(request.meta['__start_time']) + " = " + str(end_time - request.meta['__start_time']), level=log.INFO)
                errors_json = { "page": response.url, "errors": [] }
                errors_json['errors'].append({ "error": "Download Time exceded (> " + str(limit_time) + ")"})
                result = Result(description=errors_json, execution=spider.execution, page=page, validator=validator)
                result.save()

        return response

#    def process_exception(self, request, exception, spider):
#        request.meta['__end_time'] = time()
#        return Response(
#            url=request.url,
#            status=110,
#            request=request)

