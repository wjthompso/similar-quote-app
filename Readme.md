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