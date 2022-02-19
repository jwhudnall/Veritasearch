"""Seed file for Project Veritas."""
from app import app
from models import db, User, Query, QueryUser

# Need to eventually specify test database for seeding/testing

db.drop_all()
db.create_all()

# # Users
# u1 = User.signup(
#     username='ralph67',
#     password='password',
#     first_name='Ralph'
# )
# u2 = User.signup(
#     username='firstmound',
#     password='password',
#     first_name='James'
# )
# u3 = User.signup(
#     username='anon0mus',
#     password='password',
#     first_name=None
# )
# u4 = User.signup(
#     username='ronald',
#     password='password',
#     first_name='Ron'
# )

# db.session.add_all([u1, u2, u3, u4])
# db.session.commit()

# # Queries

# q1 = Query(
#     text="bitcoin"
# )

# q2 = Query(
#     text="Air Force"
# )

# q3 = Query(
#     text="decentraland"
# )

# db.session.add_all([q1, q2, q3])
# db.session.commit()

# # queries_users
# qu1 = QueryUser(
#     user_id=1,
#     query_id=1
# )

# qu2 = QueryUser(
#     user_id=2,
#     query_id=2
# )

# qu3 = QueryUser(
#     user_id=3,
#     query_id=3
# )

# db.session.add_all([qu1, qu2, qu3])
# db.session.commit()
