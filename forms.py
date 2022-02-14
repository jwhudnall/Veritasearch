"""Forms for Project Veritas"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import Length, InputRequired


# class SearchForm(FlaskForm):
#     """User search form."""

#     search = StringField('Search', validators=[
#                          InputRequired(), Length(min=3, max=25)])


class UserAddForm(FlaskForm):
    """Form for adding users."""

    first_name = StringField(
        'First Name', validators=[InputRequired(), Length(min=1, max=50)])
    username = StringField('Username', validators=[
                           InputRequired(), Length(min=1, max=50)])
    password = PasswordField('Password', validators=[Length(min=6)])


class LoginForm(FlaskForm):
    """Login form."""

    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])
