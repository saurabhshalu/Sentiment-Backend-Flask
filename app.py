from flask import Flask, request, jsonify
# import sqlite3
from twitter_client import TwitterClient
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.test'

db = SQLAlchemy(app)
# con = sqlite3.connect("tweet_response.db")
# con.execute('create table ')

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))


@app.route('/')
def home():
    return 'Hello'

@app.route('/<hashtag>', methods=['GET'])
def simple_request(hashtag):
    hashtag = '#' + hashtag
    api = TwitterClient()
    tweets = api.simple_analysis(query=hashtag)
    return jsonify(tweets)


@app.route('/insert/<name>')
def insert(name):
    user = User(name=name)
    db.session.add(user)
    db.session.commit()
    return 'Inserted successfully!'

@app.route('/view')
def viewdata():
    users = User.query.all()
    data = {}
    for user in users:
        data[user.id] = user.name
    return jsonify(data)

if __name__ == "__main__":
    app.run(debug=True)