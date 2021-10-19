from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import random
from quotes import *

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app_database.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False # This silenced annoying warnings

db = SQLAlchemy(app)

def create_db_if_necessary():
    filenames = os.listdir()
    if "app_database.db" not in filenames:
        db.create_all()


#This will be the database of all total quotes
class Quote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quote_id = db.Column(db.String(70), nullable=False)
    author = db.Column(db.String(70), nullable=False)
    quote = db.Column(db.String(500), nullable=False) #No empty tasks
    user_rating = db.Column(db.Integer, nullable=True)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    tags = db.Column(db.String(500), nullable=False)
    quote_similarities = db.Column(db.JSON, nullable = False)

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

# This sentence similarity matrix was calculated using BERT (Bidirectional Encoder Representations from Transformers), state of the art NLP!
sentence_similarity_matrix = pd.read_csv("sentence_similarity_matrix.csv", index_col = "index")
all_quote_ids = list(sentence_similarity_matrix.columns)

def add_all_quotes_to_db(sentence_similarity_matrix):
    if Quote.query.count() == 0:
        all_quotes = get_all_quotes()
        for quote in all_quotes:
            quote_id = quote["_id"]
            new_quote = Quote(
                quote_id = quote_id,
                author = quote["author"],
                quote = quote["content"],
                user_rating = None,
                tags = ", ".join(quote["tags"]),
                quote_similarities = {quote_id: list(sentence_similarity_matrix[quote_id])},
                )
            db.session.add(new_quote)
            db.session.commit()
    else:
        return None

@app.route("/", methods=['POST', 'GET'])
def front_page_quote():
    if request.method == "POST":
        if Quote.query.count() != 0:
            db.session.query(QuoteHistory).delete()
            db.session.commit()

        random_quote_data = Quote.query.get(random.randint(1, Quote.query.count()))
        return render_template('index.html', random_quote_data=random_quote_data)

    else:
        if Quote.query.count() != 0:
            db.session.query(QuoteHistory).delete()
            db.session.commit()

        random_quote_data = Quote.query.get(random.randint(1, Quote.query.count()))

        return render_template('index.html', random_quote_data=random_quote_data)

@app.route('/recommended_quote/<id>/<different>/', methods=['GET', 'POST'])
def recommended_quote(id, different):
    try:
        rating = str(len(request.url.split("?submit_button=")[1]))
    except:
        rating = None
        pass
    if rating in ["1", "2", "3"] or request.method == 'POST':
        return redirect('/')
    else:
        try:
            # We query the user selected quote and convert it to dictionaries to be used by jinja
            user_selected_quote = Quote.query.filter_by(quote_id = id).first().__dict__
            
            if different == "False":
                different = False
            else:
                different = True
            
            # Get either a similar or different quote, given that the recommended quote is not already in the QuoteHistory
            recommended_quote = find_another_quote(user_selected_quote, all_quote_ids, different = different)

            user_quote_history_entry = QuoteHistory(
                                        quote_id = user_selected_quote['quote_id'],
                                        author = user_selected_quote['author'],
                                        quote = user_selected_quote['quote'], #No empty quotes
                                        user_rating = "No rating" if rating == "Norating" else rating,
                                        time_of_rating = datetime.utcnow(),
                                        tags = user_selected_quote['tags']
                                        )

            # Only add the user_quote_history_entry to the database if it isn't already in there
            if not QuoteHistory.query.filter_by(quote_id = id).first():
                db.session.add(user_quote_history_entry)
                db.session.commit()

            time_of_rating = user_quote_history_entry.time_of_rating.strftime("%I:%M %p (UTC)")

            all_user_selected_quotes = format_times([user_history.__dict__ for user_history in QuoteHistory.query.all()])

            return render_template('recommended_quote.html', user_selected_quote = user_selected_quote,
                                                            user_rating = "no rating" if rating == "norating" else rating,
                                                            time_of_rating = time_of_rating,
                                                            recommended_quote = recommended_quote,
                                                            sim_or_diff = "different" if different else "similar",
                                                            all_user_selected_quotes = all_user_selected_quotes
                                                            )
        except Exception as e:
            print("There was an issue")
            print(e)
            


if __name__ == '__main__':
    create_db_if_necessary()
    add_all_quotes_to_db(sentence_similarity_matrix)
    app.run(host="localhost", port=8000, debug=True)