from flask import Flask, request, jsonify
from twitter_client import TwitterClient
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from functions import word_cloud, to_json, monthret, clean_tweet, sentiment_analyzer_scores
import GetOldTweets3 as got
from flask_cors import CORS
app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'

db = SQLAlchemy(app)

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
@app.route('/hashtag/<hashtag>/<count>', methods=['GET'])
def simple_request(hashtag, count=100):
    hashtag = '#' + hashtag
    count = int(count)
    db_result = SearchResult.query.get(hashtag)
    update = False
    if db_result != None:
        old_time = db_result.datetime
        curr_time = datetime.now()

        time_diff = (curr_time - old_time).total_seconds()//60
        if time_diff < 1:
            return to_json(SearchResult, db_result)
        else:
            update = True
    

    api = TwitterClient()
    tweets = api.tweet_analysis(query=hashtag, count=count)
    
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
        db_result.datetime = datetime.now()
        db_result.tweet_count = response_object.tweet_count
        db_result.positive = response_object.positive
        db_result.negative = response_object.negative
        db_result.positive_wcloud = response_object.positive_wcloud
        db_result.negative_wcloud = response_object.negative_wcloud
        db_result.pos_tweet1 = response_object.pos_tweet1 or None
        db_result.pos_tweet2 = response_object.pos_tweet2 or None
        db_result.neg_tweet1 = response_object.neg_tweet1 or None
        db_result.neg_tweet2 = response_object.neg_tweet2 or None
        db.session.commit()
    else:
        db.session.add(response_object)
        db.session.commit()

    return to_json(SearchResult, response_object)


