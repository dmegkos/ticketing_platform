# Import libraries
from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Length, Email, EqualTo

# Begin implementing the forms
class IssueForm(FlaskForm): # Create form for issues
    employee_id = IntegerField('Employee ID', validators=[DataRequired()])
    category = StringField('Category', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    submit = SubmitField('Submit')

class RegistrationForm(FlaskForm): # Create form for user registration
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm): # Create form for user login
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class UpdateAccountForm(FlaskForm): # Create form to update user credentials
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Update')