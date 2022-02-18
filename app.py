from email import header
from flask import Flask, render_template, redirect, session, flash, request, g, url_for, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from config import FLASK_KEY, BEARER_TOKEN, NEWS_API_KEY
from models import db, connect_db, User, Query
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import Unauthorized
from forms import UserAddForm, LoginForm
import requests
import time
import random
import os
import json


CURR_USER_KEY = 'cur_user'

app = Flask(__name__)
# app.config["SQLALCHEMY_DATABASE_URI"] = (
#     os.environ.get('DATABASE_URL', "postgresql:///veritas"))
app.config["SQLALCHEMY_DATABASE_URI"] = 'postgresql:///veritas'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = False
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
    if 'headlines' in session:
        session.pop('headlines')
    do_clear_search_cookies()


def do_clear_search_cookies():
    cookies = ['tweets', 'q_time', 'query_response', 'q', 'query']
    for cookie in cookies:
        if cookie in session:
            session.pop(cookie)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.route('/')
def homepage():
    do_clear_search_cookies()

    latest_queries = ['Tesla', 'Superbowl', 'Russia Ukraine']
    return render_template('index.html', queries=latest_queries)


@app.route('/search')
def handle_search():

    user = g.user if g.user else None
    query = request.args.get('query', None)

    if query:
        query = query.lower()
        new_query = Query(text=query)
        q_start_time = time.time()
        raw_tweets = query_twitter_v1(query, count=25, lang='en')
    else:
        raw_tweets = None

    if raw_tweets:
        pruned_tweets = prune_tweets(
            raw_tweets, id_key="id_str", text_key="full_text")
        categorized_tweets = categorize_by_sentiment(pruned_tweets)
        q_time = round(time.time() - q_start_time, 2)

        if user:
            user_queries = [q.text for q in user.queries]
            if query not in user_queries:
                user.queries.append(new_query)
                db.session.add(user)

            # append_to_db(pruned_tweets, new_query)

        db.session.add(new_query)
        db.session.commit()

        session['query'] = query
        return render_template('search-results.html', tweets=categorized_tweets, query=query, q_time=q_time, test_tweets=categorized_tweets)

    else:
        do_clear_search_cookies()
        # form.search.errors.append('No results found. Try another term?')
        flash('Nothing found. Try another term?', 'no-results')
        return redirect('/')


@app.route('/search/<query>', methods=['GET'])
def display_results(query):
    return redirect(url_for('handle_search', query=query))


@app.route('/register/newUserSignup', methods=["GET", "POST"])
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
            flash('Username already exists. Please try another.', 'error')
            return redirect(request.referrer)

        do_login(user)
        flash(f'Account successfully created.', 'success')
        return redirect('/')
    else:
        return render_template('/users/register.html', form=form)


@app.route('/login/returningUser', methods=['GET', 'POST'])
def login_user():
    """Logs user into website if account exists."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(
            form.username.data,
            form.password.data
        )

        if user:
            do_login(user)
            return redirect(request.referrer)
        else:
            flash('Incorrect username or password.', 'error')
            return redirect(request.referrer)

    do_clear_search_cookies()
    return render_template('users/login.html', form=form)


@app.route('/logout', methods=['POST'])
def logout_user():
    """Logs out user from website."""
    do_logout()

    flash('Successfully logged out.', 'success')
    return redirect('/')


@app.route('/users/<int:user_id>')
def show_user_details(user_id):
    """Show user details page."""

    if CURR_USER_KEY not in session and g.user == None:
        raise Unauthorized()
    if user_id != session[CURR_USER_KEY]:
        return redirect(f'/users/{g.user.id}')

    user = User.query.get_or_404(user_id)
    queries = [q.serialize() for q in user.queries]

    return render_template('users/user-details.html', user=user, queries=queries)


@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Delete user account."""

    if CURR_USER_KEY not in session and g.user == None:
        raise Unauthorized()
    if user_id != session[CURR_USER_KEY]:
        return redirect(f'/users/{g.user.id}')

    db.session.delete(g.user)
    db.session.commit()
    do_logout()
    # return redirect('/')
    flash(f'Account successfully deleted.', 'success')
    return jsonify(msg="Account Deleted.")

# Queries


@app.route('/queries/<int:query_id>', methods=['DELETE'])
def delete_query(query_id):
    """Deletes a user query. Returns confirmation message in JSON format."""
    # TODO: Protect via authentication to verify user "owns" query
    query = Query.query.get_or_404(query_id)
    query_users = [u.id for u in query.users]
    cur_user = session.get(CURR_USER_KEY, None)

    if not cur_user or cur_user not in query_users:
        raise Unauthorized()

    q = Query.query.get_or_404(query_id)
    db.session.delete(q)
    db.session.commit()
    flash('Query removed.', 'success')
    return jsonify(message="Query deleted")


@app.route('/privacy')
def display_privacy_policy():
    return render_template('privacy.html')
# ****************
# API
# ****************


@app.route('/api/tweets')
def fetch_tweets():
    """Retrieve tweets and resturn as JSON."""
    query = request.args.get('query', None)

    if query:
        # q_start_time = time.time()
        # Split string on commas. Depending on length, select 2 or 3 random items
        q_split = query.split(',')
        if len(q_split) == 1:
            query = q_split[0]
        else:
            first = random.choice(q_split)
            q_split.remove(first)
            second = random.choice(q_split)
            query = f'({first} OR {second})'

        raw_tweets = query_twitter_v2(query, count=20)
        if raw_tweets:
            pruned_tweets = prune_tweets(
                raw_tweets, id_key="id", text_key="text")
            categorized_tweets = categorize_by_sentiment(pruned_tweets)

            # session['tweets'] = categorized_tweets
            session['query'] = query
            # return redirect('/search')
            response = jsonify(tweets=categorized_tweets)
        else:
            response = jsonify(error='no tweets found')
            do_clear_search_cookies()
            # form.search.errors.append('No results found. Try another term?')
    else:
        response = jsonify(error='No query args received by server')

    return response


