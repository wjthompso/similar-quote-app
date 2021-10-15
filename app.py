from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import requests

from get_all_quotes import *

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'

db = SQLAlchemy(app)

class Quote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(70), nullable=False)
    quote = db.Column(db.String(500), nullable=False) #No empty tasks
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Quote %r>' % self.id

class QuoteHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quote = db.Column(db.String(500), nullable=False) #No empty tasks
    author = db.Column(db.String(500), nullable=False) #No empty authors
    date_liked = db.Column(db.DateTime, default=datetime.utcnow)
    rating = db.Column(db.Integer, primary_key=True)

    def __repr__(self):
        return '<QuoteHistory %r>' % self.id

@app.route("/")
def front_page_quote():
    quote_data = requests.get("https://api.quotable.io/random").json()
    
    return render_template('index.html', all_quotes=all_quotes)


if __name__ == '__main__':
    app.run(host="localhost", port=8000, debug=True)