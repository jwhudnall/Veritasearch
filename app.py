from email import header
from flask import Flask, render_template, redirect, session, flash, request, g, url_for, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from config import FLASK_KEY, BEARER_TOKEN, NEWS_API_KEY
from models import db, connect_db, User, Article, Like, Query
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import Unauthorized
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from forms import SearchForm, UserAddForm, LoginForm
import nltk
import requests
import time
import json
import itertools
nltk.download('stopwords')
nltk.download('punkt')


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
        print('***********')
        print(f'g.user set: {g.user}')
        print('***********')
    # Check for cur_user_query_term

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


@app.route('/')
def homepage():
    form = SearchForm()
    do_clear_search_cookies()
    # If headlines exist in cookies, use those instead
    if 'headlines' in session:
        headlines = session['headlines']
    else:
        headlines = get_headlines(count=3)
        session['headlines'] = headlines
    return render_template('index.html', form=form, headlines=headlines)


@app.route('/search')
def handle_search():

    user = g.user if g.user else None

    # query = request.form['query']
    query = request.args.get('query')

    new_query = Query(text=query)
    if user:
        user_queries = [q.text for q in user.queries]
        if query not in user_queries:
            user.queries.append(new_query)
            db.session.add(user)
        # Add cookie for user_query? Any liked articles can then be linked to this query.
    db.session.add(new_query)
    db.session.commit()

    q_start_time = time.time()
    raw_tweets = query_twitter_v1(query, count=20, lang='en')
    if raw_tweets:
        pruned_tweets = prune_tweets(raw_tweets)
        categorized_tweets = categorize_by_sentiment(pruned_tweets)
        q_time = round(time.time() - q_start_time, 2)
        if user:
            append_to_db(pruned_tweets, new_query)

        session['query'] = query
        # return redirect(url_for('handle_search', tweets=json_tweets, query=query, q_time=q_time))
        return render_template('search-results.html', tweets=categorized_tweets, query=query, q_time=q_time)

    else:
        do_clear_search_cookies()
        # form.search.errors.append('No results found. Try another term?')
        flash('Nothing found. Try another term?')
        return redirect('/')

    # elif request.method == 'GET':
    #     tweets = json.loads(request.args['tweets'])
    #     query = request.args['query']
    #     q_time = request.args['q_time']
    #     session['query'] = query

    #     return render_template('search-results.html', tweets=tweets, query=query, q_time=q_time)

    # # end test area

    # # Old:
    # query = request.args.get('query')
    # new_query = Query(text=query)
    # if user:
    #     user_queries = [q.text for q in user.queries]
    #     if query not in user_queries:
    #         user.queries.append(new_query)
    #         db.session.add(user)
    #     # Add cookie for user_query. Any liked articles can then be linked to this query.
    # db.session.add(new_query)
    # db.session.commit()
    # return render_template('search-results.html', testQuote=testQuote)


@app.route('/search/<query>', methods=['GET'])
def display_results(query):
    return redirect(url_for('handle_search', query=query))


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

    # flash('Successfully logged out.')
    return redirect('/')


@app.route('/login', methods=['GET', 'POST'])
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
            # flash(f'Welcome back, {user.username}')
            return redirect('/')

    do_clear_search_cookies()
    return render_template('users/login.html', form=form)


@app.route('/users/<int:user_id>')
def show_user_details(user_id):
    """Show user details page."""

    if CURR_USER_KEY not in session or g.user.id != session[CURR_USER_KEY]:
        raise Unauthorized()
        # OR, redirect to /

    # Shouldn't need _or_404, as user_id already verified?
    user = User.query.get_or_404(user_id)
    queries = [q.serialize() for q in user.queries]
    articles_by_query = [q.articles for q in user.queries]
    relevant_articles = list(itertools.chain(*articles_by_query))
    articles_formatted = [a.serialize() for a in relevant_articles]

    tweets = categorize_by_sentiment(articles_formatted)

    return render_template('users/user-details.html', user=user, queries=queries, tweets=tweets)


# def query_relevant_articles(queries):
    # queries = ['tesla','bananas','dogs', ...]

    # SELECT embed_html FROM articles WHERE text ILIKE '%tesla%' OR text ILIKE '%banana%'
    # if len(queries) < 3:
    #     articles = Article.query.filter(db.or_(
    #         Article.text.ilike('%tesla%'),
    #         Article.text.ilike('%bananas%'))).all()
    # handle case with queries len of 1
    # handle case with queries len of 2
    # handle case with more queries


