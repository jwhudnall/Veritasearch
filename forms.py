"""Forms for Project Veritas"""
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import Length, InputRequired


class SearchForm(FlaskForm):
    """User search form."""

    search = StringField('Search', validators=[
                         InputRequired(), Length(min=3, max=25)])