# ****************
# Helper Functions
# ****************

def remove_duplicates(queries):
    """Removes duplicates from a list, whilst preserving the order."""
    seen = set()
    seen_add = seen.add
    return [q for q in queries if not (q in seen or seen_add(q))]


def get_latest_queries(n):
    """Retrieves the n latest queries in descending order. Returns a list of serialized query objects."""
    queries = Query.query.order_by(Query.id.desc()).all()
    queries_text = [q.text for q in queries]
    filtered_queries = remove_duplicates(queries_text)

    return filtered_queries[:n]


# def query_twitter_oembed(id, max_width=400):
#     """Embeds a tweet using the tweet id. Returns embed HTML if id exists; else False."""
#     base_url = 'https://publish.twitter.com/oembed'
#     params = {
#         'url': f'https://twitter.com/Interior/status/{id}',
#         'maxwidth': max_width,
#         'omit_script': 'true'
#     }
#     res = requests.get(base_url, params=params)
#     html = False
#     if res.status_code == 200:
#         data = res.json()
#         html = data.get('html')

#     if html and res.status_code == 200:
#         return html
#     return False

def query_twitter_v2(q, count=10):
    base_url = 'https://api.twitter.com/2/tweets/search/recent'
    headers = {'Authorization': f'Bearer {BEARER_TOKEN}'}
    # add_flags = ' is:verified lang:en -is:retweet'
    add_flags = ' is:verified lang:en -is:retweet'
    q = q + add_flags
    print(f'Query url-encoded: {q}')
    params = {
        'query': q,
        'max_results': count
    }
    res = requests.get(f'{base_url}', headers=headers,
                       params=params)

    data = res.json()
    raw_tweets = data.get('data', None)
    print(f'Total v2 results found: {len(raw_tweets)}')
    return raw_tweets if raw_tweets else False


def query_twitter_v1(q, count=10, lang='en'):
    """Accepts a user search query. If results found, returns a list of tweet objects; else False.

    API is first queried for popular results. If none found, a second query is sent for all results.
    """
    base_url = 'https://api.twitter.com/1.1/search/tweets.json'
    headers = {'Authorization': f'Bearer {BEARER_TOKEN}'}
    add_flags = ' -filter:retweets'
    q = requests.utils.quote(q + add_flags)  # urlencodes query
    print(f'Query url-encoded: {q}')

    params = {
        'q': q,
        'lang': lang,
        'tweet_mode': 'extended',
        'result_type': 'popular',
        'count': 22
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
        data_2 = res_2.json()
        raw_tweets_2 = data_2['statuses']

        if not raw_tweets_2:
            print('NO RESULTS!')
            return False
        else:
            return raw_tweets_2
    print(f'Total results found: {len(raw_tweets)}')
    return raw_tweets


def prune_tweets(raw_tweets, id_key, text_key):
    """Prunes superfluous fields from the raw tweet response. Returns a list of pruned tweets.

    Keys to be returned: id, text, polarity, sentiment, embed_html
    """
    unassigned_tweets = []

    for tweet in raw_tweets:
        cur_tweet = {
            "id": tweet.get(id_key),
            "text": tweet.get(text_key)
        }
        sentiment = query_sentim_API(cur_tweet["text"])
        cur_tweet["polarity"] = sentiment.get("polarity")
        cur_tweet["sentiment"] = sentiment.get("type").title()
        # cur_tweet['embed_html'] = query_twitter_oembed(cur_tweet.get('id'))
        del cur_tweet['text']

        unassigned_tweets.append(cur_tweet)

    return unassigned_tweets


# def query_newsAPI(q, min_results=10, count=20, lang='en'):
#     """Searches the newsAPI for q. If results found, returns a list of article objects; else False."""
#     base_url = 'https://newsapi.org/v2/everything'
#     headers = {'X-Api-Key': NEWS_API_KEY}
#     params = {
#         'q': q,
#         'language': lang,
#         'searchIn': 'title',
#         'pageSize': count,
#         'sortBy': 'publishedAt'
#     }

#     res = requests.get(base_url, headers=headers,
#                        params=params)
#     data = res.json()
#     num_results = data['totalResults']
#     if not num_results or num_results < min_results:
#         print('*******************************************')
#         print('Not found in title. Searching content...')
#         print('*******************************************')
#         params["searchIn"] = "content"

#         res_2 = requests.get(base_url, headers=headers, params=params)
#         data = res_2.json()
#         num_results_2 = data["totalResults"]
#         if not num_results_2:
#             print("NO RESULTS FOUND ANYWHERE!")
#             return False

#     return data["articles"]


def categorize_by_sentiment(obj_lst):
    """Runs each obj in list through a NLP API and categorizes each based on sentiment, by polarity score.

    Accepts: a list of information dicts.
    Returns: a tuple comprised of 3 lists: positive, neutral, negative.
    """
    negative = []
    neutral = []
    positive = []

    for obj in obj_lst:
        if obj['sentiment'] == 'Positive':
            positive.append(obj)
        elif obj['sentiment'] == 'Negative':
            negative.append(obj)
        elif obj['sentiment'] == 'Neutral':
            neutral.append(obj)

    negative.sort(key=lambda obj: obj['polarity'])
    positive.sort(key=lambda obj: obj['polarity'], reverse=True)

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
