# -*- coding: utf-8 -*-
from datetime import datetime
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy import log, signals
from scrapy.xlib.pydispatch import dispatcher
import crawler.validators.validator

import sys, os
sys.path.append('/home/hector/develop/webquality')
os.environ['DJANGO_SETTINGS_MODULE'] ='webquality.settings'
from admin_wq.models import Execution, Page, Result, Validator, Website

import webquality.settings

class WebQualitySpider(CrawlSpider):
    name = "WebQualitySpider"
    allow_domains = None
    website = None
    validators = {}
    execution = None
    pages = {}
    errors = {}
    download_delay = webquality.settings.SCRAPY_DOWNLOAD_DELAY
    user_agent = webquality.settings.SCRAPY_USER_AGENT
    handle_httpstatus_list = [400, 401, 402, 403, 404, 405]

    def __init__(self, *args, **kwargs):
        super(WebQualitySpider, self).__init__(*args, **kwargs)
        self.user = kwargs.get('user')
        self.website = kwargs.get('website')
        self.validators = kwargs.get('validators')
        self.parameters = kwargs.get('parameters')
        self.start_urls = [self.website.start_url]
        self.allow_domains = [self.website.domain]
        self.execution = Execution(user=self.user, website=self.website, parameters=self.parameters)
        self.execution.save()
        self.execution.validators = self.validators.values()
        dispatcher.connect(self.spider_closed, signals.spider_closed)

        for r in self.rules:
            if r.follow:
                r.link_extractor.allow_domains.add(str(self.website.domain))

    # NO USAR allowed_domains
    rules = (
        Rule(SgmlLinkExtractor(allow_domains=(), tags=('a', 'area', 'img'), attrs=('href', 'src'), unique=True), follow=True),
        Rule(SgmlLinkExtractor(allow_domains=None, tags=('a', 'area', 'img'), attrs=('href', 'src'), unique=True), follow=False),
    )

    def spider_closed(self, spider):
        self.execution.end_date = datetime.now()
        self.execution.save()

