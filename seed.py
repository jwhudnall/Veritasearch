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
    text="🚨 BREAKING NEWS | U.S. Air Force B-52 bombers will shortly be deploying to the United Kingdom. Aircraft are expected to arrive over the coming days. https://t.co/JH2kLOUYqd",
    sentiment='negative',
    polarity=-0.05,
    embed_html='<blockquote class="twitter-tweet"><p lang="en" dir="ltr">&lt;THREAD&gt; <br>LESS-REDACTED MUELLER REPORT DROPPED.<br><br>Let&#39;s see what they revealed with A/B comparisons! Starting with ROGER STONE. <a href="https://t.co/gYn2gEKWkS">pic.twitter.com/gYn2gEKWkS</a></p>&mdash; Eric Garland (@ericgarland) <a href="https://twitter.com/ericgarland/status/1492266696333307919?ref_src=twsrc%5Etfw">February 11, 2022</a></blockquote>\n',
    timestamp="Mon Feb 07 00:31:17 +0000 2022"
)


a2 = Article(
    id="1491083325708304386",
    text="RT @coingecko: An Arizona couple’s wedding ceremony tied the knot with their digital identities",
    sentiment='positive',
    polarity=0.12,
    embed_html='<blockquote class="twitter-tweet"><p lang="en" dir="ltr">&lt;THREAD&gt; <br>LESS-REDACTED MUELLER REPORT DROPPED.<br><br>Let&#39;s see what they revealed with A/B comparisons! Starting with ROGER STONE. <a href="https://t.co/gYn2gEKWkS">pic.twitter.com/gYn2gEKWkS</a></p>&mdash; Eric Garland (@ericgarland) <a href="https://twitter.com/ericgarland/status/1492266696333307919?ref_src=twsrc%5Etfw">February 11, 2022</a></blockquote>\n',
    timestamp="Tue Feb 08 16:15:42 +0000 2022"
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
    text="Air Force"
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
