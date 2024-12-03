from flask_wtf import FlaskForm
from flask_babel import _, lazy_gettext as _l
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Regexp
from flask import request
       
class EditProfileForm(FlaskForm):
    username = StringField(_l('Username'), validators=[DataRequired()])
    about_me = TextAreaField(_l('About me'), validators=[Length(min=0, max=140)])
    submit = SubmitField(_l('Submit'))

class RecipeForm(FlaskForm):
    title = StringField(_l('Title'), validators=[DataRequired()])
    submit = SubmitField(_l('Submit'))

class IngredientForm(FlaskForm):
    description = StringField(_l('Ingredient'), validators=[DataRequired()])
    quantity = StringField(_l('Quantity'), validators=[Regexp(regex='^[0-9]*$', message='Enter a valid quantity')])
    unit = StringField(_l('Unit'))
    submit = SubmitField(_l('Add'))

class RecipeMethodForm(FlaskForm):
    method = TextAreaField(_l('Method'), validators=[Length(min=0, max=1024)])
    submit = SubmitField(_l('Submit'))

class SearchForm(FlaskForm):
    q = StringField(_l('Search'), validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args
        if 'meta' not in kwargs:
            kwargs['meta'] = {'csrf': False}
        super(SearchForm, self).__init__(*args, **kwargs)
