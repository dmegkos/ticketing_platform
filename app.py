# Import libraries
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, current_user, logout_user, login_required
from forms import IssueForm, RegistrationForm, LoginForm, UpdateAccountForm
from werkzeug.security import generate_password_hash, check_password_hash
import os


# Setting up the flask application
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://ticketing_user:qwerty123@localhost/ticketing_system'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY
# Initialise database
db = SQLAlchemy(app)
# Initialise login manager
login_manager = LoginManager()
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
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), nullable=False, default='reported')
    support_id = db.Column(db.Integer, db.ForeignKey('support_staff.support_id'))

class SupportStaff(db.Model): # For the Support Staff table
    # Create the table
    __tablename__ = 'support_staff'
    # Create the columns
    support_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    # Create the relationship with the issues table
    issues = db.relationship('Issue', backref='support_staff', lazy=True)

class User(UserMixin, db.Model): # For the user login manager
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

# Creater callback for login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Create the flask routes
@app.route('/') # home page
def home():
    # This will be the home page, we can show some info about the system
    return render_template('home.html')

@app.route('/issues') # issues page
def all_issues():
    issues = Issue.query.all()
    return render_template('issues.html', issues=issues)

@app.route('/issues/<int:issue_id>') # individual issue page
def issue(issue_id):
    issue = Issue.query.get(issue_id)
    return render_template('issue.html', issue=issue)

@app.route('/issue/new', methods=['GET', 'POST']) # new issue page
def add_issue():
    form = IssueForm()
    if form.validate_on_submit():
        issue = Issue(employee_id=form.employee_id.data, category=form.category.data,
                      description=form.description.data)
        db.session.add(issue)
        db.session.commit()
        return redirect(url_for('issue', issue_id=issue.issue_id))
    return render_template('add_issue.html', title='New Issue', form=form)

@app.route('/issue/<int:issue_id>/update', methods=['GET', 'POST']) # update issue page
def update_issue(issue_id):
    issue = Issue.query.get_or_404(issue_id)
    form = IssueForm()
    if form.validate_on_submit():
        issue.employee_id = form.employee_id.data
        issue.category = form.category.data
        issue.descrition = form.description.data
        db.session.commit()
        return redirect(url_for('issue', issue_id=issue.issue_id))
    elif request.method == 'GET':
        form.employee_id.data = issue.employee_id
        form.category.data = issue.category
        form.description.data = issue.description
    return render_template('update_issue.html', title='Update Issue', form=form)

@app.route('/register', methods=['GET', 'POST']) # for user registration
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title="Register", form=form)

@app.route('/login', methods=['GET', 'POST']) # for user login
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route('/logout') # for user logout
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/account', methods=['GET', 'POST']) # for updating user account information
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        current_user.email = form.email.data
        current_user.password = generate_password_hash(form.password.data, method='sha256')
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.email.data = current_user.email
    return render_template('account.html', title='Account', form=form)


# Create the tables in the database
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)