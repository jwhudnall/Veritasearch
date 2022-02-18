"""Tests for Project Veritas Models."""

import os
from unittest import TestCase
from models import db, User, Query, QueryUser

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

        db.session.add(q1)
        db.session.commit()

        self.user = u1
        self.query = q1

    def tearDown(self) -> None:
        db.session.rollback()

    def test_user_model(self):
        self.user.queries.append(self.query)
        db.session.add(self.user)
        db.session.commit()

        user_queries = QueryUser.query.all()
        self.assertEqual(len(user_queries), 1)
        self.assertIsInstance(self.user, User)

    def test_query_model(self):
        query = Query(text="Top News")
        self.user.queries.append(query)

        db.session.add_all([query, self.user])
        db.session.commit()

        self.assertEqual(len(Query.query.all()), 2)
        self.assertEqual(len(self.user.queries), 1)
        self.assertEqual(len(QueryUser.query.all()), 1)
