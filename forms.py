"""Forms for Project Veritas"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import Length, InputRequired, Optional


class UserAddForm(FlaskForm):
    """Form for adding users."""

    first_name = StringField(
        'First Name', validators=[Optional(), Length(min=1, max=50)])
    username = StringField('Username', validators=[
                           InputRequired(), Length(min=1, max=50)])
    password = PasswordField('Password', validators=[Length(
        min=6, max=100, message='Password should be at least 6 characters.')])


class LoginForm(FlaskForm):
    """Login form."""

    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])
