from flask import Flask , render_template , send_from_directory , request , jsonify , redirect , session
from flask_session import Session as sess
from tempfile import mkdtemp
from database import Session, SpiderDB , SpiderUrl, SpiderSelector , User , SpiderResult
from helper import getSpiders , loadSpider , getLastSpiderResult , getCrawlerInfo , login_required
from helper import checkSpiderOwnership , decode
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
@login_required
def hello_world():
    return redirect("/collect")


@app.route('/collect')
@login_required
def collect():
    user = session.get("user_id")
    title = "Collect Data From Web"
    return render_template("collect.html",tableTitle=title,spiders=getSpiders(),user=user)

@app.route('/crawler/<int:id>', methods=['GET','POST'])
@login_required
def crawler_edit(id):
    user = session.get("user_id")
    dbSess = Session()
    spider = dbSess.query(SpiderDB).filter(SpiderDB.id == id).first()
    name = None or spider.name
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

        if not checkSpiderOwnership(user,id):
            return "ERR"

        if request.form.get('name') != "":
            name = request.form.get('name')
        
        spider.name = name
        dbSess.query(SpiderUrl).filter(SpiderUrl.spider_id == id).delete()
        dbSess.query(SpiderSelector).filter(SpiderSelector.spider_id == id).delete()
        for url in urls:
            dbSess.add(SpiderUrl(spider_id=id, url=url))
            
        for selector in selectors:
            dbSess.add(SpiderSelector(spider_id=id, selector=selector))

        dbSess.commit()
        return redirect("/collect")
    
    
    pairs , urls = getCrawlerInfo(id)
    return render_template("crawler.html", name=name, pairs=pairs, urls=urls, id=id, user=user)

@app.route('/viewcollected/<int:id>', methods=['GET'])
@login_required
def crawled_data(id):
    user = session.get("user_id")
    if checkSpiderOwnership(user,id):
        dbSess = Session()
        results = dbSess.query(SpiderResult).filter(SpiderResult.spider_id == id).order_by(desc(SpiderResult.timestamp))[0:25]

        title = "Crawled Results"
        data = []
        headers = ['Time','Crawled Data']

        for val in results:
            data.append([val.timestamp.strftime("%H:%M %d/%m/%Y"),decode(val.result)])

        return render_template("table.html",tableTitle=title,data=data,headers=headers,user=user)
    return "Permission Denied"


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
    if checkSpiderOwnership(session.get("user_id"),id):
        result = getLastSpiderResult(id)
        if result != None:
            return result.result
    return "err"

@app.route('/api/addspider' , methods=['POST'])
@login_required
def add_spider():
    user = session.get("user_id")
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
    return jsonify({'res':id})

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