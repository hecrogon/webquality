#!/usr/bin/python2.7
import os
from twisted.internet import reactor
from scrapy.crawler import Crawler
from scrapy import log
from crawler.spiders.spider import WebQualitySpider
from scrapy.utils.project import get_project_settings

os.environ['DJANGO_SETTINGS_MODULE'] = 'webquality.settings'
from django.contrib.auth.models import User
from wqinterfaz.models import Execution, Result, Website, Validator
os.environ['SCRAPY_SETTINGS_MODULE'] = 'crawler.settings'

def setup_crawler(user, website, validator_set, parameters):
    spider = WebQualitySpider(user=user, website=website, validators=validator_set, parameters=parameters)
    settings = get_project_settings()
    crawler = Crawler(settings)
    crawler.configure()
    crawler.crawl(spider)
    crawler.start()

user = User.objects.get(username='hector')
validator_set = {}
validators = Validator.objects.filter(classname='DownloadTimeValidator')
for validator in validators:
    validator_set[validator.classname] = validator
#websites = Website.objects.filter(name='Web ULL local')
websites = Website.objects.filter(name='Shidix')
parameters = {u'DownloadTimeValidator': {'fields': {u'time': u'10.0'}}}

log.start(logfile="log.txt", loglevel=log.INFO)

for website in websites:
    setup_crawler(user, website, validator_set, parameters)

settings = get_project_settings()
log.msg("Init " + str(settings['BOT_NAME']), level=log.INFO)

reactor.run()

