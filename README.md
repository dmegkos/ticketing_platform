# HelpDesk Ticketing System

A simple Help Desk Ticketing system built using Flask. This system allows employees to report issues, and support staff to manage and address those issues.

## Features

- User registration and authentication (Employee, Support Staff)
- Issue reporting
- Issue tracking
- Issue updating
- Flash messages
- Pre-populated Admin account

## Technologies Used

- **Flask**: The Python web framework used for building the application.
- **SQLAlchemy**: The Python SQL toolkit and Object-Relational Mapper that gives application developers the full power and flexibility of SQL.
- **PostgreSQL**: The database used for storing user and ticket data.
- **Flask-WTF**: For form handling.
- **Werkzeug**: For password hashing to ensure security.
- **Flask-Login**: For handling user sessions.

## Setting Up

1. Clone this repository.

2. Set up a virtual environment and install the dependencies:

<pre><code>$ python3 -m venv env
$ source env/bin/activate
$ pip install -r requirements.txt
</code></pre>

3. Set up your PostgreSQL database and update the configuration in `app.py`.

<pre><code>#SQL_Queries_for_PostgreSQL
CREATE DATABASE ticketing_system;
CREATE USER ticketing_user WITH PASSWORD ‘qwerty123’;
GRANT ALL PRIVILEGES ON DATABASE ticketing_system TO ticketing_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO ticketing_user;</code></pre>

4. Run the application:

<pre><code>$ python app.py
</code></pre>

## Application Screenshots

![Login Screen](/pictures/1_login.png)
![Register Screen](/pictures/2_register.png)
![Account Created](/pictures/3_account_created.png)
![Home Page](/pictures/4_home.png)
![Update Account](/pictures/5_update_account.png)
![About Page](/pictures/6_about.png)
![Empty Issues - Employee](/pictures/7_my_issues_empty.png)
![New Issue](/pictures/8_new_issue.png)
![Issue Details](/pictures/9_issue_details.png)
![Issues - Employee](/pictures/10_my_issues.png)
![Issues - Support](/pictures/11_all_issues_admin.png)
![Update Issue - Support](/pictures/12_admin_update_issue.png)
![Updated Issues - Support](/pictures/13_updated_issues.png)