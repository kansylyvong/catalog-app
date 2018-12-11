import time
from functools import update_wrapper
from flask import request, g
from flask import session as login_session
import random
import string
from flask import Flask, jsonify, render_template, redirect, url_for, make_response, flash
from models import Base, Category, Author, Book, User
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2

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

@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                for c in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)

@app.route('/getcoobook/<int:id>/json')
def getCookBook(id):
    session = DBSession()
    book = session.query(Book).filter_by(id = id).first()
    return jsonify(Book=book.serialize)

@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print "access token received %s" % access_token

    app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
            'web']['app_id']
    app_secret = json.loads(
            open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (
                     app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    user_info_url = "https://graph.facebook.com/v2.8/me"

    token = result.split(',')[0].split(':')[1].replace('"','')
    url = 'https://graph.facebook.com/v2.8/me?access_token=%s&fields=name,id,email' % token
    result = h.request(url, 'GET')[1]
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data['email']
    login_session['email'] = data['email']
    login_session['facebook_id'] = data['id']
    login_session['access_token'] = token
    #get pic
    url = 'https://graph.facebook.com/v2.8/me/picture?access_token=%s&redirect=0&height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)
    login_session['picture'] = data["data"]["url"]

    user_id = getUserId(login_session['email'])
    print(user_id)
    if user_id is None:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("Now logged in as %s" % login_session['username'])
    return output

@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (facebook_id,access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "you have been logged out"

@app.route('/addcookbook/', methods=['GET', 'POST'])
def addCookBook():
    session = DBSession()
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        title = request.form['title']
        authorFirstName = request.form['authorFirstName']
        authorLastName = request.form['authorLastName']
        description = request.form['description']
        book_category = request.form['book_category']
        image_url = request.form['image_url']
        user_id = login_session['user_id']
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
        cookBook = Book(title = title, description = description, category = cat.id, author_id = author.id, image_url = image_url, user_id=user_id)
        session.add(cookBook)
        session.commit()
        return redirect(url_for('getBooksByCat', cat_id = cookBook.category))
    else:
        return render_template('addcookbook.html')

@app.route('/deletebook/<int:book_id>/', methods=['GET', 'POST'])
def deleteCookBook(book_id):
    session = DBSession()
    if 'username' not in login_session:
        return redirect('/login')
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
    if 'username' not in login_session:
        return redirect('/login')
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

def createUser(login_session):
    session = DBSession()
    newUser = User(name = login_session['username'], email = login_session['email'], picture = login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email = login_session['email']).one()
    return user.id

def getUserInfo(user_id):
    user = session.query(User).filter_by(id = user_id).one()
    return user

def getUserId(email):
    session = DBSession()
    try:
        user = session.query(User).filter_by(email = email).one()
        return user.id
    except:
        return None

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host = '0.0.0.0', port = 8234)
