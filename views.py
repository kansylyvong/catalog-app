import time
from functools import update_wrapper
from flask import request, g
from flask import Flask, jsonify 
from models import Base, Item


from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine

import json

engine = create_engine('sqlite:///bargainMart.db')

Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
app = Flask(__name__)

def addCategory(name)
    session = DBSession()
    #check if category already exists
    category = session.query(Category).filter_by(nane=name)
    if category == []:
        category = Category(name=name)
        session.add(category)
        session.commit()
        print("Item added, here are all the categories so far")
        categories = session.query(category).all()
        print categories
    else:
        print("That category is already in the db!")

app = Flask(__name__)

if __name__ == '__main__':
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)
