"""SQLAlchemy models for Project Veritas."""

from datetime import datetime
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

    queries = db.relationship(
        'Query', secondary='queries_users', backref='users')

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


class Query(db.Model):
    """Query model."""

    __tablename__ = 'queries'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    text = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False,
                          default=datetime.utcnow())

    def __repr__(self):
        return f"<Query #{self.id}: {self.text}>"

    def serialize(self):
        return {
            'id': self.id,
            'text': self.text,
            'timestamp': self.timestamp
        }


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
