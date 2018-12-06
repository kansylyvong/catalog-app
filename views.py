import time
from functools import update_wrapper
from flask import request, g
from flask import Flask, jsonify, render_template, redirect, url_for 
from models import Base, Category, Author, Book 


from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine 
from sqlalchemy.orm.exc import  NoResultFound 
from sqlalchemy.exc import DBAPIError, SQLAlchemyError

import json

engine = create_engine('sqlite:///cookBook.db')

Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
app = Flask(__name__)

def getAuthorId(first, last):
    pass

@app.route('/addcookbook/', methods=['GET', 'POST'])
def addCookBook():
    session = DBSession()
    if request.method == 'POST':
        title = request.form['title']
        authorFirstName = request.form['authorFirstName']
        authorLastName = request.form['authorLastName']
        description = request.form['description']
        book_category = request.form['book_category']
        image_url = request.form['image_url']
        try:
            author = session.query(Author).filter_by(first_name = authorFirstName, last_name = authorLastName).one()
        except (SQLAlchemyError, DBAPIError) as e:
            author = Author(first_name = authorFirstName, last_name = authorLastName)
            session.add(author)
            session.commit()
            author = session.query(Author).filter_by(first_name = authorFirstName, last_name = authorLastName).one()
        try:
            cat = session.query(Category).filter_by(name = book_category).one()
        except (SQLAlchemyError, DBAPIError) as e:
            cat = Category(name = book_category)
            session.add(cat)
            session.commit()
            cat = session.query(Category).filter_by(name = book_category).one()
        cookBook = Book(title = title, description = description, category = cat.id, author_id = author.id, image_url = image_url)
        session.add(cookBook)
        session.commit()
        return redirect(url_for('getBooksByCat', cat_id = cookBook.category))
    else:
        return render_template('addcookbook.html')

@app.route('/deletebook/<int:book_id>/', methods=['GET', 'POST'])
def deleteCookBook(book_id):
    session = DBSession()
    bookToDelete = session.query(Book).filter_by(id = book_id).one()
    if request.method == 'POST':
        session.delete(bookToDelete)
        session.commit()
        return redirect(url_for('getBooksByCat', cat_id = bookToDelete.category))
    else:
        return render_template('deletebook.html', book = bookToDelete)

@app.route('/cookbook/edit/<int:book_id>/', methods=['GET', 'POST'])
def editCookBook(book_id):
    session = DBSession()
    bookToEdit = session.query(Book).filter_by(id = book_id).one()
    bookToEditAuthor = session.query(Author).filter_by(id = bookToEdit.author_id).first()
    categories = session.query(Category).all()
    categoryToEdit = session.query(Category).filter_by(id = bookToEdit.category).first()
    if request.method == 'POST':
        title = request.form['title']
        authorFirstName = request.form['authorFirstName']
        authorLastName = request.form['authorLastName']
        description = request.form['description']
        book_category = request.form['book_category']
        image_url = request.form['image_url']
        bookToEdit.title = title
        bookToEdit.description = description
        bookToEdit.image_url = image_url
        bookToEdit.category = book_category
        if bookToEditAuthor.first_name != authorFirstName or bookToEditAuthor.last_name != authorLastName:
            author = Author(first_name = authorFirstName, last_name = authorLastName)
            session.add(author)
            session.commit()
            auth = session.query(Author).filter_by(first_name = authorFirstName, last_name = authorLastName)
            bookToEdit.author_id = auth.id
        session.add(bookToEdit)
        session.commit()
        return redirect(url_for('getBooksByCat', cat_id = bookToEdit.category))
    else:
        return render_template('editcookbook.html', book = bookToEdit, author = bookToEditAuthor, category = categoryToEdit, categories = categories)

@app.route('/cookbooks/')
def getAllCookBooks():
    session = DBSession()
    books = session.query(Book, Author, Category).join(Author, Book.author_id == Author.id).join(Category, Category.id == Book.category).all()
    return render_template('cookbooks.html', books = books) 

@app.route('/categories/<int:cat_id>/')
def getBooksByCat(cat_id):
    session = DBSession()
    books = session.query(Book, Author, Category).join(Author, Book.author_id == Author.id).join(Category, Category.id == Book.category).filter(Book.category==cat_id).all()
    return render_template('cookbooks.html', books = books)

@app.route('/addcategory/')
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

@app.route('/')
@app.route('/categories/')
def getCategories():
    session = DBSession()
    categories = session.query(Category).all()
    return render_template('categories.html', categories = categories)

if __name__ == '__main__':
    app.debug = True
    app.run(host = '0.0.0.0', port = 8234)
