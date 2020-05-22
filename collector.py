from scrapy import Spider
from scrapy.selector import Selector
from scrapy.crawler import CrawlerProcess
from database import TimerLog, Session

class DifferenceSpider(Spider):
    
    def parse(self, response):
        data = []
        for pair in self.pairs:
            data.append(response.xpath(pair).get())
        self.afterCrawl(data)

def create_spider():
    session = Session()
    entry = Spider(name="test")
    session.add(entry)
    url = SpiderUrl(spider_id = 1,url="http://yyegm.meb.gov.tr/www/Duyurular/kategori/2")
    session.add(url)
    entry2 = SpiderSelector(spider_id=1,selector='//tr//h4/text()')
    session.add(entry2)
    entry3 = SpiderSelector(spider_id=1,selector='//tr//td[1]//a/@href')
    session.add(entry3)
    entry4 = SpiderSelector(spider_id=1,selector='//tr//td[3]/text()')
    session.add(entry4)
    session.commit()
    