# Import necessary libraries for form creation
from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, SubmitField, PasswordField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, Optional

# Form for issue creation for an employee
class IssueFormEmployee(FlaskForm): 
    # Drop-down menu for issue category selection
    category = SelectField('Category', choices=[('Hardware', 'Hardware'), ('Software', 'Software'), ('Network', 'Network'), ('Printing', 'Printing'), ('Other', 'Other')], validators=[DataRequired()])
    # Text field for issue description
    description = StringField('Description', validators=[DataRequired()])
    # Submit button for the form
    submit = SubmitField('Submit')

# Form for issue handling for support staff
class IssueFormSupport(FlaskForm): 
    # Drop-down menu for issue status update
    status = SelectField('Status', choices=[('Reported', 'Reported'), ('In Progress', 'In Progress'), ('Resolved', 'Resolved')], default='In Progress')
    # Submit button for the form
    submit = SubmitField('Submit')

# Form for new user registration
class RegistrationForm(FlaskForm): 
    # Fields for various user data
    employee_id = IntegerField('Employee ID', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone', validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired()])
    # Fields for password and its confirmation
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    # Submit button for the form
    submit = SubmitField('Sign Up')

# Form for user login
class LoginForm(FlaskForm): 
    # Fields for email and password
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    # Checkbox for remembering the user
    remember = BooleanField('Remember Me')
    # Submit button for the form
    submit = SubmitField('Login')

# Form for user account updates
class UpdateAccountForm(FlaskForm): 
    # Fields for email and password update
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('New Password', validators=[Optional()])
    confirm_password = PasswordField('Confirm New Password', validators=[EqualTo('password', message='Passwords must match')])
    # Checkbox for remembering the user
    remember = BooleanField('Remember Me')
    # Submit button for the form to update information
    submit = SubmitField('Update')
    # Button for account deletion
    delete = SubmitField('Delete Account') 