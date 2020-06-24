# -*- coding: utf-8 -*-
"""
Created on Sun Apr  5 20:15:58 2020

@author: Martin
"""

import sqlite3
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

con = sqlite3.connect("db.db")
engine = create_engine('sqlite:///db.db', convert_unicode=True)
metadata = MetaData(bind = engine)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

def init_db():
    import models
    Base.metadata.create_all(bind=engine)
    
def shut_engine():
    engine.dispose()    
