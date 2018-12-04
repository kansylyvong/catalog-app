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

def addCookBook(title, authorFirstName, authorLastName, description, book_category, image_url):
    session = DBSession()
    author = session.query(Author).filter_by(first_name = authorFirstName, last_name = authorLastName).all()
    cat = session.query(Category).filter_by(name = book_category).all()
    #check to see if the author and category exists first anf if they do not add them
    print(author)
    print(cat)
    if author == []:
        author = Author(first_name = authorFirstName, last_name = authorLastName)
        session.add(author)
        session.commit()
        author = session.query(Author).filter_by(first_name = authorFirstName, last_name = authorLastName).one()
    if cat == []:
        cat = Category(name = book_category)
        session.add(cat)
        session.commit()
        cat = session.query(Category).filter_by(name = book_category)

    cookBook = Book(title = title, description = description, category = cat[0].id, author_id = author[0].id, image_url = image_url)
    session.add(cookBook)
    session.commit()

def getAllCookBooks():
    session = DBSession()
    books = session.query(Book, Author, Category).join(Author, Book.author_id == Author.id).join(Category, Category.id == Book.category).all()
    for book, author, category in books:
        print("{} by {} {} category {}".format(book.title, author.first_name, author.last_name, category.name))

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

getAllCookBooks()

app = Flask(__name__)

if __name__ == '__main__':
    app.debug = True
    app.run(host = '0.0.0.0', port = 8234)
