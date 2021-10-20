# Introduction

The following app gives a random quote, asks for a user rating, and then displays either another random quote given a low user rating, or finds a similar quote given a high user rating.

It uses asynchronous programming to make 95 HTTP requests to get the 1,885 quotes in around a second and Flask_SQLAlchemy to manage a database with two tables: one of the all of the quotes, and the other to manage the history of quotes a user has liked. It also uses the state-of-the-art natural language processing model BERT, which is also used in Google Search engines as of 2019. Similarity scores between all of the different quotes were calculated using the `create_similarity_matrix.py`. However, since this script takes about 2-4 minutes to run, it has been pre-created and uploaded to this repo.

BERT is revolutionary in that it actually seems to understand the intent of a sentence, rather than simply extracting the key word or key phrase. Here are links to the paper on BERT and the Medium article where I got the code to calculate BERT similarity scores:
* https://arxiv.org/abs/1810.04805
* https://towardsdatascience.com/bert-for-measuring-text-similarity-eec91c6bf9e1

# Start-up Instructions
## Docker

First, we had to create our virtual environment, so we have to install
`pip3 install virtualenv`
`virtualenv env` "env" is the name of the environment, which is the convention, but any name can be used.

Then we had to activate our virtual environment. When active, the "(env)" can be seen next to the command line prompt. We do this so that we can work with other people. We want to make sure all of the requirements are the same for everybody.
`source env/bin/activate` (the usual case)
`source briq-flask-app-env/bin/activate`

Within that environment, install the necessary requirements.
`pip3 install flask flask-sqlalchemy`

After writing the .py file, various .html files, and .css file use the following command to run the local webserver. You can type `localhost:5000` to see the webpage
`python3 app.py`

# Project Notes

We want three pages. The first page shows you a quote, and displays a rating system of 5 potentials stars. If you click on stars 1-3, the page is reloaded with a new quote.

The second page 

# Personal Notes

There's sort of a back and forth communication between the Quote and QuoteHistory class and the database. They both appear to inherit from each other. I didn't track it down in the github code, but I'm assuming db.Model has some classmethods which can be called by db.Column to change db itself.

Seems useful
DataResults = Data.query.filter(Data.id.in_(IDs)).all()

# This sentence similarity matrix was calculated using BERT (Bidirectional Encoder Representations from Transformers), state of the art NLP!
# The BERT model was presented recently in a October 2018 paper. Although too slow to run in the app, the results are good!
# Link to paper: https://arxiv.org/abs/1810.04805
# Link to medium article with Python code to generate a single row in the matrix: https://towardsdatascience.com/bert-for-measuring-text-similarity-eec91c6bf9e1

