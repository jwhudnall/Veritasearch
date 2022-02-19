"""Helper Functions for Project Veritas"""

import random
from flask import flash
from models import Query
import requests


def get_search_suggestions():
    """Returns a list of 3 options from a pre-defined topic list."""
    q_list = ['Tesla', 'Politics', 'Russia Ukraine', 'Donald Trump',
              'Joe Biden', 'Global Warming', 'Stock Market', 'Joe Rogan', 'Cancel Culture', 'Vaccine', 'Inflation', 'Bitcoin', 'Taylor Swift', 'Cybersecurity', 'Financial Independence']
    random.shuffle(q_list)
    return q_list[:3]


def convert_query_string(query):
    """Converts a string with comma-separated values into a query-formatted string of random terms.

    If query contains more than 2 values, the selection is randomized.
    """

    q_split = query.split(',')
    if len(q_split) == 1:
        formatted_query = q_split[0]
    elif len(q_split) == 2:
        formatted_query = f'({q_split[0]} OR {q_split[1]})'
    else:
        first = random.choice(q_split)
        q_split.remove(first)
        second = random.choice(q_split)
        q_split.remove(second)
        third = random.choice(q_split)
        formatted_query = f'({first} OR {second} OR {third})'

    return formatted_query


def query_twitter_v2(q, count=10):
    base_url = 'https://api.twitter.com/2/tweets/search/recent'
    headers = {'Authorization': f'Bearer {BEARER_TOKEN}'}
    add_flags = ' is:verified lang:en -is:retweet'
    q += add_flags
    print(f'Query url-encoded: {q}')
    params = {
        'query': q,
        'max_results': count
    }
    res = requests.get(f'{base_url}', headers=headers,
                       params=params)

    data = res.json()
    raw_tweets = data.get('data', None)
    if raw_tweets:
        print(f'Total v2 results found: {len(raw_tweets)}')
        return raw_tweets
    return False


def prune_tweets(raw_tweets, id_key, text_key):
    """Aggregates desired fields from each raw tweet response. Returns a list of pruned tweets.

    Keys to be returned: id, polarity, sentiment
    """
    unassigned_tweets = []

    for tweet in raw_tweets:
        try:
            cur_tweet = {
                "id": tweet[id_key],
                "text": tweet[text_key]
            }
        except KeyError:
            flash('It appears the Twitter API has changed its key-value pairs.', 'error')
            return False
        try:
            sentiment = query_sentim_API(cur_tweet["text"])
            cur_tweet["polarity"] = sentiment.get("polarity")
            cur_tweet["sentiment"] = sentiment.get("type").title()
        except:
            # Case where Sentim API is down
            cur_tweet["polarity"] = round(((random.random() * 2) - 1), 2)
            cur_tweet["sentiment"] = 'API Issue'

        del cur_tweet['text']

        unassigned_tweets.append(cur_tweet)

    return unassigned_tweets


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
        else:
            choice = random.choice([positive, negative, neutral])
            choice.append(obj)

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

##################
# Unused Functions
##################


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
