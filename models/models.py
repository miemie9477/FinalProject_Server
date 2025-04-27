#models.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import Unicode, Numeric, Integer, DateTime, Float

db = SQLAlchemy()

class Product(db.Model):
    pId = db.Column(Unicode(8), primary_key=True)
    pName = db.Column(Unicode(50))
    brand = db.Column(Unicode(30))
    category = db.Column(Unicode(20))
    price = db.Column(Numeric(10, 2))
    clickTimes = db.Column(Integer)
    review = db.Column(Float)

class PriceHistory(db.Model):
    pId = db.Column(Unicode(8), primary_key=True)
    prePrice = db.Column(Numeric(10, 2))
    updateTime = db.Column(DateTime, default=datetime.utcnow)
    storeName = db.Column(Unicode (50))

class PriceNow(db.Model):
    pId = db.Column(Unicode(8), primary_key=True)
    updateTime = db.Column(DateTime, default=datetime.utcnow, primary_key=True)
    store = db.Column(Unicode(50))
    storePrice = db.Column(Numeric(10, 2))
    storeDiscount = db.Column(Unicode(200))
    storeLink = db.Column(Unicode(200))

class Client(db.Model):
    cId = db.Column(Unicode(8), primary_key=True)
    cName = db.Column(Unicode(30))
    account = db.Column(Unicode(20), unique=True)
    password = db.Column(Unicode(14))
    email = db.Column(Unicode(64), unique=True)
    phone = db.Column(Unicode(10), unique=True)
    sex = db.Column(Unicode(14))
    birthday = db.Column(DateTime)

class ClientFavorites(db.Model):
    cId = db.Column(Unicode(8), primary_key=True)
    pId = db.Column(Unicode(8), primary_key=True)

class GoodReview(db.Model):
    pId = db.Column(Unicode(8), primary_key=True)
    date = db.Column(DateTime, default=datetime.utcnow, primary_key=True)
    userName = db.Column(Unicode(30))
    rating = db.Column(Float)
    reviewText = db.Column(Unicode)