@app.route('/users/<int:user_id>/delete', methods=['POST'])
def delete_user(user_id):
    """Delete user account."""

    if CURR_USER_KEY not in session or g.user.id != session[CURR_USER_KEY]:
        raise Unauthorized()
        # OR, redirect to /

    # Shouldn't need _or_404, as user_id already verified?
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    do_logout()
    return redirect('/')

# Queries


@app.route('/queries/<int:query_id>', methods=['DELETE'])
def delete_query(query_id):
    """Deletes a user query. Returns confirmation message in JSON format."""
    # TODO: Protect via authentication to verify user "owns" query
    if CURR_USER_KEY not in session or g.user.id != session[CURR_USER_KEY]:
        raise Unauthorized()

    q = Query.query.get_or_404(query_id)
    db.session.delete(q)
    db.session.commit()
    return jsonify(message="Query deleted")


# ****************
# API
# ****************


@app.route('/api/articles')
def fetch_articles():
    """Retrieve articles and return as JSON."""
    # TODO: Protect this route in any scenarios?
    query = request.args.get('q', None)
    if query:
        # q_start_time = time.time()
        raw_articles = query_newsAPI(query, count=20)
        if raw_articles:
            pruned_articles = prune_articles(raw_articles)
            categorized_articles = categorize_by_sentiment(pruned_articles)

            session['query'] = query
            response = jsonify(articles=categorized_articles)
        else:
            response = jsonify(error='no articles found')
    else:
        response = jsonify(error='No query args received by server')

    return response


@app.route('/api/tweets')
def fetch_tweets():
    """Retrieve tweets and resturn as JSON."""
    query = request.args.get('q', None)
    if query:
        # q_start_time = time.time()
        raw_tweets = query_twitter_v1(query, count=20, lang='en')
        if raw_tweets:
            pruned_tweets = prune_tweets(raw_tweets)
            categorized_tweets = categorize_by_sentiment(pruned_tweets)

            # session['tweets'] = categorized_tweets
            session['query'] = query
            # return redirect('/search')
            response = jsonify(tweets=categorized_tweets)
        else:
            response = jsonify(error='no articles found')
            do_clear_search_cookies()
            # form.search.errors.append('No results found. Try another term?')
    else:
        response = jsonify(error='No query args received by server')

    return response


# ****************
# Helper Functions
# ****************

def append_to_db(tweets, query):
    for t in tweets:
        try:
            new_article = Article(
                id=t['id'],
                text=t['text'],
                sentiment=t['sentiment'],
                polarity=t['polarity'],
                embed_html=t['oembed_url']
            )
            db.session.add(new_article)
            new_article.queries.append(query)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()


def get_headlines(count=3):
    """Retrieve top headlines."""
    base_url = 'https://newsapi.org/v2/top-headlines'
    headers = {'X-Api-Key': NEWS_API_KEY}
    params = {
        'country': 'us'
    }
    res = requests.get(f'{base_url}', headers=headers,
                       params=params)
    data = res.json()
    if data.get('articles'):
        headlines = []
        for i in range(count):
            title = data['articles'][i]['title']
            truncated = remove_stop_words(title, n=2)
            headlines.append(truncated)
    else:
        flash('Headlines API appears to be down')
        return False

    return headlines


def remove_stop_words(text, n=2):
    """Uses nltk to convert text into tokens. Removes stopwords and returns a string of n words."""
    text_tokens = word_tokenize(text)
    text_tokens_no_sw = [
        word for word in text_tokens if not word in stopwords.words()]
    filtered_sentence = (" ").join(text_tokens_no_sw[0:n])
    return filtered_sentence


def query_twitter_oembed(id):
    """Embeds a tweet using the tweet id. Returns embed HTML if id exists; else False."""
    base_url = 'https://publish.twitter.com/oembed'
    params = {
        'url': f'https://twitter.com/Interior/status/{id}',
        # 'maxwidth': 220,
        'omit_script': 'true'
    }
    res = requests.get(base_url, params=params)
    html = False
    if res.status_code == 200:
        data = res.json()
        html = data.get('html')

    if html and res.status_code == 200:
        return html
    return False


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
        data_2 = res_2.json()
        raw_tweets_2 = data_2['statuses']

        if not raw_tweets_2:
            print('NO RESULTS!')
            return False
        else:
            return raw_tweets_2

    return raw_tweets


