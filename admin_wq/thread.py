from twisted.internet import reactor
from scrapy.crawler import Crawler
from scrapy.utils.project import get_project_settings
from scrapy.settings import Settings
from scrapy import log
from scrapy.xlib.pydispatch import dispatcher
from crawler.spiders.spider import WebQualitySpider

import os
os.environ['SCRAPY_SETTINGS_MODULE'] = 'crawler.settings'

def setup_crawler(user, website, validator_set, parameters):
    log.start(logfile="log.txt", loglevel=log.INFO)

    spider = WebQualitySpider(user=user, website=website, validators=validator_set, parameters=parameters)
    settings = get_project_settings()
    crawler = Crawler(settings)
    crawler.configure()
    crawler.crawl(spider)
    crawler.start()

    if reactor._started == False:
        reactor.run()
    else:
        reactor.callFromThread(WebQualitySpider)

def run_crawler(user, website, validator_set, parameters):
    setup_crawler(user, website, validator_set, parameters)

