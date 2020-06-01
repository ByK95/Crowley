from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime , ForeignKey
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

Base = declarative_base()
engine = create_engine('sqlite:///data.db', echo=True)
Session = sessionmaker(bind=engine)

class User(Base):
	__tablename__ = 'users'

	id = Column(Integer,primary_key=True)
	username = Column(String, unique=True)
	emailAddress = Column(String, unique=True)
	passwordSalt = Column(String)
	passwordHash = Column(String)

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

Base.metadata.create_all(engine)