def prune_tweets(raw_tweets):
    """Prunes superfluous fields from the raw tweet response. Returns a list of pruned tweets."""
    unassigned_tweets = []

    for tweet in raw_tweets:
        cur_tweet = {
            "id": tweet["id_str"],
            # "type": "tweet",
            # "url": tweet["entities"]["urls"][0]["url"] if tweet["entities"]["urls"] else None,
            # "published": tweet["created_at"],
            # "source": tweet["user"].get("name", "unknown"),
            "text": tweet["full_text"]
        }
        sentiment = query_sentim_API(cur_tweet["text"])
        cur_tweet["polarity"] = sentiment.get("polarity")
        cur_tweet["sentiment"] = sentiment.get("type")
        cur_tweet['oembed_url'] = query_twitter_oembed(cur_tweet.get('id'))

        unassigned_tweets.append(cur_tweet)

    return unassigned_tweets


def query_newsAPI(q, min_results=10, count=20, lang='en'):
    """Searches the newsAPI for q. If results found, returns a list of article objects; else False."""
    base_url = 'https://newsapi.org/v2/everything'
    headers = {'X-Api-Key': NEWS_API_KEY}
    params = {
        'q': q,
        'language': lang,
        'searchIn': 'title',
        'pageSize': count,
        'sortBy': 'publishedAt'
    }

    res = requests.get(base_url, headers=headers,
                       params=params)
    data = res.json()
    num_results = data['totalResults']
    if not num_results or num_results < min_results:
        print('*******************************************')
        print('Not found in title. Searching content...')
        print('*******************************************')
        params["searchIn"] = "content"

        res_2 = requests.get(base_url, headers=headers, params=params)
        data = res_2.json()
        num_results_2 = data["totalResults"]
        if not num_results_2:
            print("NO RESULTS FOUND ANYWHERE!")
            return False

    return data["articles"]


def prune_articles(raw_articles):
    """Prunes superfluous fields from the raw article response. Returns a list of pruned articles."""
    article_lst = []

    for article in raw_articles:
        cur_article = {
            # Create unique id incorporating datatime?
            "type": "article",
            "url": article["url"],
            "img_url": article.get("urlToImage", None),
            "published": article["publishedAt"],
            "source": article.get("author", "unknown"),
            "title": article["title"],
            "description": article["description"],
            "content": article["content"]
        }
        # sentiment_search_str = ' . '.join(
        #     [cur_article['title'], cur_article['description'], cur_article['content']])
        sentiment_search_str = f"{cur_article['title']}. {cur_article['description']}"
        # sentiment_search_str = cur_article["title"]

        sentiment = query_sentim_API(sentiment_search_str)
        cur_article["polarity"] = sentiment.get("polarity")
        cur_article["sentiment"] = sentiment.get("type")

        article_lst.append(cur_article)

    return article_lst


# def query_twitter_v2(id):
#     """Query Twitter v2 API. If success, returns the full tweet text; else False"""

#     print('Twitter v2 API called!')
#     base_url = 'https://api.twitter.com/2/tweets'
#     headers = {'Authorization': f'Bearer {BEARER_TOKEN}'}
#     res = requests.get(f'{base_url}/{id}', headers=headers)

#     if res.status_code == 200:
#         data = res.json()
#         text = data['data']['text']
#         print('Text updated:')
#         print(text)
#         print('***************')
#         return text

#     return False


def categorize_by_sentiment(obj_lst):
    """Runs each obj in list through a NLP API and categorizes each based on sentiment, by polarity score.

    Accepts: a list of information dicts.
    Returns: a tuple comprised of 3 lists: positive, neutral, negative.
    """
    negative = []
    neutral = []
    positive = []

    for obj in obj_lst:
        if obj['sentiment'] == 'positive':
            positive.append(obj)
        elif obj['sentiment'] == 'negative':
            negative.append(obj)
        elif obj['sentiment'] == 'neutral':
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
