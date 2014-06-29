# Scrapy settings for crawler project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#

BOT_NAME = 'websitequality_crawler'

SPIDER_MODULES = ['crawler.spiders']
NEWSPIDER_MODULE = 'crawler.spiders'

DOWNLOADER_MIDDLEWARES = {
#    'crawler.middlewares.ValidatorMiddleware': 10,
    'crawler.middlewares.PageMiddleware': 20,
    'crawler.middlewares.W3CValidatorMiddleware': 30,
    'crawler.middlewares.BrokenLinksMiddleware': 31,
    'crawler.middlewares.ImagesValidatorMiddleware': 32,
    'crawler.middlewares.SpellingMiddleware': 33,
    'crawler.middlewares.DownloadTimeMiddleware': 34,
}

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'crawler (+http://www.yourdomain.com)'
