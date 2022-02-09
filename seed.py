"""Seed file for Project Veritas."""
from app import app
from models import db, User, Article, Like, Query, QueryUser, QueryArticle

# Need to eventually specify test database for seeding/testing

db.drop_all()
db.create_all()

# Users
u1 = User.signup(
    username='ralph67',
    password='password',
    first_name='Ralph'
)
u2 = User.signup(
    username='firstmound',
    password='password',
    first_name='James'
)
u3 = User.signup(
    username='anon0mus',
    password='password',
    first_name=None
)
u4 = User.signup(
    username='ronald',
    password='password',
    first_name='Ron'
)

db.session.add_all([u1, u2, u3, u4])
db.session.commit()

# Articles
a1 = Article(
    id="1490483269552553987",
    type='tweet',
    url='https://t.co/dAdvBiOEOy',  # "urls"['url'] (escapes removed)
    published="Mon Feb 07 00:31:17 +0000 2022",  # "created_at"
    source="George Allison",  # user['name']
    text="🚨 BREAKING NEWS | U.S. Air Force B-52 bombers will shortly be deploying to the United Kingdom. Aircraft are expected to arrive over the coming days. https://t.co/JH2kLOUYqd",
    polarity=-0.05,
    sentiment='negative'
)

a2 = Article(
    id="1491083325708304386",
    type='tweet',
    url='https://t.co/0IPqvY1YEv',
    published="Tue Feb 08 16:15:42 +0000 2022",
    source="CoinGecko",
    text="RT @coingecko: An Arizona couple’s wedding ceremony tied the knot with their digital identities on @decentraland, making it the first ever…",
    polarity=0.12,
    sentiment='positive'
)

db.session.add_all([a1, a2])
db.session.commit()

# Likes
l1 = Like(
    user_id=1,
    article_id="1490483269552553987"
)

l2 = Like(
    user_id=1,
    article_id="1491083325708304386"
)

l3 = Like(
    user_id=2,
    article_id="1490483269552553987"
)

db.session.add_all([l1, l2, l3])
db.session.commit()

# Queries

q1 = Query(
    text="bitcoin"
)

q2 = Query(
    text="'Air Force'"
)

q3 = Query(
    text="decentraland"
)

db.session.add_all([q1, q2, q3])
db.session.commit()

# queries_users
qu1 = QueryUser(
    user_id=1,
    query_id=1
)

qu2 = QueryUser(
    user_id=2,
    query_id=2
)

qu3 = QueryUser(
    user_id=3,
    query_id=3
)

db.session.add_all([qu1, qu2, qu3])
db.session.commit()

# queries_articles
qa1 = QueryArticle(
    article_id='1490483269552553987',
    query_id=2
)
qa2 = QueryArticle(
    article_id='1491083325708304386',
    query_id=2
)
qa3 = QueryArticle(
    article_id='1491083325708304386',
    query_id=3
)

db.session.add_all([qa1, qa2, qa3])
db.session.commit()
