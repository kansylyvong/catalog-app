import time
from functools import update_wrapper
from flask import request, g
from flask import Flask, jsonify 
from models import Base, Category, Author, Book 


from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine

import json

engine = create_engine('sqlite:///cookBook.db')

Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
app = Flask(__name__)

def getAuthorId(first, last):
    pass

def addCookBook(title, authorFirstName, authorLastName, description, category, image_url):
    session = DBSession()
    author = session.query(Author).filter_by(first_name = authorFirstName, last_name = authorLastName).all()
    category = session.query(Category).filter_by(name = category)
    #check to see if the author and category exists first anf if they do not add them
    if author == []:
        author = Author(first_name = authorFirstName, last_name = authorLastName)
        session.add(author)
        session.commit()
    if category == []:
        category = Category(name = category)
        session.add(category)
        session.commit()
    cookBook = Book(title = title, description = description, category_id = category.id, author_id = author.id, image_url = image_url)
    session.add(cookBook)

def getAllCookBooks():
    session = DBSession()
    books = session.query(Books).all()

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
    for cat in categories:
        print cat.name

addCookBook("Six Seasons", "Jeremy", "McFadden", "A really great cookbook!", "new american", "https://www.example.com")

app = Flask(__name__)

if __name__ == '__main__':
    app.debug = True
    app.run(host = '0.0.0.0', port = 8234)
