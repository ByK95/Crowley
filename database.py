from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

Base = declarative_base()
engine = create_engine('sqlite:///data.db', echo=True)
Session = sessionmaker(bind=engine)

class TimerLog(Base):
	__tablename__ = 'timerstamps'

	id = Column(Integer,primary_key=True)
	interval = Column(String)
	date = Column(DateTime)

	def __repr__(self):
		return "<Timer Activity ('%s')>" % self.date

class SpiderDB(Base):
	__tablename__ = 'spiders'

	id = Column(Integer,primary_key=True)
	name = Column(String)

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