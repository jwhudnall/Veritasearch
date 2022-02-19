from flask import Flask, render_template, redirect, session, flash, request, g, url_for, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Query
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import Unauthorized
from requests.exceptions import ConnectionError
from forms import UserAddForm, LoginForm
from helpers import get_search_suggestions, convert_query_string, query_twitter_v2, prune_tweets, categorize_by_sentiment
import psycopg2
import time
import os
import re

CURR_USER_KEY = 'cur_user'


uri = os.getenv("DATABASE_URL")  # or other relevant config var
if uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)

app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
#     'DATABASE_URL', 'postgresql:///veritas')
app.config['SQLALCHEMY_DATABASE_URI'] = uri

DATABASE_URL = uri
conn = psycopg2.connect(DATABASE_URL, sslmode='require')


app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = os.environ.get(
    "SECRET_KEY", "defaultsecretkeybutnotreally!")

connect_db(app)


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
    cookies = [CURR_USER_KEY, 'username',
               'headlines', 'csrf_token', 'hide_nav_search']
    for cookie in cookies:
        if cookie in session:
            session.pop(cookie)
    do_clear_search_cookies()

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


def do_clear_search_cookies():
    cookies = ['tweets', 'q_time', 'query_response', 'q', 'query']
    for cookie in cookies:
        if cookie in session:
            session.pop(cookie)


@app.errorhandler(404)
def page_not_found(e):
    search_suggestions = get_search_suggestions()
    return render_template('404.html', suggestions=search_suggestions), 404


@app.route('/')
def homepage():
    do_clear_search_cookies()

    search_suggestions = get_search_suggestions()
    return render_template('index.html', suggestions=search_suggestions)


@app.route('/search')
def handle_search():

    user = g.user if g.user else None
    query = request.args.get('query', None)

    if query:
        query = query.lower()
        new_query = Query(text=query)
        q_start_time = time.time()
        raw_tweets = query_twitter_v2(query, count=22)
    else:
        raw_tweets = None

    if raw_tweets:
        pruned_tweets = prune_tweets(
            raw_tweets, id_key="id", text_key="text")
        if pruned_tweets:
            categorized_tweets = categorize_by_sentiment(pruned_tweets)
            q_time = round(time.time() - q_start_time, 2)
        else:
            return redirect(request.referrer)

        if user:
            user_queries = [q.text for q in user.queries]
            if query not in user_queries:
                user.queries.append(new_query)
                db.session.add(user)

        db.session.add(new_query)
        db.session.commit()

        session['query'] = query
        search_suggestions = get_search_suggestions()
        return render_template('search-results.html', tweets=categorized_tweets, query=query, q_time=q_time, test_tweets=categorized_tweets, suggestions=search_suggestions)

    else:
        do_clear_search_cookies()
        flash('Nothing found. Try another term?', 'no-results')
        return redirect('/')


@app.route('/search/<query>', methods=['GET'])
def display_results(query):
    return redirect(url_for('handle_search', query=query))


@app.route('/register')
def redirect_from_register():
    flash('Please use the menu to create an account.', 'error')
    return redirect('/')


@app.route('/register', methods=["PUT", "POST"])
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


@app.route('/login', methods=['PUT', 'POST'])
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
            return redirect(f'/users/{user.id}')
        else:
            flash('Incorrect username or password.', 'error')
            return redirect(request.referrer)

    do_clear_search_cookies()
    return render_template('users/login.html', form=form)


@app.route('/login')
def redirect_from_login():
    flash('Please use the menu to login.', 'error')
    return redirect('/')


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
    search_suggestions = get_search_suggestions()

    return render_template('users/user-details.html', user=user, queries=queries, suggestions=search_suggestions)


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
    flash(f'Account successfully deleted.', 'success')
    return jsonify(msg="Account Deleted.")


@app.route('/queries/<int:query_id>', methods=['DELETE'])
def delete_query(query_id):
    """Deletes a user query. Returns confirmation message in JSON format."""
    query = Query.query.get_or_404(query_id)
    query_users = [u.id for u in query.users]
    cur_user = session.get(CURR_USER_KEY, None)

    if not cur_user or cur_user not in query_users:
        raise Unauthorized()

    q = Query.query.get_or_404(query_id)
    db.session.delete(q)
    db.session.commit()
    return jsonify(message="Query deleted")


@app.route('/privacy')
def display_privacy_policy():
    return render_template('privacy.html')


# ****************
# API
# ****************
@app.route('/api/tweets')
def fetch_tweets():
    """Retrieve tweets and return as JSON."""
    query = request.args.get('query', None)

    if query:
        formatted_query = convert_query_string(query)
        try:
            raw_tweets = query_twitter_v2(formatted_query, count=25)
        except ConnectionError:
            flash("Something went wrong. Please refresh and try again.")
            return jsonify(error="Something Went Wrong")

        if raw_tweets:
            pruned_tweets = prune_tweets(
                raw_tweets, id_key="id", text_key="text")
            categorized_tweets = categorize_by_sentiment(pruned_tweets)

            session['query'] = formatted_query
            response = jsonify(tweets=categorized_tweets)
        else:
            response = jsonify(error='no tweets found')
            do_clear_search_cookies()
    else:
        response = jsonify(error='No query args received by server')

    return response
