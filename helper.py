from database import *
from collector import *
from sqlalchemy import desc
import datetime

session = Session()

def getSpiders():
    data = []
    session = Session()
    result = session.query(SpiderDB)[0:15]
    for val in result:
        data.append(val)
    return data

def save(self,data):
    if self.lastscrap != None:
        if self.lastscrap.result == data[0]:
            return
    print("value changed")
    session = Session()
    entry = SpiderResult(spider_id=self.id,timestamp=datetime.datetime.now(),result=data[0])
    session.add(entry)
    session.commit()

def getLastSpiderResult(id):
    session = Session()
    return session.query(SpiderResult).filter(SpiderResult.spider_id == id).order_by(desc(SpiderResult.timestamp)).first()

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

    lastscrap = getLastSpiderResult(id)

    spider = DifferenceSpider
    spider.name = "placeholder"
    spider.id = id
    spider.pairs = pairs
    spider.start_urls = urls
    spider.afterCrawl = save
    spider.lastscrap = lastscrap

    return spider

def addNotifChecked():
    session = Session()
    session.add(NotifChecked(date=datetime.datetime.now()))
    session.commit()

def notifCount(id):
    a = session.query(NotifChecked).filter(NotifChecked.id == id).first()
    date = a.date
    return session.query(NotifMessage).filter(NotifMessage.date > date).count()

def addNotifMessage(message,link):
    notif = NotifMessage(message = message, link = link, date = datetime.datetime.now())
    session.add(notif)
    session.commit()