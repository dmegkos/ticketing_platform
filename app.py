# Import libraries
import random
from sqlalchemy.sql.expression import func
from flask import Flask, abort, render_template, request, redirect, url_for, flash
from flask_wtf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, current_user, logout_user, login_required
from forms import IssueFormEmployee, IssueFormSupport, RegistrationForm, LoginForm, UpdateAccountForm
from werkzeug.security import generate_password_hash, check_password_hash
import os


# Setting up the flask application
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://ticketing_user:qwerty123@db/ticketing_system'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['LOGIN_VIEW'] = 'login'
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY
csrf = CSRFProtect()
# Initialise database
db = SQLAlchemy(app)
# Initialise login manager
login_manager = LoginManager(app)
login_manager.init_app(app)
csrf.init_app(app)
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
    issues = db.relationship('Issue', backref='employee', lazy=True, cascade="all, delete-orphan")

class Issue(db.Model): # For the Issues Table
    # Create the table
    __tablename__ = 'issues'
    # Create the columns
    issue_id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.employee_id'), nullable=False)
    employee_name = db.Column(db.String(100), nullable=False)
    employee_email = db.Column(db.String(120), nullable=False)
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

# Function to get user type
def get_user_type(email):
    if Employee.query.filter_by(email=email).first():
        return 'employee'
    elif SupportStaff.query.filter_by(email=email).first():
        return 'support'
    return None

# Creater callback for login
@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

# Create the flask routes
@app.route('/') # home page
@login_required
def home():
    user_type = get_user_type(current_user.email)
    return render_template('home.html', user_type=user_type)

@app.route('/issues') # issues page for helpdesk staff
@login_required
def all_issues():
    support_staff = SupportStaff.query.filter_by(email=current_user.email).first()
    user_type = get_user_type(current_user.email)
    if not support_staff:
        flash('You do not have the necessary permissions to view this page.', 'danger')
        return redirect(url_for('home'))
    issues = Issue.query.all()
    return render_template('issues.html', issues=issues, user_type=user_type)

@app.route('/my_issues') # issues page for employee
@login_required
def my_issues():
    employee = Employee.query.filter_by(email=current_user.email).first()
    user_type = get_user_type(current_user.email)
    if not employee:
        flash('You do not have the necessary permissions to view this page.', 'danger')
        return redirect(url_for('home'))
    user_email = current_user.email # get the id of the currently logged in user
    issues = Issue.query.filter_by(employee_email=user_email).all()  # fetch the issues reported by this user
    return render_template('issues.html', issues=issues, user_type=user_type)


@app.route('/issues/<int:issue_id>', methods=['GET', 'POST']) # individual issue page
@login_required
def issue(issue_id):
    issue = Issue.query.get_or_404(issue_id)
    user_type = get_user_type(current_user.email)
    if (current_user.email != issue.employee_email) and (user_type != 'support'):
        abort(403)
    return render_template('issue.html', issue=issue, user_type=user_type)

@app.route('/issue/new', methods=['GET', 'POST']) # new issue page
@login_required
def add_issue():
    user_type = get_user_type(current_user.email)
    if user_type != 'employee':
        abort(403)
    form = IssueFormEmployee()
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
    return render_template('add_issue.html', title='New Issue', form=form, user_type=user_type)

@app.route('/issue/<int:issue_id>/update', methods=['GET', 'POST']) # update issue page
@login_required
def update_issue(issue_id):
    issue = Issue.query.get_or_404(issue_id)
    user_type = get_user_type(current_user.email)
    if (current_user.email != issue.employee_email) and (user_type != 'support'):
        abort(403)
    
    if user_type == 'employee':
        form = IssueFormEmployee()
    elif user_type == 'support':
        form = IssueFormSupport()
    else:
        abort(403)  # or handle this case as needed

    if form.validate_on_submit():
        if user_type == 'employee':
            issue.category = form.category.data
            issue.description = form.description.data
        elif user_type == 'support':
            support_user = SupportStaff.query.join(Users, Users.email == SupportStaff.email).filter(Users.email == current_user.email).first()
            issue.status = form.status.data
            issue.support_name = support_user.name
        db.session.commit()
        flash('Issue has been updated!', 'success')
        return redirect(url_for('issue', issue_id=issue.issue_id))
    elif request.method == 'GET':
        if user_type == 'employee':
            form.category.data = issue.category
            form.description.data = issue.description
        elif user_type == 'support' and issue.status:
            form.status.data = issue.status
    else:
        print(form.errors)
    return render_template('update_issue.html', title='Update Issue', form=form, user_type=user_type)


