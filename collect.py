import sys
from scrapy.crawler import CrawlerProcess
import base64
import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime , ForeignKey
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import desc
from scrapy import Spider
from scrapy.selector import Selector
from scrapy.crawler import CrawlerProcess
from config import SQLALCHEMY_DATABASE_URI

Base = declarative_base()
engine = create_engine(SQLALCHEMY_DATABASE_URI)
Session = sessionmaker(bind=engine)

class SpiderDB(Base):
	__tablename__ = 'spiders'

	id = Column(Integer,primary_key=True)
	user_id = Column(Integer,ForeignKey("users.id"))
	name = Column(String)
	spider_type = Column(Integer)

class SpiderUrl(Base):
	__tablename__ = 'spider_url'

	id = Column(Integer,primary_key=True)
	spider_id = Column(Integer)
	url = Column(String)

class SpiderSelector(Base):
	__tablename__ = 'spider_selector'

	id = Column(Integer,primary_key=True)
	spider_id = Column(Integer)
	selector = Column(String)

class SpiderResult(Base):
	__tablename__ = 'spider_result'

	id = Column(Integer,primary_key=True)
	spider_id = Column(Integer)
	timestamp = Column(DateTime)
	result = Column(String)

def DifferenceCrawlerSave(self,data):
    encoded = []
    for piece in data:
        encoded.append(str(base64.b64encode(piece.encode("utf-8")),"utf-8"))
    result = ",".join(encoded)
    session = Session()
    last = session.query(SpiderResult).filter(SpiderResult.spider_id == self.id).order_by(desc(SpiderResult.timestamp)).first()
    if (last != None) and last.result == result:
        last.timestamp = datetime.datetime.now()
        session.commit()
        return
    entry = SpiderResult(spider_id=self.id,timestamp=datetime.datetime.now(),result=result)
    session.add(entry)
    session.commit()

class DifferenceSpider(Spider):
    
    def parse(self, response):
        data = []
        for pair in self.pairs:
            data.append(response.xpath(pair).get())
        self.afterCrawl(data)

def NormalCrawlerSave(self,data):
    encoded = []
    for piece in data:
        encoded.append(str(base64.b64encode(piece.encode("utf-8")),"utf-8"))
    result = ",".join(encoded)
    session = Session()
    entry = SpiderResult(spider_id=self.id,timestamp=datetime.datetime.now(),result=result)
    session.add(entry)
    session.commit()

def getCrawlerInfo(id):
    session = Session()
    pairs = []
    urls = [] 

    result = session.query(SpiderSelector).filter(SpiderSelector.spider_id == id)
    for i in range(result.count()):
        pairs.append(result[i].selector)

    url = session.query(SpiderUrl).filter(SpiderUrl.spider_id == id)
    for i in range(url.count()):
        urls.append(url[i].url)

    return pairs,urls

def loadSpider(id):
    pairs, urls = getCrawlerInfo(id)
    session = Session()
    dbspider = session.query(SpiderDB).filter(SpiderDB.id == id).first()

    types = {1:NormalCrawlerSave,2:DifferenceCrawlerSave}

    spider = DifferenceSpider
    spider.name = dbspider.name
    spider.id = id
    spider.pairs = pairs
    spider.start_urls = urls
    spider.afterCrawl = types[dbspider.spider_type]

    return spider

spider = loadSpider(sys.argv[1])

process = CrawlerProcess({
    'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
})
process.crawl(spider)
process.start()