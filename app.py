from flask import Flask , render_template , send_from_directory , request , jsonify , redirect , session
from flask_session import Session as sess
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
import subprocess
from sqlalchemy import desc,exc
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
import datetime
from helper import login_required
import base64

app = Flask(__name__, static_url_path='')
app.config.from_object('dev_config')
sess(app)
db = SQLAlchemy(app)
from database import SpiderDB , SpiderUrl, SpiderSelector , UserModel , SpiderResult

def getSpiders(id):
    data = []
    result = SpiderDB.query.filter_by(user_id = id)[0:15]
    for val in result:
        data.append(val)
    return data

def checkSpiderOwnership(user,id):
    spider_result = SpiderDB.query.filter_by(id = id).first()
    if (spider_result is None) or spider_result.user_id != user:
        return False
    return True

def getCrawlerInfo(id):
    pairs = []
    urls = [] 

    result = SpiderSelector.query.filter_by(spider_id = id)
    for i in range(result.count()):
        pairs.append(result[i].selector)

    url = SpiderUrl.query.filter_by(spider_id = id)
    for i in range(url.count()):
        urls.append(url[i].url)

    return pairs,urls

def getLastSpiderResult(id):
    return SpiderResult.query.filter_by(spider_id = id).order_by(desc(SpiderResult.timestamp)).first()

def decode(text):
    vals = text.split(',')
    return list(map( lambda a : str(base64.b64decode(a),"utf-8"),vals))

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
    return render_template("collect.html",tableTitle=title,spiders=getSpiders(user),user=user)

@app.route('/crawler/<int:id>', methods=['GET','POST'])
@login_required
def crawler_edit(id):
    user = session.get("user_id")

    if not checkSpiderOwnership(user,id):
        return render_template("error.html",errTitle='Permission Denied!', redir="/collect")

    spider = SpiderDB.query.filter_by(id = id).first()
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

        if request.form.get('name') != "":
            name = request.form.get('name')

        try:
            spider_type = int(request.form.get('crawlertype'))
        except ValueError:
            return render_template("error.html",errTitle='Whoops!', redir="/crawler/{}".format(id))

        if spider_type > 0 and spider_type < 3:
            spider.spider_type = spider_type
        
        spider.name = name
        SpiderUrl.query.filter_by(spider_id = id).delete()
        SpiderSelector.query.filter_by(spider_id = id).delete()
        for url in urls:
            db.session.add(SpiderUrl(spider_id=id, url=url))
            
        for selector in selectors:
            db.session.add(SpiderSelector(spider_id=id, selector=selector))

        db.session.commit()
        return redirect("/collect")
    
    
    pairs , urls = getCrawlerInfo(id)
    return render_template("crawler.html", spider = spider, pairs=pairs, urls=urls, id=id, user=user)

@app.route('/viewcollected/<int:id>', methods=['GET'])
@login_required
def crawled_data(id):
    user = session.get("user_id")
    if checkSpiderOwnership(user,id):
        results = SpiderResult.query.filter_by(spider_id = id).order_by(desc(SpiderResult.timestamp))[0:25]

        title = "Crawled Results"
        data = []
        headers = ['Time','Crawled Data']

        for val in results:
            data.append([val.timestamp.strftime("%H:%M %d/%m/%Y"),decode(val.result)])

        return render_template("table.html",tableTitle=title,data=data,headers=headers,user=user)
    return render_template("error.html",errTitle='Permission Denied!', redir="/viewcollected")


@app.route('/api/run/<int:id>' , methods=['POST'])
@login_required
def run_spider(id):
    if checkSpiderOwnership(session.get("user_id"),id):
        subprocess.Popen(["python","collect.py",str(id)])
        return "OK"
    return render_template("error.html",errTitle='Permission Denied!', redir="/collect")

@app.route('/api/crawlall' , methods=['POST'])
@login_required
def crawlall():
    spiders = SpiderDB.query.filter_by(user_id = session.get("user_id"))
    for spidey in spiders:
        subprocess.Popen(["python","collect.py",str(spidey.id)])
    return "OK"

@app.route('/api/getlast/<int:id>' , methods=['POST'])
@login_required
def get_last(id):
    if checkSpiderOwnership(session.get("user_id"),id):
        result = getLastSpiderResult(id)
        if result != None:
            return result.result
    return render_template("error.html",errTitle='Permission Denied!', redir="/collect")

@app.route('/api/addspider' , methods=['POST'])
@login_required
def add_spider():
    user = session.get("user_id")
    entry = SpiderDB(name = 'New Spider',user_id=user)
    db.session.add(entry)
    db.session.commit()
    db.session.add(SpiderUrl(spider_id=entry.id, url="Url"))
    db.session.add(SpiderSelector(spider_id=entry.id, selector="Selector"))
    db.session.commit()
    return jsonify({'res':entry.id})

@app.route('/api/delspider/<int:id>' , methods=['POST'])
@login_required
def del_spider(id):
    if checkSpiderOwnership(session.get("user_id"),id):
        SpiderDB.query.filter_by(id = id).delete()
        SpiderUrl.query.filter_by(spider_id = id).delete()
        SpiderSelector.query.filter_by(spider_id = id).delete()
        db.session.commit()
        return jsonify({'res':id})
    return render_template("error.html",errTitle='Permission Denied!', redir="/login")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    session.clear()

    if request.method == "POST":

        if not request.form.get("username"):
            return render_template("error.html",errTitle='Username is required!', redir="/login")

        elif not request.form.get("password"):
            return render_template("error.html",errTitle='Password is required!', redir="/login")


        query = UserModel.query.filter_by(username = request.form.get("username"))

        if query.count() != 1:
            return render_template("error.html",errTitle='User does not exists!')
        
        if not check_password_hash(query[0].passwordHash, request.form.get("password")):
            return render_template("error.html",errTitle='Wrong password!', redir="/login")

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

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":

        form = {"username":None,"email":None,"password":None}
        for i in form:
            if request.form.get(i) is None or request.form.get(i) == "":
                return "Must Provide {}".format(i)
            form[i] = request.form.get(i)

        passhash = generate_password_hash(request.form.get("password"))

        new_user = UserModel(username = form["username"], emailAddress = form["email"], passwordHash = passhash)
        
        try:
            db.session.add(new_user)
            db.session.commit()
        except exc.IntegrityError:
            return render_template("error.html",errTitle='User exists!',redir="/register")

        return redirect("/")
    else:
        return render_template("register.html")


if __name__ == "__main__":
    app.run()