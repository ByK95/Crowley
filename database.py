from manage import db,app

class UserModel(db.Model):
	__tablename__ = 'users'

	id = db.Column(db.Integer,primary_key=True)
	username = db.Column(db.String, unique=True)
	emailAddress = db.Column(db.String, unique=True)
	passwordSalt = db.Column(db.String)
	passwordHash = db.Column(db.String)

class SpiderDB(db.Model):
	__tablename__ = 'spiders'

	id = db.Column(db.Integer,primary_key=True)
	user_id = db.Column(db.Integer)
	name = db.Column(db.String)
	spider_type = db.Column(db.Integer)

class SpiderUrl(db.Model):
	__tablename__ = 'spider_url'

	id = db.Column(db.Integer,primary_key=True)
	spider_id = db.Column(db.Integer)
	url = db.Column(db.String)

class SpiderSelector(db.Model):
	__tablename__ = 'spider_selector'

	id = db.Column(db.Integer,primary_key=True)
	spider_id = db.Column(db.Integer)
	selector = db.Column(db.String)

class SpiderResult(db.Model):
	__tablename__ = 'spider_result'

	id = db.Column(db.Integer,primary_key=True)
	spider_id = db.Column(db.Integer)
	timestamp = db.Column(db.DateTime)
	result = db.Column(db.String)

db.create_all()