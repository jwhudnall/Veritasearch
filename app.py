from email import header
from flask import Flask, render_template, redirect, session, flash, request, g
from flask_debugtoolbar import DebugToolbarExtension
from config import FLASK_KEY, BEARER_TOKEN, NEWS_API_KEY
from models import db, connect_db, User, Article, Like
from forms import SearchForm
import requests
import time

CURR_USER_KEY = 'cur_user'

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///veritas"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = FLASK_KEY
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True

connect_db(app)
toolbar = DebugToolbarExtension(app)


# @app.before_request
# def add_user_to_g():
#     """If we're logged in, add curr user to Flask global."""

#     if CURR_USER_KEY in session:
#         g.user = User.query.get(session[CURR_USER_KEY])

#     else:
#         g.user = None


# def do_login(user):
#     """Log in user."""

#     session[CURR_USER_KEY] = user.id


# def do_logout():
#     """Logout user."""

#     if CURR_USER_KEY in session:
#         del session[CURR_USER_KEY]


@app.route('/')
def homepage():
    form = SearchForm()
    return render_template('index.html', form=form)


@app.route('/search', methods=['GET', 'POST'])
def handle_search():
    form = SearchForm()

    if form.validate_on_submit():
        # q = request.args['q']
        q = form.search.data
        print(f'q: {q}')
        twitter_response = query_twitter_v1(q)
        if not twitter_response:
            form.search.errors.append('No results found. Try another term?')
            return redirect('/')
        return render_template('search-results.html', q=twitter_response)

    flash('Please search using the search bar below.')
    return redirect('/')

    # TWITTER:


def query_twitter_v1(q, popular_results=True):
    """Accepts a user search query. Returns a JSON object."""
    v1_base_url = 'https://api.twitter.com/1.1/search/tweets.json'
    headers = {'Authorization': f'Bearer {BEARER_TOKEN}'}
    add_flags = ' -filter:retweets'
    q = requests.utils.quote(q + add_flags)  # urlencodes query
    print(f'Query url-encoded: {q}')

    params = {
        'q': q,
        'lang': 'en',
        'count': 10,
        'result_type': 'popular'
    }

    res = requests.get(f'{v1_base_url}', headers=headers,
                       params=params)
    data = res.json()

    tweets = data['statuses']

    if not tweets:
        # print('No results. result_type header removed!')
        del params['result_type']
        # print(f'Params updated: {params}')
        res = requests.get(f'{v1_base_url}', headers=headers,
                           params=params)
        data = res.json()
        tweets = data['statuses']
        if not tweets:
            # form.search.errors.append('')
            print('NO RESULTS!')
            return False

    # TODO: If tweets does not contain valid results, requery API setting popular_results=False

    unassigned_tweets = []

    for tweet in tweets:
        cur_tweet = {
            'id': tweet['id_str'],
            'type': 'tweet',
            'url': tweet['entities']['urls'][0]['url'] if tweet['entities']['urls'] else None,
            'published': tweet['created_at'],
            'source': tweet['user'].get('name', 'unknown'),
            'text': tweet['text'],
            'is_truncated': tweet['truncated'],
        }
        if tweet['truncated']:
            print('Truncated tweet found!')
            full_text = query_twitter_v2(cur_tweet['id'])
            if full_text:
                print('updating text...')
                cur_tweet['text'] = full_text
                cur_tweet['is_truncated'] = False

        sentiment = query_sentim_API(cur_tweet['text'])
        cur_tweet['polarity'] = sentiment.get('polarity')
        cur_tweet['sentiment'] = sentiment.get('type')

        unassigned_tweets.append(cur_tweet)
    # import pdb
    # pdb.set_trace()
    return categorize_tweets(unassigned_tweets)


def query_twitter_v2(id):
    """Query Twitter v2 API. If success, returns the full tweet text; else False"""

    print('Twitter v2 API called!')
    base_url = 'https://api.twitter.com/2/tweets'
    headers = {'Authorization': f'Bearer {BEARER_TOKEN}'}
    res = requests.get(f'{base_url}/{id}', headers=headers)

    if res.status_code == 200:
        data = res.json()
        text = data['data']['text']
        print('Text updated:')
        print(text)
        print('***************')
        return text

    return False


def categorize_tweets(tweet_lst):
    """Accepts a list of tweet dicts. Returns 3 lists: negative, neutral, positive"""
    negative = []
    neutral = []
    positive = []

    for tweet in tweet_lst:
        if tweet['sentiment'] == 'positive':
            positive.append(tweet)
        elif tweet['sentiment'] == 'negative':
            negative.append(tweet)
        elif tweet['sentiment'] == 'neutral':
            neutral.append(tweet)

    return (positive, neutral, negative)


def query_sentim_API(text):
    """Query the sentim API. Text is passed and analyzed for sentiment.

    Returns a dictionary with keys: 'polarity' and 'positive'
      ex: {'polarity': 0.4, 'type': 'positive'}
    """

    base_url = 'https://sentim-api.herokuapp.com/api/v1/'
    headers = {'Accept': 'application/json',
               'Content-Type': 'application/json'}
    json = {'text': text}

    res = requests.post(base_url, headers=headers, json=json)
    data = res.json()
    return data['result'] or False
