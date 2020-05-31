from database import *
from collector import *
from sqlalchemy import desc
from functools import wraps
from flask import session , redirect
import datetime
import base64

def getSpiders(id):
    data = []
    session = Session()
    result = session.query(SpiderDB).filter(SpiderDB.user_id == id)[0:15]
    for val in result:
        data.append(val)
    return data

def save(self,data):
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

def decode(text):
    vals = text.split(',')
    return list(map( lambda a : str(base64.b64decode(a),"utf-8"),vals))

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

def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def checkSpiderOwnership(user,id):
    dbSess = Session()
    spider_result = dbSess.query(SpiderDB).filter(SpiderDB.id == id).first()
    if (spider_result is None) or spider_result.user_id != user:
        return False
    return True