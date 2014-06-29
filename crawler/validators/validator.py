# -*- coding: utf-8 -*-
from scrapy import log
from scrapy.selector import Selector

from twisted.internet import reactor
from twisted.web.client import Agent
from twisted.web.http_headers import Headers
from twisted.internet.defer import Deferred
from twisted.internet.protocol import Protocol

from tidylib import tidy_document
from PIL import Image

import webquality.settings

import urllib
import requests
import json
import sys, os

sys.path.append('/home/hector/develop/webquality')
os.environ['DJANGO_SETTINGS_MODULE'] ='webquality.settings'
from wqinterfaz.models import Execution, Result, Website
from django.db import transaction

import cStringIO

"""
	ValidatorBase
"""
class ValidatorBase(object):
    response = []
    execution = None
    page = None
    validator = None

    def run(self, execution, page, validator):
        pass

"""
	W3C Validator to check HTML
"""
class W3CValidator(ValidatorBase):
    w3c_validator = 'http://validator.w3.org/'

    def __init__(self, response):
        self.response = response

    def run(self, execution, page, validator):
        self.execution = execution
        self.page = page
        self.validator = validator

        errors_json = { "page": self.response.url, "errors": [] }

        document, errors = tidy_document(self.response.body, options={'numeric-entities': 1})
        for error in errors.split('\n'):
            errors_json['errors'].append({ "error": error })

        result = Result(description=errors_json, execution=self.execution, page=self.page, validator=self.validator)
        result.save()

"""
	Broken Links Validator
"""
class BrokenLinksValidator(ValidatorBase):
    checked_urls = {}

    def __init__(self, response):
        self.response = response
        self.checked_urls[response.url] = True

    def handleResponse(self, response):
        pass

    def handleError(self, reason):
        with transaction.commit_manually():
            try:
                result = Result.objects.get(execution=self.execution, page=self.page, validator=self.validator)
                errors_json = result.description
            except:
                result = Result(execution=self.execution, page=self.page, validator=self.validator)
                errors_json = { "page": self.response.url, "errors": [] }

            errors_json['errors'].append({ "error": reason.getErrorMessage() })

            result.description = errors_json
            result.save()
            transaction.commit()

    def run2(self, execution, page, validator):
        self.execution = execution
        self.page = page
        self.validator = validator

        try:
            sel = Selector(self.response)

            for url in sel.xpath('//a/@href|//img/@src').extract():
                if url.startswith('/'):
                    url = "http://" + page.website.domain + url

                if url not in self.checked_urls:
                    self.checked_urls[url] = True

                    if not url.startswith('#') and not url.lower().startswith('mailto') and not url.lower().startswith('javascript'):
                        log.msg("B0 " + url, level=log.INFO)
                        agent = Agent(reactor)
#                        d = agent.request('GET', str(url), Headers({'User-Agent': [webquality.settings.SCRAPY_USER_AGENT]}), None)
#                        d.addCallbacks(self.handleResponse, self.handleError)
        except AttributeError:
            pass

    def run(self, execution, page, validator, response):
        self.execution = execution
        self.page = page
        self.validator = validator

        if response.status >= 400:
            errors_json = { "page": response.url, "errors": [] }
            errors_json['errors'].append({ "error": response.status })

            result = Result(description=errors_json, execution=self.execution, page=self.page, validator=self.validator)
            result.save()

"""
	Images Validator. Check width, height and size
"""
class ImagesValidator(ValidatorBase):
    checked_urls = {}

    class CheckImage(Protocol):
        def __init__(self, finished, filesize, url):
            self.finished = finished
            self.remaining = filesize
            self.url = url

        def dataReceived(self, body):
            try:
#                log.msg("B0 " + str(self.remaining), level=log.INFO)
#                log.msg("B1 " + str(len(body)), level=log.INFO)
                file_like = cStringIO.StringIO(body)
                im = Image.open(file_like)
                height, width = im.size
                log.msg("I3 " + str(height) + " " + str(width) + " " + str(len(body)) + " " + str(self.remaining) + " " + self.url, level=log.INFO)

            except Exception as e:
#                log.msg("E0 " + self.url + " " + str(e), level=log.INFO)
                pass

        def connectionLost(self, reason):
            pass
#            log.msg("E1 " + reason.getErrorMessage(), level=log.INFO)

    def __init__(self, response):
        self.response = response
        self.checked_urls[response.url] = True

    def handleResponse(self, response, url):
        finished = Deferred()
        response.deliverBody(self.CheckImage(finished, response.length, url))
        return finished

    def handleError(self, reason, url):
        pass

    def run(self, execution, page, validator):
        self.execution = execution
        self.page = page
        self.validator = validator

        try:
            sel = Selector(self.response)

            for url in sel.xpath('//img/@src').extract():
                if url.startswith('/'):
                    url = "http://" + page.website.domain + url

                if url not in self.checked_urls:
                    self.checked_urls[url] = True

                    agent = Agent(reactor)
                    d = agent.request('GET', str(url), Headers({'User-Agent': [webquality.settings.SCRAPY_USER_AGENT]}), None)
                    d.addCallback(self.handleResponse, url)
                    d.addErrback(self.handleError, url)

        except AttributeError:
            pass

