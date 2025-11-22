from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from utils import get_db_cursor
import mysql.connector

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_type = request.form['user_type']
        
        try:
            with get_db_cursor(commit=True) as cursor:
                # Check if user already exists
                cursor.execute("SELECT * FROM Users WHERE UserID = %s", (username,))
                if cursor.fetchone():
                    flash('UserID already exists.')
                    return render_template('register.html')

                # Insert new user
                insert_query = """
                    INSERT INTO Users (UserID, FullName, UserType, PasswordHash, RegistrationDate)
                    VALUES (%s, %s, %s, %s, %s)
                """
                hashed_password = generate_password_hash(password)
                cursor.execute(insert_query, (username, username, user_type, hashed_password, datetime.now()))
                flash('You have successfully registered. Please login.')
                return redirect(url_for('auth.login'))
        except mysql.connector.Error as err:
            flash(f'An error occurred: {err}')
            
    return render_template('register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        userid = request.form['userid']
        password = request.form['password']
        
        try:
            with get_db_cursor() as cursor:
                cursor.execute("SELECT * FROM Users WHERE UserID = %s", (userid,))
                user = cursor.fetchone()
                
                if user and check_password_hash(user['PasswordHash'], password):
                    session['user_id'] = user['UserID']
                    session['user_name'] = user['FullName']
                    session['user_type'] = user['UserType'] # Store user type in session
                    flash('You were successfully logged in.')
                    return redirect(url_for('main.index'))
                else:
                    flash('Invalid credentials.')
        except mysql.connector.Error as err:
            flash(f'Database connection failed: {err}')
            
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user_name', None)
    session.pop('user_type', None)
    flash('You were logged out.')
    return redirect(url_for('main.index'))


