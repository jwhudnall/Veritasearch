"""Tests for Project Veritas routes."""

import os
from unittest import TestCase
from models import db, User, Query, QueryUser
from flask import g

os.environ['DATABASE_URL'] = "postgresql:///veritas-test"
from app import app, CURR_USER_KEY
app.config['TESTING'] = True

app.config['WTF_CSRF_ENABLED'] = False


class RoutesTestCase(TestCase):
    """Test views for primary routes."""

    def setUp(self):
        db.drop_all()
        db.create_all()

        self.client = app.test_client()
        self.user1 = User.signup(
            username='Johnny96',
            password='password',
            first_name='John'
        )
        self.user1.id = 1

        self.user2 = User.signup(
            username='JoeMontana',
            password='password',
            first_name='Joe'
        )
        self.user2.id = 2

        self.query1 = Query(text="tesla")
        db.session.add(self.query1)
        db.session.commit()
        self.query1.id = 1

    def tearDown(self) -> None:
        db.session.rollback()

    def test_root_route_logged_in(self):
        """Check main page with user logged in."""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id
                sess['username'] = self.user1.username

            res = c.get('/')
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('Veritas', html)
            self.assertIn('<input type="text"', html)
            self.assertIn(self.user1.username, html)

    def test_root_route_logged_out(self):
        """Check main page with no user logged in."""
        with self.client as c:
            res = c.get('/')
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('Veritas', html)
            self.assertIn('<input type="text"', html)
            self.assertNotIn(self.user1.username, html)

    def test_user_profile_authorized(self):
        """Check user profile page."""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id
                sess['username'] = self.user1.username
                g.user = User.query.get(sess[CURR_USER_KEY])

            res = c.get(f'/users/{self.user1.id}')
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('Welcome,', html)

            # verify user cannot view other peoples profiles
    def test_user_profile_unauthorized(self):
        """Check user profile page."""
        another_user_id = 15
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id
                sess['username'] = self.user1.username
                g.user = User.query.get(sess[CURR_USER_KEY])

            res = c.get(f'/users/{another_user_id}')

            self.assertEqual(res.status_code, 302)

    def test_delete_query_wrong_user(self):
        """Verify user cannot delete another user's query."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id
                sess['username'] = self.user1.username
                g.user = User.query.get(sess[CURR_USER_KEY])

            res = c.delete('/queries/1')

            self.assertEqual(res.status_code, 401)

    def test_delete_query_no_user(self):
        """Verify that no logged user cannot delete another user's query."""
        with self.client as c2:
            res2 = c2.delete(f'/queries/1')
            self.assertEqual(res2.status_code, 401)

    def test_delete_account_other_user(self):
        """Verify user cannot delete another user's account."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id
                sess['username'] = self.user1.username
                g.user = User.query.get(sess[CURR_USER_KEY])

            res = c.delete('/users/2', follow_redirects=True)
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn(self.user1.username, html)

    def test_delete_account_unknown(self):
        """Verify that no logged user cannot delete another user's account."""

        with self.client as c:

            res = c.delete('/users/1')
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 401)
            self.assertIn('Unauthorized', html)
