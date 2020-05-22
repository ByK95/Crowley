from flask import Flask , render_template , send_from_directory , request , jsonify
from database import TimerLog, Session, SpiderDB
from helper import getSpiders , loadSpider , getLastSpiderResult , getCrawlerInfo
import subprocess
from sqlalchemy import desc

import datetime

app = Flask(__name__, static_url_path='')

@app.route('/asset/<path:path>')
def send_asset(path):
    return send_from_directory('static', path)

@app.route('/')
def hello_world():
    return render_template("layout.html")

@app.route('/timer')
def countdown():
    return render_template("timer.html")

@app.route('/timeractivity')
def activity():
    title = "Timer Activity Table"
    data = []
    headers = ['Time','Interval']

    session = Session()
    result = session.query(TimerLog).order_by(desc(TimerLog.date))[0:15]
    for val in result:
        data.append([val.date.strftime("%H:%M:%S %d/%m/%Y"),val.interval])

    return render_template("table.html",headers=headers,data=data,tableTitle=title)

@app.route('/code')
def code():
    title = "Search Snippets"
    return render_template("code.html",tableTitle=title)

@app.route('/collect')
def collect():
    title = "Collect Data From Web"
    return render_template("collect.html",tableTitle=title,spiders=getSpiders())

@app.route('/listcrawlers')
def listcrawlers():
    title = "Collection of Spiders"
    data = []
    headers = ['Name']

    session = Session()
    result = session.query(SpiderDB)[0:15]
    for val in result:
        data.append([val.name])

    return render_template("table.html",tableTitle=title,data=data,headers=headers)

@app.route('/crawler/<int:id>')
def crawler_info(id):
    pairs , urls = getCrawlerInfo(id)
    return render_template("crawler.html",tableTitle="Crawler Name",pairs=pairs,urls=urls,id=id)

@app.route('/crawler/edit/<id>', methods=['POST'])
def crawler_edit(id):
    urls = []
    selectors = []

    index = 1
    while request.form.get('url{}'.format(index)) != None and index < 16:
        urls.append(request.form.get('url{}'.format(index)))
        index += 1

    index = 1
    while request.form.get('selector{}'.format(index)) != None and index < 16:
        selectors.append(request.form.get('selector{}'.format(index)))
        index += 1

    print(urls)
    print('')
    print(selectors)
    return 'OK'


@app.route('/api/log/timer' , methods=['POST'])
def log_timer_usage():
    if request.json:
        content = request.json
        print(content)
        if content['intr'] != None or content['intr'] != '':
            session = Session()
            entry = TimerLog(interval=content['intr'],date=datetime.datetime.now())
            session.add(entry)
            session.commit()
            return jsonify({'res':'success'})
    return jsonify({'res':'err'})


@app.route('/api/run/<int:id>' , methods=['POST'])
def run_spider(id):
    subprocess.Popen(["python","collect.py",str(id)])
    return "OK"

@app.route('/api/getlast/<int:id>' , methods=['POST'])
def get_last(id):
    return getLastSpiderResult(id).result