from sqlalchemy import Column,Integer,String,ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
from passlib.apps import custom_app_context as pwd_context
import random, string
from itsdangerous import(TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))
    @property
    def serialize(self):
        return {
            'username': self.name,
            'email': self.email,
            'picture': self.picture
        }

class Author(Base):
    __tablename__ = 'author'
    id = Column(Integer, primary_key=True)
    first_name = Column(String(100))
    last_name = Column(String(100))
    @property
    def serialize(self):
        return {
            'author_first_name': self.first_name,
            'author_last_name': self.last_name
        }

class Category(Base):
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True)
    name = Column(String(500))
    
    @property
    def serialize(self):
        return {
            'name': self.name
        }

class Book(Base):
    __tablename__ = 'book'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    author_id = Column(Integer, ForeignKey("author.id"), nullable=False)
    description = Column(String(2500))
    category = Column(Integer, ForeignKey("category.id"), nullable=False)
    image_url = Column(String(500))
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)

    @property
    def serialize(self):
        return {
            'book_title': self.title,
            'author_id': self.author_id,
            'description': self.description,
            'category_id': self.category,
            'image_url': self.image_url,
            'user_id': self.user_id
        }
        
engine = create_engine('sqlite:///cookBook.db')

Base.metadata.create_all(engine)
