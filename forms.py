from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, FloatField
from wtforms.validators import DataRequired, Email, Length


class SearchPokemonForm(FlaskForm):

    poke_name = StringField("Search by Name")
    poke_number = FloatField("Search by Number")

class UserAddForm(FlaskForm):
    """Form for adding users."""

    username = StringField('Trainer ID', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[Length(min=6)])


class LoginForm(FlaskForm):
    """Login form."""

    username = StringField('Trainer ID', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])

class UserEditForm(FlaskForm):
    """Form for editing/updating user information"""
        
    username = StringField('Trainer ID', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[Length(min=6)])
              