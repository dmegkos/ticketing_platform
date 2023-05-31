# Import necessary libraries
import random # for generating random numbers
# flask for creating the web application
# abort, render_template, request, redirect, url_for, flash from flask for handling various web requests and responses
from flask import Flask, abort, render_template, request, redirect, url_for, flash
# CSRFProtect from flask_wtf for CSRF protection
from flask_wtf import CSRFProtect
# SQLAlchemy from flask_sqlalchemy for database handling
from flask_sqlalchemy import SQLAlchemy
# UserMixin, LoginManager, login_user, current_user, logout_user, login_required from flask_login for user authentication and session management
from flask_login import UserMixin, LoginManager, login_user, current_user, logout_user, login_required
# IssueFormEmployee, IssueFormSupport, RegistrationForm, LoginForm, UpdateAccountForm from forms are custom forms for handling user input
from forms import IssueFormEmployee, IssueFormSupport, RegistrationForm, LoginForm, UpdateAccountForm
# generate_password_hash, check_password_hash from werkzeug.security for handling password hashing and verification
from werkzeug.security import generate_password_hash, check_password_hash
# os for interacting with the operating system
import os

# Setting up the Flask application
# Initialize flask application
app = Flask(__name__)
# Setup configurations for SQLAlchemy. Here we provide the connection string for the postgresql database.
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://ticketing_user:qwerty123@db/ticketing_system'
# We set this to False to disable signalling the application every time a change is about to be made in the database.
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Default view to redirect to when the user needs to log in
app.config['LOGIN_VIEW'] = 'login'
# Generate a secret key for our application. This is used by Flask to handle sessions securely.
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY
# Initialize CSRF protection for our application
csrf = CSRFProtect()
# Initialize SQLAlchemy to connect to the database
db = SQLAlchemy(app)
# Initialize Login Manager for handling user sessions
login_manager = LoginManager(app)
# Setup Flask app within login manager
login_manager.init_app(app)
# Setup CSRF protection within our Flask application
csrf.init_app(app)
# Specify the name of the view to redirect to when the user needs to log in.
login_manager.login_view = 'login'


# Define the models for the database based on the schema

