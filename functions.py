from wordcloud import WordCloud
import matplotlib.pyplot as plt
import io
import base64
import urllib

import preprocessor as p

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
analyser = SentimentIntensityAnalyzer()


def word_cloud(text):
    try:
        wc = WordCloud(width=1600, height=800,random_state=1, max_words=100,colormap="Paired", background_color='black',)
        wc = wc.generate(text)
        plt.figure(figsize=(10,5))
        plt.imshow(wc, interpolation='bilinear')
        plt.axis("off")
        plt.tight_layout(pad=0)
        image = io.BytesIO()
        plt.savefig(image, format='png')
        image.seek(0)
        string = base64.b64encode(image.read())

        image_64 = 'data:image/png;base64,' + urllib.parse.quote(string)
        return image_64
    except:
        pass

def sentiment_analyzer_scores(sentence):
    score = analyser.polarity_scores(sentence)
    if score['compound']<=-0.01:
        return -1
    if score['compound']>=0.01:
        return 1
    else:
        return 0


def clean_tweet(tweet):
    p.set_options(p.OPT.URL)
    x=p.clean(tweet)
    return x.replace('#', '')


def monthret(x):
    if x==1:
        return 'jan'
    if x==2:
        return 'Feb'
    if x==3:
        return 'Mar'
    if x==4:
        return 'Apr'
    if x==5:
        return 'May'
    if x==6:
        return 'june'
    if x==7:
        return 'july'
    if x==8:
        return 'Aug'
    if x==9:
        return 'Sept'
    if x==10:
        return 'Oct'
    if x==11:
        return 'Nov'
    if x==12:
        return 'Dec'
