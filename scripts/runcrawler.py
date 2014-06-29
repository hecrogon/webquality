#!/usr/bin/python2.7

from twisted.internet import reactor
from scrapy.crawler import Crawler
from scrapy.settings import Settings
from scrapy import log
from crawler.crawler.spiders.spider import WebQualitySpider

def setup_crawler(domain, validators):
	spider = WebQualitySpider(domain=domain, allowed_domains=domain, start_urls="http://" + domain, validators=validators)
	crawler = Crawler(Settings())
	crawler.configure()
	crawler.crawl(spider)
	crawler.start()

validators = ['BrokenLinksValidator']
#validators = ['W3CValidator', 'BrokenLinksValidator']

for domain in ['www.shidix.com']:
	setup_crawler(domain, validators)

log.start(logfile="log.txt", loglevel=log.INFO)
reactor.run()

