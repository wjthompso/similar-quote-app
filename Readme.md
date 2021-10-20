# Project Summary

The following app gives a random quote, asks for a user rating, and then displays either another random quote given a low user rating (1-3 stars), or finds a similar quote given a high user rating (4-5 stars).

It uses asynchronous programming to make 95 HTTP requests for the 1,885 quotes in around a second and Flask_SQLAlchemy to manage a database with two tables: one with all the quotes, and the other to manage the history of quotes a user has liked. 

It also uses the state-of-the-art natural language processing model BERT, which is also used in Google Search engine as of 2019. Similarity scores between all of the different quotes were calculated using the `create_similarity_matrix.py`. However, since this script takes about 2-4 minutes to run, the similarity matrix has been pre-created and uploaded to this repo.

BERT is revolutionary in that it actually seems to understand the intent of a sentence, rather than simply extracting the key word or key phrase. Here are links to the paper on BERT and the Medium article where I got the code to calculate BERT similarity scores:
* https://arxiv.org/abs/1810.04805
* https://towardsdatascience.com/bert-for-measuring-text-similarity-eec91c6bf9e1

# Start-up Instructions
## Docker

Assuming you have docker installed, run the following command and then go to `localhost:8000` on your machine:

`docker compose up`

## Running the app locally

If you'd like to run the app locally, please do the following.

First, we had to create our virtual environment, so we have to install virtualenv and then create the virtual environment with the name `app-env`:

`pip3 install virtualenv`<br>
`virtualenv app-env`

Then we had to activate our virtual environment. When active, the "(env)" can be seen next to the command line prompt. We do this so that we can work with other people. We want to make sure all of the requirements are the same for everybody.

`source app-env/bin/activate`

Within that environment, install the necessary requirements.

`pip3 install -r requirements.txt`

After writing the .py file, various .html files, and .css file use the following command to run the local webserver. You can type `localhost:8000` to see the webpage:

`python3 app.py`

