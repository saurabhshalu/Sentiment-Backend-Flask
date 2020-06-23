from flask import Flask, request, jsonify
# import sqlite3
from twitter_client import TwitterClient
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from functions import word_cloud
import json
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'

db = SQLAlchemy(app)

#from models import SearchResult

# con = sqlite3.connect("tweet_response.db")
# con.execute('create table ')

# class User(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(50))


class SearchResult(db.Model):
    hashtag = db.Column(db.String(100), primary_key=True)
    datetime = db.Column(db.DateTime,default=datetime.now)
    positive = db.Column(db.Float, default=0)
    negative = db.Column(db.Float, default=0)
    pos_tweet1 = db.Column(db.String(350))
    pos_tweet2 = db.Column(db.String(350))
    neg_tweet1 = db.Column(db.String(350))
    neg_tweet2 = db.Column(db.String(350))
    mode = db.Column(db.String(10), default="simple") 
    mode_type = db.Column(db.String(10))
    tweet_count = db.Column(db.Integer)
    positive_wcloud = db.Column(db.String(10000000))
    negative_wcloud = db.Column(db.String(10000000))




@app.route('/')
def home():
    return 'Hello'

@app.route('/hashtag/<hashtag>', methods=['GET'])
def simple_request(hashtag):
    hashtag = '#' + hashtag

    db_result = SearchResult.query.get(hashtag)
    update = False
    if db_result != None:
        old_time = db_result.datetime
        curr_time = datetime.now()

        time_diff = (curr_time - old_time).total_seconds()//60
        if time_diff < 1:
            return str(db_result.datetime) + ' from db'
        else:
            update = True
    

    api = TwitterClient()
    tweets = api.simple_analysis(query=hashtag)
    
    ptweets=[]
    ptext=''
    ntweets = []
    ntext = ''

    for tweet in tweets:
        if tweet['sentiment'] == 1:
            ptweets.append(tweet)
            ptext = ptext + " " + tweet['text']
        elif tweet['sentiment'] == -1:
            ntweets.append(tweet)
            ntext = ntext + " " + tweet['text']
    

    response_object = SearchResult(hashtag=hashtag, datetime=datetime.now())

    response_object.tweet_count = len(tweets)
    response_object.positive = 100 * len(ptweets) / len(tweets)
    response_object.negative = 100 * len(ntweets) / len(tweets)
    response_object.positive_wcloud = word_cloud(ptext)
    response_object.negative_wcloud = word_cloud(ntext)

    try:
        response_object.pos_tweet1 = ptweets[len(ptweets)-1]['status']
    except:
        pass
    try:
        response_object.neg_tweet1 = ntweets[len(ntweets) - 1]['status']
    except:
        pass
    try:
        response_object.pos_tweet2 = ptweets[len(ptweets) - 2]['status']
    except:
        pass
    try:
        response_object.neg_tweet2 = ntweets[len(ntweets) - 2]['status']
    except:
        pass

    
    if update == True:
        db_results.datetime = datetime.now()
        db_results.tweet_count = response_object.tweet_count
        db_results.positive = response_object.positive
        db_results.negative = response_object.negative
        db_results.positive_wcloud = response_object.positive_wcloud
        db_results.negative_wcloud = response_object.negative_wcloud
        db_results.pos_tweet1 = response_object.pos_tweet1 or None
        db_results.pos_tweet2 = response_object.pos_tweet2 or None
        db_results.neg_tweet1 = response_object.neg_tweet1 or None
        db_results.neg_tweet2 = response_object.neg_tweet2 or None
        db.session.commit()
        print('updating!')
    else:
        print('new value')
        db.session.add(response_object)
        db.session.commit()
    return str(response_object.datetime) # 'json.dumps(response_object.__dict__)'


# @app.route('/insert/<name>')
# def insert(name):
#     user = User(name=name)
#     db.session.add(user)
#     db.session.commit()
#     return 'Inserted successfully!'

# @app.route('/view')
# def viewdata():
#     users = User.query.all()
#     data = {}
#     for user in users:
#         data[user.id] = user.name
#     return jsonify(data)

if __name__ == "__main__":
    app.run(debug=True)