import time
from functools import update_wrapper
from flask import request, g
from flask import Flask, jsonify 
from models import Base, Category 


from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine

import json

engine = create_engine('sqlite:///cookBook.db')

Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
app = Flask(__name__)

def addCategory(name):
    session = DBSession()
    #check if category already exists
    category = session.query(Category).filter_by(name=name).all()
    if category == []:
        category = Category(name=name)
        session.add(category)
        session.commit()
        print("Item added, here are all the categories so far")
        categories = session.query(Category).all()
        for cat in categories:
            print(cat)
    else:
        print("That category is already in the db!")
        for cat in category:
            print(cat)

def getCategories():
    session = DBSession()
    categories = session.query(Category).all()
    print(categories)

addCategory('Georgian')

app = Flask(__name__)

if __name__ == '__main__':
    app.debug = True
    app.run(host = '0.0.0.0', port = 8234)
