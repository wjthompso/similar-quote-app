from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import requests
import random
from quotes import *

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app_database.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False # This silenced annoying warnings

db = SQLAlchemy(app)

#This will be the database of all total quotes
class Quote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quote_id = db.Column(db.String(70), nullable=False)
    author = db.Column(db.String(70), nullable=False)
    quote = db.Column(db.String(500), nullable=False) #No empty tasks
    user_rating = db.Column(db.Integer, nullable=True)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    tags = db.Column(db.String(500), nullable=False)

    def __repr__(self):
        return '<Quote %r>' % self.id

#This will be the database of the user's quote history
class QuoteHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quote_id = db.Column(db.String(70), nullable=False)
    author = db.Column(db.String(70), nullable=False)
    quote = db.Column(db.String(500), nullable=False) #No empty tasks
    user_rating = db.Column(db.Integer, nullable=True)
    time_of_rating = db.Column(db.DateTime, default=datetime.utcnow)
    tags = db.Column(db.String(500), nullable=False)

    def __repr__(self):
        return '<Quote %r>' % self.id

def add_all_quotes_to_db():
    #If the database is empty, perform the API calls and enter the data into our database
    if Quote.query.count() == 0:
        all_quotes = get_all_quotes()
        for quote in all_quotes:
            new_quote = Quote(
                quote_id = quote["_id"],
                author = quote["author"],
                quote = quote["content"],
                user_rating = None,
                tags = ", ".join(quote["tags"])
                )
            db.session.add(new_quote)
            db.session.commit()
    else:
        pass

@app.route("/", methods=['POST', 'GET'])
def front_page_quote():
    if request.method == "POST":
        random_int = random.randint(1,95)
        random_quote_data = Quote.query.get(random.randint(1,95))
        return render_template('index.html', random_quote_data=random_quote_data)

    else:

        random_quote_data = Quote.query.get(random.randint(1,95))
        print(random_quote_data)

        return render_template('index.html', random_quote_data=random_quote_data)

@app.route('/recommended_quote/<id>/<rating>/', methods=['GET', 'POST'])
def recommended_quote(id, rating):
    if request.method == 'POST':
        return redirect('/')
    else:
        # try:
        # We query the user selected quote and convert it to dictionaries to be used by jinja
        user_selected_quote = Quote.query.filter_by(quote_id = id).first().__dict__
        all_quotes = [dict(Quote.__dict__) for Quote in Quote.query.all()] 
        similar_quote = find_similar_quote(user_selected_quote, all_quotes)     

        user_quote_history_entry = QuoteHistory(
                                    quote_id = user_selected_quote['quote_id'],
                                    author = user_selected_quote['author'],
                                    quote = user_selected_quote['quote'], #No empty tasks
                                    user_rating = rating,
                                    time_of_rating = datetime.utcnow(),
                                    tags = user_selected_quote['tags']
                                    )
        db.session.add(user_quote_history_entry)
        db.session.commit()

        # get_time_of_rating = datetime.strftime(user_quote_history_entry.time_of_rating, "%Y"
        print("\n\nThis is what the user_quote_history_entry.time_of_rating object looks like")
        print(user_quote_history_entry.time_of_rating)
        print("\n")

        # time_of_rating = datetime.strptime(user_quote_history_entry.time_of_rating, '%Y-%m-%d %H:%M:%S.%f').strftime("%I:%M %p (UTC)")
        time_of_rating = user_quote_history_entry.time_of_rating.strftime("%I:%M %p (UTC)")


        all_user_selected_quotes = [user_history.__dict__ for user_history in QuoteHistory.query.all()]

        return render_template('recommended_quote.html', user_selected_quote = user_selected_quote,
                                                        user_rating = rating,
                                                        time_of_rating = time_of_rating,
                                                        similar_quote = similar_quote,
                                                        all_user_selected_quotes = all_user_selected_quotes)
        # except Exception as e:
        #     print("There was an issue")
        #     print(e)


if __name__ == '__main__':
    add_all_quotes_to_db()
    print(f"\nHere is the count of the database! {Quote.query.count()} \n")
    app.run(host="localhost", port=8002, debug=True)