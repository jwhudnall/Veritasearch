"""Tests for Project Veritas Models."""

import os
from unittest import TestCase
from models import db, User, Article, Query, QueryUser, QueryArticle

os.environ['DATABASE_URL'] = "postgresql:///veritas-test"
from app import app


class ModelsTestCase(TestCase):
    """Test User Model."""

    def setUp(self):
        db.drop_all()
        db.create_all()

        u1 = User.signup(
            username='Johnny96',
            password='password',
            first_name='John'
        )

        q1 = Query(text="tesla")

        a1 = Article(
            id="1490483269552553987",
            text="🚨 BREAKING NEWS | U.S. Air Force B-52 bombers will shortly be deploying to the United Kingdom. Aircraft are expected to arrive over the coming days. https://t.co/JH2kLOUYqd",
            sentiment='negative',
            polarity=-0.05,
            embed_html='<blockquote class="twitter-tweet"><p lang="en" dir="ltr">&lt;THREAD&gt; <br>LESS-REDACTED MUELLER REPORT DROPPED.<br><br>Let&#39;s see what they revealed with A/B comparisons! Starting with ROGER STONE. <a href="https://t.co/gYn2gEKWkS">pic.twitter.com/gYn2gEKWkS</a></p>&mdash; Eric Garland (@ericgarland) <a href="https://twitter.com/ericgarland/status/1492266696333307919?ref_src=twsrc%5Etfw">February 11, 2022</a></blockquote>\n',
            timestamp="Mon Feb 07 00:31:17 +0000 2022"
        )

        db.session.add_all([q1, a1])
        db.session.commit()

        self.user = u1
        self.query = q1
        self.article = a1

    def tearDown(self) -> None:
        db.session.rollback()

    def test_user_model(self):

        self.user.queries.append(self.query)
        db.session.add(self.user)
        db.session.commit()

        user_queries = QueryUser.query.all()
        self.assertEqual(len(user_queries), 1)
        self.assertIsInstance(self.user, User)

    def test_article_model(self):
        self.assertEqual(len(QueryArticle.query.all()), 0)
        self.article.queries.append(self.query)

        db.session.add(self.article)
        db.session.commit()

        article_queries = QueryArticle.query.all()
        self.assertEqual(len(article_queries), 1)
        self.assertIsInstance(self.article, Article)

    def test_query_model(self):
        query = Query(text="Top News")
        self.user.queries.append(query)

        db.session.add_all([query, self.user])
        db.session.commit()

        self.assertEqual(len(Query.query.all()), 2)
        self.assertEqual(len(self.user.queries), 1)
        self.assertEqual(len(QueryUser.query.all()), 1)