# Employee Model corresponding to the 'employees' table in the database
class Employee(db.Model):
    # Specify the name of the table
    __tablename__ = 'employees'
    
    # Define columns in the table
    # employee_id is the primary key
    employee_id = db.Column(db.Integer, primary_key=True)
    # name, email, phone, location are required fields and cannot be null. Email is a unique field
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    phone = db.Column(db.String(15), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    
    # Define relationship with the issues table
    # Here, a one-to-many relationship is established with the Issue model (one employee can have many issues)
    # The 'backref' attribute is used to access the Employee model from the Issue model (i.e., issue.employee)
    # 'lazy=True' enables lazy loading, which means SQLAlchemy will only load the data as necessary
    # 'cascade="all, delete-orphan"' means all changes including delete will propagate to the related objects (issues in this case)
    issues = db.relationship('Issue', backref='employee', lazy=True, cascade="all, delete-orphan")


# Issue Model corresponding to the 'issues' table in the database
class Issue(db.Model):
    # Specify the name of the table
    __tablename__ = 'issues'
    
    # Define columns in the table
    # issue_id is the primary key
    issue_id = db.Column(db.Integer, primary_key=True)
    # employee_id is a foreign key linked to the 'employees.employee_id'
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.employee_id'), nullable=False)
    # employee_name, employee_email, location, category, description are required fields and cannot be null
    employee_name = db.Column(db.String(100), nullable=False)
    employee_email = db.Column(db.String(120), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    # status is a required field with default value 'Reported'
    status = db.Column(db.String(50), nullable=False, default='Reported')
    # support_name is an optional field
    support_name = db.Column(db.String(100))


# SupportStaff Model corresponding to the 'support_staff' table in the database
class SupportStaff(db.Model):
    # Specify the name of the table
    __tablename__ = 'support_staff'
    
    # Define columns in the table
    # support_id is the primary key
    support_id = db.Column(db.Integer, primary_key=True)
    # name, email are required fields and cannot be null. Email is a unique field
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)


# Users Model to manage user login, inheriting from UserMixin and db.Model
# UserMixin is a default implementation for user authentication provided by Flask-Login
class Users(UserMixin, db.Model):
    # Specify the name of the table
    __tablename__ = 'users'
    
    # Define columns in the table
    # id is the primary key
    id = db.Column(db.Integer, primary_key=True)
    # email is a unique field and cannot be null
    email = db.Column(db.String(120), unique=True, nullable=False)
    # password cannot be null
    password = db.Column(db.String(120), nullable=False)


# This function is used to determine the type of user based on the email
def get_user_type(email):
    # Check if the provided email belongs to an Employee
    # If an Employee with this email exists in the database, return 'employee'
    if Employee.query.filter_by(email=email).first():
        return 'employee'
    # Check if the provided email belongs to a Support Staff member
    # If a Support Staff with this email exists in the database, return 'support'
    elif SupportStaff.query.filter_by(email=email).first():
        return 'support'
    # If the provided email does not belong to either an Employee or a Support Staff member, return None
    return None

# This function is a callback function used by Flask-Login's user_loader decorator. 
# Flask-Login uses this function behind the scenes to load the user from the session
@login_manager.user_loader
def load_user(user_id):
    # It queries the Users table using the user_id and returns the User object
    # If a user with the provided id doesn't exist in the database, it returns None.
    return Users.query.get(int(user_id))


# Define a Flask route for the home page of the application
@app.route('/') 
@login_required # Decorator to ensure that the user is authenticated before they can access the home page
def home():
    # Get the type of the user (employee or support staff)
    user_type = get_user_type(current_user.email)
    # Render the home.html template and pass the user_type to it
    return render_template('home.html', user_type=user_type)

# Define a Flask route for the issues page of the application, accessible only to helpdesk staff
@app.route('/issues') 
@login_required # Decorator to ensure that the user is authenticated before they can access the issues page
def all_issues():
    # Query the SupportStaff table to find a support staff member with the current user's email
    support_staff = SupportStaff.query.filter_by(email=current_user.email).first()
    # Get the type of the user (employee or support staff)
    user_type = get_user_type(current_user.email)
    # If the current user is not a support staff member, they are not allowed to access the issues page
    if not support_staff:
        # Show a flash message to the user stating they don't have the necessary permissions to view the page
        flash('You do not have the necessary permissions to view this page.', 'danger')
        # Redirect the user to the home page
        return redirect(url_for('home'))
    # If the user is a support staff member, query all issues from the Issue table
    issues = Issue.query.all()
    # Render the issues.html template, passing in the list of issues and the user_type to it
    return render_template('issues.html', issues=issues, user_type=user_type)

# Define a Flask route for the personal issues page of an employee
@app.route('/my_issues') 
@login_required # Decorator to ensure that the user is authenticated before they can access their personal issues page
def my_issues():
    # Get the type of the user (employee or support staff)
    user_type = get_user_type(current_user.email)
    # If the current user is not an employee, they are not allowed to access the my_issues page
    if user_type != 'employee':
        # Show a flash message to the user stating they don't have the necessary permissions to view the page
        flash('You do not have the necessary permissions to view this page.', 'danger')
        # Redirect the user to the home page
        return redirect(url_for('home'))
    # Query the Issue table to get all issues reported by the current user
    issues = Issue.query.filter_by(employee_email=current_user.email).all() 
    # Render the issues.html template, passing in the list of issues and the user_type to it
    return render_template('issues.html', issues=issues, user_type=user_type)

# Define a Flask route for an individual issue page
@app.route('/issues/<int:issue_id>', methods=['GET', 'POST']) 
@login_required # Decorator to ensure that the user is authenticated before they can access an individual issue page
def issue(issue_id):
    # Query the Issue table to get the issue with the provided issue_id or return a 404 error if not found
    issue = Issue.query.get_or_404(issue_id)
    # Get the type of the user (employee or support staff)
    user_type = get_user_type(current_user.email)
    # If the current user is neither the reporting employee of the issue nor a support staff, they are not allowed to access the page
    if (current_user.email != issue.employee_email) and (user_type != 'support'):
        # Abort with a 403 error
        abort(403)
    # Render the issue.html template, passing in the issue and the user_type to it
    return render_template('issue.html', issue=issue, user_type=user_type)


# Define a Flask route for creating a new issue
@app.route('/issue/new', methods=['GET', 'POST']) 
@login_required # Decorator to ensure that the user is authenticated before they can create a new issue
def add_issue():
    # Get the type of the user (employee or support staff)
    user_type = get_user_type(current_user.email)
    # If the current user is not an employee, they are not allowed to create a new issue
    if user_type != 'employee':
        # Abort with a 403 error
        abort(403)
    # Create a new form object from the IssueFormEmployee class
    form = IssueFormEmployee()
    # Check if the form data is valid when the form is submitted
    if form.validate_on_submit():
        # Query the SupportStaff table to get all support staff names
        support_staff_names = SupportStaff.query.with_entities(SupportStaff.name).all()
        # Select a support staff at random
        random_support_name = random.choice(support_staff_names)
        # Query the Employee and Users tables to get the employee id, name, location, and email of the current user
        employee_info = db.session.query(Employee.employee_id, Employee.location, Employee.name, Employee.email)\
                      .join(Users, Employee.email == Users.email)\
                      .filter(Users.email == current_user.email).first()
        # Create a new Issue object with the form data and the information obtained above
        issue = Issue(
            employee_id = employee_info.employee_id,
            employee_name = employee_info.name,
            employee_email = employee_info.email,
            location = employee_info.location,
            category=form.category.data,
            description=form.description.data,
            support_name=random_support_name[0],
        )
        # Add the new issue to the database session
        db.session.add(issue)
        # Commit the changes to the database
        db.session.commit()
        # Redirect the user to the issue page for the newly created issue
        return redirect(url_for('issue', issue_id=issue.issue_id))
    # Render the add_issue.html template, passing in the form and the user_type to it
    return render_template('add_issue.html', title='New Issue', form=form, user_type=user_type)

# Define a Flask route for updating an issue
@app.route('/issue/<int:issue_id>/update', methods=['GET', 'POST'])
@login_required
def update_issue(issue_id):
    # Get the issue from the database
    issue = Issue.query.get_or_404(issue_id)
    # Get the user type of the current user
    user_type = get_user_type(current_user.email)
    # Verify if the user is the one who created the issue or a support user, else abort
    if (current_user.email != issue.employee_email) and (user_type != 'support'):
        abort(403)    
    # If the user is an employee, use the IssueFormEmployee form
    if user_type == 'employee':
        form = IssueFormEmployee()
    # If the user is a support user, use the IssueFormSupport form
    elif user_type == 'support':
        form = IssueFormSupport()
    else:
        abort(403)  # or handle this case as needed
    # Check if the form is submitted and validate the form inputs
    if form.validate_on_submit():
        # If user is an employee, update the issue category and description
        if user_type == 'employee':
            issue.category = form.category.data
            issue.description = form.description.data
        # If user is a support user, update the issue status and the support user's name
        elif user_type == 'support':
            support_user = SupportStaff.query.join(Users, Users.email == SupportStaff.email).filter(Users.email == current_user.email).first()
            issue.status = form.status.data
            issue.support_name = support_user.name
        # Save changes to database
        db.session.commit()
        # Show a success message
        flash('Issue has been updated!', 'success')
        # Redirect the user to the updated issue page
        return redirect(url_for('issue', issue_id=issue.issue_id))
    # If a GET request, pre-populate the form fields with existing issue data
    elif request.method == 'GET':
        if user_type == 'employee':
            form.category.data = issue.category
            form.description.data = issue.description
        elif user_type == 'support' and issue.status:
            form.status.data = issue.status
    # Render the update_issue.html template, passing in the form and user_type
    return render_template('update_issue.html', title='Update Issue', form=form, user_type=user_type)

# Define a Flask route for deleting an issue
@app.route('/issue/<int:issue_id>/delete', methods=['POST'])
@login_required
def delete_issue(issue_id):
    # Get the issue to be deleted
    issue = Issue.query.get_or_404(issue_id)
    # Check if the current user is the one who created the issue, else abort
    if current_user.email != issue.employee_email:
        abort(403)
    # Delete the issue from the database
    db.session.delete(issue)
    # Save changes to the database
    db.session.commit()
    # Show a success message
    flash('Your issue has been deleted!', 'success')
    # Redirect the user to their issues page
    return redirect(url_for('my_issues'))

# Define Flask route for user registration
@app.route('/register', methods=['GET', 'POST']) # route for user registration
def register():
    # Redirect the user to the home page if they're already authenticated
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    # Create an instance of the RegistrationForm
    form = RegistrationForm()
    # If form is submitted and validated
    if form.validate_on_submit():
        # Check if the employee ID or email is already registered
        employee_id = Employee.query.filter_by(employee_id=form.employee_id.data).first()
        employee_email = Employee.query.filter_by(email=form.email.data).first()
        support_email = SupportStaff.query.filter_by(email=form.email.data).first()
        if employee_id:
            # If the employee ID is taken, show a message and redirect to the registration page
            flash('That employee ID is taken. Please choose a different one.', 'danger')
            return redirect(url_for('register'))
        if employee_email or support_email:
            # If the email is taken, show a message and redirect to the registration page
            flash('That email is taken. Please choose a different one.', 'danger')
            return redirect(url_for('register'))
        # Generate a hashed version of the password
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        # Create a new user and employee with the form data
        user = Users(email=form.email.data, password=hashed_password)
        employee = Employee(employee_id=form.employee_id.data, name=form.name.data, email=form.email.data, phone=form.phone.data, location=form.location.data)
        # Add the new user and employee to the database
        db.session.add(user)
        db.session.add(employee)
        db.session.commit()
        # Show a success message
        flash('Your account has been created! You are now able to log in', 'success')
        # Redirect to the next page or home page if no next page is specified
        next_page = request.args.get('next')
        return redirect(next_page) if next_page else redirect(url_for('home'))
    # Render the registration form
    return render_template('register.html', title="Register", form=form)

# Define Flask route for user log in
@app.route('/login', methods=['GET', 'POST']) # route for user login
def login():
    # If user is already authenticated, redirect to their corresponding pages
    if current_user.is_authenticated:
        user_type = get_user_type(current_user.email)
        if user_type == 'employee':
            return redirect (url_for('my_issues')) # employees are directed to 'my_issues' page
        elif user_type == 'support':
            return redirect(url_for('all_issues')) # support staff are directed to 'all_issues' page
    # Instantiate the LoginForm
    form = LoginForm()
    # If form is submitted and validated
    if form.validate_on_submit():
        # Query for user using email
        user = Users.query.filter_by(email=form.email.data).first()
        # If user exists and password is correct
        if user and check_password_hash(user.password, form.password.data):
            # Log the user in
            login_user(user, remember=form.remember.data)
            # Get the next page the user was trying to access before login
            next_page = request.args.get('next')
            # Determine the user type
            user_type = get_user_type(user.email)
            # Redirect user to their corresponding pages
            if user_type == 'employee':
                return redirect(next_page) if next_page else redirect(url_for('my_issues'))
            elif user_type == 'support':
                return redirect(next_page) if next_page else redirect(url_for('all_issues'))
        else:
            # If login is unsuccessful, flash a danger message
            flash('Login Unsuccessful. Please check email and password', 'danger')
    # Render the login form
    return render_template('login.html', title='Login', form=form)

# Define Flask route for account page
@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    # Determine the type of the user
    user_type = get_user_type(current_user.email)    
    # Instantiate a form object
    form = UpdateAccountForm()    
    # Process form submissions
    if form.validate_on_submit():
        # Check which button the user clicked
        if request.form.get('action') == 'delete':  # If user chose to delete their account
            if user_type == 'employee':
                # Fetch the corresponding Employee record
                employee_user = Employee.query.filter_by(email=current_user.email).first()
                if employee_user:
                    # Delete the Employee record
                    db.session.delete(employee_user)
            # Delete the User record
            db.session.delete(current_user)
            db.session.commit()
            flash('Your account has been deleted.', 'success')
            return redirect(url_for('login'))  # Redirect to the login page
        elif request.form.get('action') == 'update':  # If user chose to update their account
            # Check if the new email is already used by another user
            user_with_same_email = Users.query.filter_by(email=form.email.data).first()
            if user_with_same_email and (user_with_same_email.id != current_user.id):
                flash('Email is already in use. Please choose a different one.', 'danger')
            else:
                # If the user has entered a new password, hash it and store it
                if form.password.data:
                    current_user.password = generate_password_hash(form.password.data, method='sha256')
                old_email = current_user.email
                current_user.email = form.email.data  # Update the email of the User record
                if user_type == 'employee':
                    # Fetch the corresponding Employee record
                    employee_user = Employee.query.filter_by(email=old_email).first()
                    if employee_user:
                        # Update the email of the Employee record
                        employee_user.email = form.email.data
                        # Update the employee_email field of all issues reported by this employee
                        issues_to_update = Issue.query.filter_by(employee_email=old_email).all()
                        for issue in issues_to_update:
                            issue.employee_email = form.email.data
                elif user_type == 'support':
                    # Fetch the corresponding SupportStaff record
                    support_user = SupportStaff.query.filter_by(email=old_email).first()
                    if support_user:
                        # Update the email of the SupportStaff record
                        support_user.email = form.email.data
                db.session.commit()
                flash('Your account has been updated!', 'success')
            return redirect(url_for('account'))  # Redirect to the account page
    elif request.method == 'GET':  # Pre-fill the form
        form.email.data = current_user.email    
    # Render the page
    return render_template('account.html', title='Account', form=form, user_type=user_type)

# Define Flask route for the about page
@app.route('/about')
@login_required  # Only authenticated users can access this route
def about():
    # Determine the type of the current user
    user_type = get_user_type(current_user.email)
    # Render the about page, passing the user type to the template
    return render_template('about.html', user_type=user_type)

# Define Flask route for the logout action
@app.route('/logout')
@login_required  # Only authenticated users can perform this action
def logout():
    # Log out the current user
    logout_user()
    # Redirect to the login page
    return redirect(url_for('login'))


if __name__ == "__main__":
    # Ensure the Flask application instance runs in the context
    with app.app_context():
        # Create the database tables based on SQLAlchemy models (if they don't exist)
        db.create_all()      
        # Check if the admin user already exists in the Users table
        admin_user = Users.query.filter_by(email="admin@email.com").first()
        # Check if the admin support staff already exists in the SupportStaff table
        admin_staff = SupportStaff.query.filter_by(email="admin@email.com").first()
        # If the admin user does not exist in the Users table
        if admin_user is None:
            # Hash the password "qwer1234" using the generate_password_hash function
            hashed_password = generate_password_hash("qwer1234")
            # Create a new Users instance for the admin user
            admin_user = Users(email="admin@email.com", password=hashed_password)
            # Add the new user to the session
            db.session.add(admin_user)
        # If the admin support staff does not exist in the SupportStaff table
        if admin_staff is None:
            # Create a new SupportStaff instance for the admin user
            admin_staff = SupportStaff(name="Admin", email="admin@email.com")
            # Add the new support staff to the session
            db.session.add(admin_staff)
        # Commit the changes to the database
        db.session.commit()

    # Run the Flask development server with Docker
    app.run(host='0.0.0.0', port=5000)

    # Use the line below instead if you're running the application without Docker
    # app.run()