@app.route('/hashtag/<hashtag>/<type>/<type_count>/<count_per_type>', methods=['GET'])
def detailed_request(hashtag, type, type_count, count_per_type):
    hashtag = '#' + hashtag

    db_result = SearchResult.query.get(hashtag)
    update = db_result != None

    type_count = int(type_count)
    count_per_type = int(count_per_type)
    api = TwitterClient()

    tcountp=0
    tcountn=0
    ttcount=0
    label = []
    count = []
    poslist = []
    neglist = []
    postweet = []
    negtweet= []
    ntext = ''
    ptext = ''

    response_object = SearchResult(hashtag=hashtag, datetime=datetime.now())

    if type=='day':
        x = datetime.today()
        for key in range(type_count):
            edate = x - timedelta(days=key)
            sdate = x - timedelta(days=key+1)
            tweets = api.tweet_analysis(query=hashtag,type='detailed',until=edate.strftime('%Y-%m-%d'),since=sdate.strftime('%Y-%m-%d') ,count=count_per_type)
            positive = 0
            negative = 0
            pz=0
            if len(tweets) > 0:
                ptweets=[]
                for tweet in tweets:
                    if tweet['sentiment'] == 1:
                        ptweets.append(tweet)
                        ptext = ptext + " " + tweet['text']
                ntweets = []
                for tweet in tweets:
                    if tweet['sentiment'] == -1:
                        ntweets.append(tweet)
                        ntext = ntext + " " + tweet['text']
                px=len(ptweets)
                py=len(tweets)
                positive = 100 * px/py
                ttcount += py
                tcountp += px
                pz=len(ntweets)
                negative = 100 * pz/py
            label.append(str(edate.strftime('%d'))+"/"+ str(monthret(int(edate.strftime('%m')))))
            count.append(len(tweets))
            poslist.append(positive)
            neglist.append(negative)
            tcountn+=pz
            if key == 0:
                try:
                    postweet.append(ptweets[len(ptweets) - 1]['status'])
                except:
                    pass
                try:
                    negtweet.append(ntweets[len(ntweets) - 1]['status'])
                except:
                    pass
                try:
                    postweet.append(ptweets[len(ptweets) - 2]['status'])
                except:
                    pass
                try:
                    negtweet.append(ntweets[len(ntweets) - 2]['status'])
                except:
                    pass
    else:
        x = datetime.now().month
        y1 = datetime.now().year
        for key in range(type_count):
            month1=x-key
            year1 = y1
            if month1 <= 0 :
                year1 = y1 - 1
                month1 += 12
            dates1 = str(year1) + '-' + str(month1) + '-'
            tweetCriteria = got.manager.TweetCriteria().setQuerySearch(hashtag) \
                .setSince(dates1 + "01") \
                .setUntil(dates1 + "28") \
                .setMaxTweets(count_per_type)
            try:
                tweetgot = got.manager.TweetManager.getTweets(tweetCriteria)
                tweets = []
                for tweet in tweetgot:

                    parsed_tweet = {}
                    parsed_tweet['status'] = f'https://twitter.com/{tweet.username}/status/{tweet.id}'
                    y = clean_tweet(tweet.text)
                    parsed_tweet['text'] = y
                    parsed_tweet['sentiment'] = sentiment_analyzer_scores(y)
                    if tweet.retweets > 0:
                        if parsed_tweet not in tweets:
                            tweets.append(parsed_tweet)
                    else:
                        tweets.append(parsed_tweet)
                positive = 0
                negative = 0
                if len(tweets) > 0:
                    ptweets = []
                    for tweet in tweets:
                        if tweet['sentiment'] == 1:
                            ptweets.append(tweet)
                            ptext = ptext + " " + tweet['text']
                    ntweets = []
                    for tweet in tweets:
                        if tweet['sentiment'] == -1:
                            ntweets.append(tweet)
                            ntext = ntext + " " + tweet['text']
                    positive = 100 * len(ptweets) / len(tweets)
                    negative = 100 * len(ntweets) / len(tweets)
                label.append(str(monthret(month1)) + "/" + str(year1))
                count.append(len(tweets))
                poslist.append(positive)
                neglist.append(negative)
                ttcount += len(tweets)
                tcountp += len(ptweets)
                tcountn += len(ntweets)
                if key == 0:
                    try:
                        postweet.append(ptweets[len(ptweets) - 1]['status'])
                    except:
                        pass
                    try:
                        negtweet.append(ntweets[len(ntweets) - 1]['status'])
                    except:
                        pass
                    try:
                        postweet.append(ptweets[len(ptweets) - 2]['status'])
                    except:
                        pass
                    try:
                        negtweet.append(ntweets[len(ntweets) - 2]['status'])
                    except:
                        pass
            except:
                pass
    
    


    response_object.tweet_count = len(tweets)
    response_object.positive = 100 * tcountp / ttcount
    response_object.negative = 100 * tcountn / ttcount
    response_object.positive_wcloud = word_cloud(ptext)
    response_object.negative_wcloud = word_cloud(ntext)

    try:
        response_object.pos_tweet1 = postweet[0]
    except:
        pass
    try:
        response_object.neg_tweet1 = negtweet[0]
    except:
        pass
    try:
        response_object.pos_tweet2 = postweet[1]
    except:
        pass
    try:
        response_object.neg_tweet2 = negtweet[1]
    except:
        pass

    
    if update == True:
        db_result.datetime = datetime.now()
        db_result.tweet_count = response_object.tweet_count
        db_result.positive = response_object.positive
        db_result.negative = response_object.negative
        db_result.positive_wcloud = response_object.positive_wcloud
        db_result.negative_wcloud = response_object.negative_wcloud
        db_result.pos_tweet1 = response_object.pos_tweet1 or None
        db_result.pos_tweet2 = response_object.pos_tweet2 or None
        db_result.neg_tweet1 = response_object.neg_tweet1 or None
        db_result.neg_tweet2 = response_object.neg_tweet2 or None
        db.session.commit()
    else:
        db.session.add(response_object)
        db.session.commit()

    returndata = {
        "hashtag": hashtag, 
        "positive": response_object.positive, 
        "negative": response_object.negative,
        "tweetcount": ttcount, 
        "datetime": response_object.datetime,
        "label": label, 
        "count": count, 
        "positive_list": poslist,
        "negative_list": neglist, 
        "positive_tweet": postweet, 
        "negative_tweet": negtweet, 
        "ptweet": tcountp, 
        "ntweet": tcountn,
        "positive_wcloud":response_object.positive_wcloud,
        "negative_wcloud":response_object.negative_wcloud
    }
    return jsonify(returndata)

if __name__ == "__main__":
    app.run()