"""SQLAlchemy models for Project Veritas."""

from datetime import datetime
from enum import auto
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask import flash

bcrypt = Bcrypt()
db = SQLAlchemy()


def connect_db(app):
    """Connect to database."""
    db.app = app
    db.init_app(app)


class User(db.Model):
    """User Model."""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)

    first_name = db.Column(db.String(50))
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)

    liked_articles = db.relationship('Article', secondary='likes',
                                     backref='liked_users')

    def __repr__(self):
        return f"<User #{self.id}: {self.username}>"

    @classmethod
    def signup(cls, username, password, first_name):
        """Sign up user."""

        hashed_pw = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            password=hashed_pw,
            first_name=first_name
        )

        db.session.add(user)
        db.session.commit()
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Authenticate user by 'username' and 'password'.

        If username and password match, user object is returned. Otherwise, returns False.
        """
        user = cls.query.filter_by(username=username).first()

        if user:
            has_valid_pw = bcrypt.check_password_hash(user.password, password)
            if has_valid_pw:
                return user
        flash('Invalid credentials.')
        return False


class Article(db.Model):
    """Article Model."""

    __tablename__ = 'articles'

    id = db.Column(db.String(25), primary_key=True)
    type = db.Column(db.String(10), nullable=False)
    url = db.Column(db.Text, nullable=False)
    published = db.Column(db.DateTime, nullable=False)
    source = db.Column(db.String(50), nullable=False)
    text = db.Column(db.Text, nullable=False)
    polarity = db.Column(db.Numeric(precision=3, scale=2), nullable=False)
    sentiment = db.Column(db.String(15), nullable=False)

    queries = db.relationship(
        'Query', secondary='queries_articles', backref='articles')

    def like_count(self):
        return len(self.liked_users)

    # Define published_pretty format method


class Like(db.Model):
    """Maps user likes to articles."""

    __tablename__ = 'likes'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey(
        'users.id', ondelete='cascade'), primary_key=True)
    article_id = db.Column(db.String(25), db.ForeignKey(
        'articles.id', ondelete='cascade'), primary_key=True)


class Query(db.Model):
    """Query model."""

    __tablename__ = 'queries'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    text = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False,
                          default=datetime.utcnow())


class QueryUser(db.Model):
    """Maps queries to users."""

    __tablename__ = 'queries_users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey(
        'users.id', ondelete='cascade'), primary_key=True)
    query_id = db.Column(db.Integer, db.ForeignKey(
        'queries.id', ondelete='cascade'), primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False,
                          default=datetime.utcnow())


class QueryArticle(db.Model):
    """Maps queries to articles."""

    __tablename__ = 'queries_articles'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    article_id = db.Column(db.String(25), db.ForeignKey(
        'articles.id', ondelete='cascade'), primary_key=True)
    query_id = db.Column(db.Integer, db.ForeignKey(
        'queries.id', ondelete='cascade'), primary_key=True)