@app.route('/issue/<int:issue_id>/delete', methods=['POST'])
@login_required
def delete_issue(issue_id):
    issue = Issue.query.get_or_404(issue_id)
    if current_user.email != issue.employee_email:
        abort(403)
    db.session.delete(issue)
    db.session.commit()
    flash('Your issue has been deleted!', 'success')
    return redirect(url_for('my_issues'))

@app.route('/register', methods=['GET', 'POST']) # for user registration
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        employee_id = Employee.query.filter_by(employee_id=form.employee_id.data).first()
        employee_email = Employee.query.filter_by(email=form.email.data).first()
        support_email = SupportStaff.query.filter_by(email=form.email.data).first()
        if employee_id:
            flash('That employee ID is taken. Please choose a different one.', 'danger')
            return redirect(url_for('register'))
        if employee_email or support_email:
            flash('That email is taken. Please choose a different one.', 'danger')
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
        user_type = get_user_type(current_user.email)
        if user_type == 'employee':
            return redirect (url_for('my_issues'))
        elif user_type == 'support':
            return redirect(url_for('all_issues'))
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            user_type = get_user_type(user.email)
            if user_type == 'employee':
                return redirect(next_page) if next_page else redirect(url_for('my_issues'))
            elif user_type == 'support':
                return redirect(next_page) if next_page else redirect(url_for('all_issues'))
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
    user_type = get_user_type(current_user.email)
    form = UpdateAccountForm()
    if form.validate_on_submit():
        print(request.form)
        if request.form.get('action') == 'delete':
            if user_type == 'employee':
                employee_user = Employee.query.filter_by(email=current_user.email).first()
                if employee_user:
                    db.session.delete(employee_user)
            db.session.delete(current_user)
            db.session.commit()
            flash('Your account has been deleted.', 'success')
            return redirect(url_for('login'))
        elif request.form.get('action') == 'update': 
            user_with_same_email = Users.query.filter_by(email=form.email.data).first()
            if user_with_same_email and (user_with_same_email.id != current_user.id):
                flash('Email is already in use. Please choose a different one.', 'danger')
            else:
                if form.password.data:
                    current_user.password = generate_password_hash(form.password.data, method='sha256')
                old_email = current_user.email
                current_user.email = form.email.data
                if user_type == 'employee':
                    employee_user = Employee.query.filter_by(email=old_email).first()
                    if employee_user:
                        employee_user.email = form.email.data
                        # update employee_email in issues
                        issues_to_update = Issue.query.filter_by(employee_email=old_email).all()
                        for issue in issues_to_update:
                            issue.employee_email = form.email.data
                elif user_type == 'support':
                    support_user = SupportStaff.query.filter_by(email=old_email).first()
                    if support_user:
                        support_user.email = form.email.data
                db.session.commit()
                flash('Your account has been updated!', 'success')
            return redirect(url_for('account'))
    elif request.method == 'GET':
        form.email.data = current_user.email
    return render_template('account.html', title='Account', form=form, user_type=user_type)

@app.route('/about')
@login_required
def about():
    user_type = get_user_type(current_user.email)
    return render_template('about.html', user_type=user_type)



# Create the tables in the database
if __name__ == "__main__":
    with app.app_context():
        db.create_all()

        # Check if the admin user already exists
        admin_user = Users.query.filter_by(email="admin@email.com").first()
        admin_staff = SupportStaff.query.filter_by(email="admin@email.com").first()

        # If not, create them
        if admin_user is None:
            admin_user = Users(email="admin@email.com", password=generate_password_hash("qwer1234"))
            db.session.add(admin_user)

        if admin_staff is None:
            admin_staff = SupportStaff(name="Admin", email="admin@email.com")
            db.session.add(admin_staff)

        # Commit the changes
        db.session.commit()

    app.run(host='0.0.0.0', port=5000)
