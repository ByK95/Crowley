import sys
from helper import loadSpider
from scrapy.crawler import CrawlerProcess

print(sys.argv[1])

spider = loadSpider(sys.argv[1])

process = CrawlerProcess({
    'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
})
process.crawl(spider)
process.start()