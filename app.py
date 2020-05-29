from flask import Flask , render_template , send_from_directory , request , jsonify , redirect , session
from flask_session import Session as sess
from tempfile import mkdtemp
from database import TimerLog, Session, SpiderDB , SpiderUrl, SpiderSelector , User
from helper import getSpiders , loadSpider , getLastSpiderResult , getCrawlerInfo , login_required
from helper import checkSpiderOwnership
from werkzeug.security import check_password_hash, generate_password_hash
import subprocess
from sqlalchemy import desc

import datetime

app = Flask(__name__, static_url_path='')
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
sess(app)


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
@login_required
def activity():
    title = "Timer Activity Table"
    data = []
    headers = ['Time','Interval']

    dbSess = Session()
    result = dbSess.query(TimerLog).order_by(desc(TimerLog.date))[0:15]
    for val in result:
        data.append([val.date.strftime("%H:%M:%S %d/%m/%Y"),val.interval])

    user = session.get("user_id")
    return render_template("table.html",headers=headers,data=data,tableTitle=title,user=user)

@app.route('/code')
def code():
    title = "Search Snippets"
    return render_template("code.html",tableTitle=title)

@app.route('/collect')
@login_required
def collect():
    title = "Collect Data From Web"
    return render_template("collect.html",tableTitle=title,spiders=getSpiders())

@app.route('/listcrawlers')
@login_required
def listcrawlers():
    title = "Collection of Spiders"
    data = []
    headers = ['Name']

    dbSess = Session()
    result = dbSess.query(SpiderDB)[0:15]
    for val in result:
        data.append([val.name])

    user = session.get("user_id")
    return render_template("table.html",tableTitle=title,data=data,headers=headers,user=user)

@app.route('/crawler/<int:id>', methods=['GET','POST'])
@login_required
def crawler_edit(id):
    user = session.get("user_id")
    if request.method == 'POST':
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

        dbSess = Session()
        spider_result = dbSess.query(SpiderDB).filter(SpiderDB.id == id).first()
        if (spider_result is None) or spider_result.user_id != user:
            return "ERR"

        dbSess.query(SpiderUrl).filter(SpiderUrl.spider_id == id).delete()
        dbSess.query(SpiderSelector).filter(SpiderSelector.spider_id == id).delete()
        for url in urls:
            dbSess.add(SpiderUrl(spider_id=id, url=url))
            
        for selector in selectors:
            dbSess.add(SpiderSelector(spider_id=id, selector=selector))

        dbSess.commit()
    
    
    pairs , urls = getCrawlerInfo(id)
    return render_template("crawler.html",tableTitle="Crawler Name",pairs=pairs,urls=urls,id=id,user=user)

@app.route('/api/log/timer' , methods=['POST'])
@login_required
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
@login_required
def run_spider(id):
    if checkSpiderOwnership(session.get("user_id"),id):
        subprocess.Popen(["python","collect.py",str(id)])
        return "OK"
    return "Permission Denied!"

@app.route('/api/getlast/<int:id>' , methods=['POST'])
@login_required
def get_last(id):
    last_result = getLastSpiderResult(id)
    if last_result != None:
        return last_result.result
    return "err"

@app.route('/api/addspider' , methods=['POST'])
@login_required
def add_spider():
    user = session.get("user_id")
    print(user)
    dbSess = Session()
    entry = SpiderDB(name = 'New Spider',user_id=user)
    dbSess.add(entry)
    dbSess.commit()
    dbSess.add(SpiderUrl(spider_id=entry.id, url="Url"))
    dbSess.add(SpiderSelector(spider_id=entry.id, selector="Selector"))
    dbSess.commit()
    return jsonify({'res':entry.id})

@app.route('/api/delspider/<int:id>' , methods=['POST'])
@login_required
def del_spider(id):
    session = Session()
    session.query(SpiderDB).filter(SpiderDB.id == id).delete()
    session.query(SpiderUrl).filter(SpiderUrl.spider_id == id).delete()
    session.query(SpiderSelector).filter(SpiderSelector.spider_id == id).delete()
    session.commit()
    return jsonify({'res':entry.id})

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    session.clear()

    if request.method == "POST":

        if not request.form.get("username"):
            return "ERR"

        elif not request.form.get("password"):
            return "ERR"

        dBsess = Session()

        query = dBsess.query(User).filter(User.username == request.form.get("username"))

        if query.count() != 1:
            return "ERR"
        
        if not check_password_hash(query[0].passwordHash, request.form.get("password")):
            return "ERR"

        session["user_id"] = query[0].id

        return redirect("/")

    else:
        return render_template("login.html")
    
@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")