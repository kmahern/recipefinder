from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, ValidationError, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Regexp
import sqlalchemy as sa
from app import db
from app.models import User
from flask import request
       
class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')

class RecipeForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    submit = SubmitField('Submit')

class IngredientForm(FlaskForm):
    description = StringField('Ingredient', validators=[DataRequired()])
    quantity = StringField('Quantity', validators=[Regexp(regex='^[0-9]*$', message='Enter a valid quantity')])
    unit = StringField('Unit')
    submit = SubmitField('Add')

class RecipeMethodForm(FlaskForm):
    method = TextAreaField('Method', validators=[Length(min=0, max=1024)])
    submit = SubmitField('Submit')

class SearchForm(FlaskForm):
    q = StringField('Search', validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args
        if 'meta' not in kwargs:
            kwargs['meta'] = {'csrf': False}
        super(SearchForm, self).__init__(*args, **kwargs)
