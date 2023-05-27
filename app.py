# Import libraries
import random
from sqlalchemy.sql.expression import func
from flask import Flask, abort, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, current_user, logout_user, login_required
from forms import IssueForm, RegistrationForm, LoginForm, UpdateAccountForm
from werkzeug.security import generate_password_hash, check_password_hash
import os


# Setting up the flask application
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://ticketing_user:qwerty123@localhost/ticketing_system'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['LOGIN_VIEW'] = 'login'
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY
# Initialise database
db = SQLAlchemy(app)
# Initialise login manager
login_manager = LoginManager(app)
login_manager.init_app(app)
login_manager.login_view = 'login'

# Define the models based on the schema
class Employee(db.Model): # For the Employees Table
    # Create the table
    __tablename__ = 'employees'
    # Create the columns
    employee_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    phone = db.Column(db.String(15), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    # Create the relationship with the issues table
    issues = db.relationship('Issue', backref='employee', lazy=True)

class Issue(db.Model): # For the Issues Table
    # Create the table
    __tablename__ = 'issues'
    # Create the columns
    issue_id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.employee_id'), nullable=False)
    employee_name = db.Column(db.String(100), nullable=False)
    employee_email = db.Column(db.String(120), unique=True, nullable=False)
    location = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), nullable=False, default='Reported')
    support_name = db.Column(db.String(100))

class SupportStaff(db.Model): # For the Support Staff table
    # Create the table
    __tablename__ = 'support_staff'
    # Create the columns
    support_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)

class Users(UserMixin, db.Model): # For the user login manager
    # Create the table
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

# Creater callback for login
@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

# Create the flask routes
@app.route('/') # home page
@login_required
def home():
    # This will be the home page, we can show some info about the system
    return render_template('home.html')

@app.route('/issues') # issues page for helpdesk staff
@login_required
def all_issues():
    support_staff = SupportStaff.query.filter_by(email=current_user.email).first()
    if not support_staff:
        flash('You do not have the necessary permissions to view this page.', 'danger')
        return redirect(url_for('home'))
    issues = Issue.query.all()
    return render_template('issues.html', issues=issues)

@app.route('/my_issues') # issues page for employee
@login_required
def my_issues():
    user_email = current_user.email # get the id of the currently logged in user
    issues = Issue.query.filter_by(employee_email=user_email).all()  # fetch the issues reported by this user
    return render_template('issues.html', issues=issues)


@app.route('/issues/<int:issue_id>') # individual issue page
@login_required
def issue(issue_id):
    issue = Issue.query.get_or_404(issue_id)
    if current_user.email != issue.employee_email:
        abort(403)
    return render_template('issue.html', issue=issue)

@app.route('/issue/new', methods=['GET', 'POST']) # new issue page
@login_required
def add_issue():
    form = IssueForm()
    if form.validate_on_submit():
        # Query SupportStaff table to get all IDs, and select one at random
        support_staff_names = SupportStaff.query.with_entities(SupportStaff.name).all()
        random_support_name = random.choice(support_staff_names)
        # Perform a join operation on User and Employee table to get employee id, name, and location
        employee_info = db.session.query(Employee.employee_id, Employee.location, Employee.name, Employee.email)\
                      .join(Users, Employee.email == Users.email)\
                      .filter(Users.email == current_user.email).first()
        # Create new issue
        issue = Issue(
            employee_id = employee_info.employee_id,
            employee_name = employee_info.name,
            employee_email = employee_info.email,
            location = employee_info.location,
            category=form.category.data,
            description=form.description.data,
            support_name=random_support_name[0],
        )

        db.session.add(issue)
        db.session.commit()
        return redirect(url_for('issue', issue_id=issue.issue_id))
    return render_template('add_issue.html', title='New Issue', form=form)

@app.route('/issue/<int:issue_id>/update', methods=['GET', 'POST']) # update issue page
@login_required
def update_issue(issue_id):
    issue = Issue.query.get_or_404(issue_id)
    if current_user.email != issue.employee_email:
        abort(403)
    form = IssueForm()
    if form.validate_on_submit():
        issue.category = form.category.data
        issue.description = form.description.data
        db.session.commit()
        flash('Your issue has been updated!', 'success')
        return redirect(url_for('issue', issue_id=issue.issue_id))
    elif request.method == 'GET':
        form.category.data = issue.category
        form.description.data = issue.description
    return render_template('update_issue.html', title='Update Issue', form=form)

@app.route('/register', methods=['GET', 'POST']) # for user registration
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        employee = Employee.query.filter_by(employee_id=form.employee_id.data).first()
        if employee:
            flash('That employee ID is taken. Please choose a different one.', 'danger')
            return redirect(url_for('register'))
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        user = Users(email=form.email.data, password=hashed_password)
        employee = Employee(employee_id=form.employee_id.data, name=form.name.data, email=form.email.data, phone=form.phone.data, location=form.location.data)
        db.session.add(user)
        db.session.add(employee)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        next_page = request.args.get('next')
        return redirect(next_page) if next_page else redirect(url_for('home'))
    return render_template('register.html', title="Register", form=form)

@app.route('/login', methods=['GET', 'POST']) # for user login
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)
    

@app.route('/logout') # for user logout
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/account', methods=['GET', 'POST']) # for updating user account information
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        current_user.email = form.email.data
        current_user.password = generate_password_hash(form.password.data, method='sha256')
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('login'))
    elif request.method == 'GET':
        form.email.data = current_user.email
    return render_template('account.html', title='Account', form=form)


# Create the tables in the database
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)