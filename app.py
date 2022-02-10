from email import header
from flask import Flask, render_template, redirect, session, flash, request, g, url_for
from flask_debugtoolbar import DebugToolbarExtension
from config import FLASK_KEY, BEARER_TOKEN, NEWS_API_KEY
from models import db, connect_db, User, Article, Like
from sqlalchemy.exc import IntegrityError
from forms import SearchForm, UserAddForm
import requests
import time


CURR_USER_KEY = 'cur_user'

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///veritas"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = FLASK_KEY
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

connect_db(app)
toolbar = DebugToolbarExtension(app)


@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id
    session['username'] = user.username


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]
    if 'username' in session:
        session.pop('username')


@app.route('/', methods=['GET', 'POST'])
def homepage():
    form = SearchForm()
    return render_template('index.html', form=form)


@app.route('/search', methods=['GET', 'POST'])
def handle_search():
    form = SearchForm()

    if form.validate_on_submit():
        q = form.search.data
        print(f'q: {q}')
        q_start_time = time.time()
        raw_tweets = query_twitter_v1(q, count=10, lang='en')
        if raw_tweets:
            pruned_tweets = prune_tweets(raw_tweets, query_v2=False)
            categorized_tweets = categorize_tweets(pruned_tweets)

            session['tweets'] = categorized_tweets
            session['q_time'] = time.time() - q_start_time
            return redirect('/search')

        form.search.errors.append('No results found. Try another term?')
        return render_template('index.html', form=form)

    tweets = session.get('tweets')
    q_time = session.get('q_time')
    return render_template('search-results.html', tweets=tweets, q_time=q_time)


@app.route('/register', methods=["GET", "POST"])
def signup():
    """Handle user signup.

    Create new user and add to DB. Redirect to home page.
    """

    form = UserAddForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                first_name=form.first_name.data,
                username=form.username.data,
                password=form.password.data,
            )

        except IntegrityError:
            form.username.errors.append('Username already exists.')
            return render_template('/users/signup.html', form=form)

        do_login(user)
        return redirect('/')
    else:
        return render_template('/users/signup.html', form=form)


@app.route('/logout', methods=['POST'])
def logout_user():
    """Logs out user from website."""
    do_logout()

    flash('Successfully logged out.')
    return redirect('/')


@app.route('/login')
def login_user():
    """Logs user into website if account exists."""
    # TODO: Implement this
    pass


def query_twitter_v1(q, count=10, lang='en'):
    """Accepts a user search query. If results found, returns a list of tweet objects; else False."""
    base_url = 'https://api.twitter.com/1.1/search/tweets.json'
    headers = {'Authorization': f'Bearer {BEARER_TOKEN}'}
    add_flags = ' -filter:retweets'
    q = requests.utils.quote(q + add_flags)  # urlencodes query
    print(f'Query url-encoded: {q}')

    params = {
        'q': q,
        'lang': lang,
        'count': count,
        'tweet_mode': 'extended',
        'result_type': 'popular'
    }

    res = requests.get(f'{base_url}', headers=headers,
                       params=params)
    data = res.json()

    raw_tweets = data['statuses']

    if not raw_tweets:
        print('*******************************************')
        print('No popular results. Searching all tweets...')
        print('*******************************************')
        del params['result_type']
        res_2 = requests.get(f'{base_url}', headers=headers,
                             params=params)
        data_2 = res.json()
        raw_tweets_2 = data['statuses']
        if not raw_tweets_2:
            print('NO RESULTS!')
            return False
    # import pdb
    # pdb.set_trace()
    return raw_tweets


def prune_tweets(raw_tweets, query_v2=True):
    """Prunes superfluous fields from the raw tweet response. Returns a list of pruned tweets."""
    unassigned_tweets = []

    for tweet in raw_tweets:
        cur_tweet = {
            'id': tweet['id_str'],
            'type': 'tweet',
            'url': tweet['entities']['urls'][0]['url'] if tweet['entities']['urls'] else None,
            'published': tweet['created_at'],
            'source': tweet['user'].get('name', 'unknown'),
            'text': tweet['full_text'],
            'is_truncated': tweet['truncated'],
        }
        # if query_v2 and tweet['truncated']:
        #     print('Truncated tweet found!')
        #     full_text = query_twitter_v2(cur_tweet['id'])
        #     if full_text:
        #         print('updating text...')
        #         cur_tweet['text'] = full_text
        #         cur_tweet['is_truncated'] = False

        sentiment = query_sentim_API(cur_tweet['text'])
        cur_tweet['polarity'] = sentiment.get('polarity')
        cur_tweet['sentiment'] = sentiment.get('type')

        unassigned_tweets.append(cur_tweet)

    return unassigned_tweets


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
    """Accepts a list of tweet dicts. Returns a tuple comprised of 3 lists: positive, neutral, negative"""
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
