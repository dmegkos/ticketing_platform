# Import libraries
from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, SubmitField, PasswordField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, Optional

# Begin implementing the forms
class IssueFormEmployee(FlaskForm): # Create form for issues as an employee
    category = SelectField('Category', choices=[('Hardware', 'Hardware'), ('Software', 'Software'), ('Network', 'Network'), ('Printing', 'Printing'), ('Other', 'Other')], validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    submit = SubmitField('Submit')

class IssueFormSupport(FlaskForm): # Create form for issues as support staff
    status = SelectField('Status', choices=[('Reported', 'Reported'), ('In Progress', 'In Progress'), ('Resolved', 'Resolved')], default='In Progress')
    submit = SubmitField('Submit')

class RegistrationForm(FlaskForm): # Create form for user registration
    employee_id = IntegerField('Employee ID', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone', validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm): # Create form for user login
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class UpdateAccountForm(FlaskForm): # Create form to update user credentials
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('New Password', validators=[Optional()])
    confirm_password = PasswordField('Confirm New Password', validators=[EqualTo('password', message='Passwords must match')])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Update')
    delete = SubmitField('Delete Account')