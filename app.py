from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import asyncio
import aiohttp
import time
import json
import pandas as pd
import os
import random

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

def get_request_tasks(session):
    tasks = []
    for i in range(1, 96):
        url = "https://api.quotable.io/quotes?" + f"page={i}"
        tasks.append(session.get(url, ssl=False))
    return tasks

async def get_all_quote_responses():
    async with aiohttp.ClientSession() as session:
        tasks = get_request_tasks(session)
        responses = await asyncio.gather(*tasks)
        return responses

def get_all_quotes(): 
    results = asyncio.run(get_all_quote_responses())
    json_results = [asyncio.run(result.json()) for result in results]
    quotes = [quote for sublist in json_results for quote in sublist["results"]]
    return quotes
    
def find_quote_by_id(id):
    all_quotes = get_all_quotes()
    quote_dict = {quote["_id"]: quote for quote in all_quotes}
    return quote_dict[id]

def find_nth_extrema(nth, unsorted_list, max = True):
    """Find the second largest number means nth = 2, max = True
    Find the third largest number means nth = 3, max = True.
    Find the second smallest number means nth = 2, max = False, and so on"""
    unsorted_list = unsorted_list
    if max:
        sorted_list = sorted(list(unsorted_list), reverse = True) # Starts from largest to smallest
        return unsorted_list.index(sorted_list[nth - 1])
    if not max:
        sorted_list = sorted(list(unsorted_list), reverse = False) # Starts from smallest to largest
        return unsorted_list.index(sorted_list[nth - 1])


def find_another_quote(quote, all_quote_ids, different = False):
    "Takes a flattened list of dictionaries containing quote data"

    quote_similarities = quote["quote_similarities"][quote["quote_id"]]
    idx_max = find_nth_extrema(1, quote_similarities, max = not different) #index of max or min value, the most similar/different quote
    quote_id = all_quote_ids[idx_max] #The quote_id using the index of the maximum/minimum similarity score
    nth = 1
    while True:
        if QuoteHistory.query.filter_by(quote_id = quote_id).count() == 0: #Is the quote in our history? No? Carry on
            return Quote.query.filter_by(quote_id = quote_id).first().__dict__
        else: #The most similar quote is already in the user's quote history: Get another quote, but slightly less familiar.
            nth += 1
            nth_idx_max = find_nth_extrema(nth, quote_similarities)
            quote_id = all_quote_ids[nth_idx_max]

def format_times(all_quotes):
    for idx, quote in enumerate(all_quotes):
        all_quotes[idx]["formatted_time"] = quote["time_of_rating"].strftime("%B %-d, %Y at %I:%M %p (UTC)")

    return all_quotes

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
            
            # Get either a similar or different quote, as long as it's not already in the QuoteHistory
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
    docker = os.environ.get('AM_I_IN_A_DOCKER_CONTAINER', False)
    
    create_db_if_necessary()
    add_all_quotes_to_db(sentence_similarity_matrix)

    if docker:
        app.run(debug=True)
    else:
        app.run(debug=True)