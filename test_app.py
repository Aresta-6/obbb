import pytest
from app import app as flask_app
import mysql.connector
import os

# --- Test Database Configuration ---
TEST_DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'YQR050917.',
    'database': 'test_library_db'
}

def init_database():
    """Initializes the test database."""
    # Connect to MySQL server
    conn = mysql.connector.connect(
        host=TEST_DB_CONFIG['host'],
        user=TEST_DB_CONFIG['user'],
        password=TEST_DB_CONFIG['password']
    )
    cursor = conn.cursor()
    
    # Drop the test database if it exists, then create a new one
    cursor.execute(f"DROP DATABASE IF EXISTS {TEST_DB_CONFIG['database']}")
    cursor.execute(f"CREATE DATABASE {TEST_DB_CONFIG['database']}")
    conn.database = TEST_DB_CONFIG['database']

    # Read and execute schema and data SQL files
    with open('database/schema.sql', 'r', encoding='utf-8') as f:
        sql_script = f.read()
    for statement in sql_script.split(';'):
        if statement.strip():
            cursor.execute(statement)

    with open('database/data.sql', 'r', encoding='utf-8') as f:
        sql_script = f.read()
    for statement in sql_script.split(';'):
        if statement.strip():
            cursor.execute(statement)

    conn.commit()
    cursor.close()
    conn.close()

@pytest.fixture(scope='module')
def app():
    """Set up and tear down the test application and database."""
    # Initialize the test database once per module
    try:
        init_database()
    except Exception as e:
        print(f"Error initializing database: {e}")
        import traceback
        traceback.print_exc()
        raise

    # Create a new Flask app instance for testing
    from app import app as original_flask_app
    test_app_instance = original_flask_app
    
    # Configure the new app instance to use the test database
    test_app_instance.config["DB_CONFIG"] = TEST_DB_CONFIG
    test_app_instance.config.update({
        "TESTING": True,
        "WTF_CSRF_ENABLED": False,
    })
    
    yield test_app_instance
    
    # Teardown: Drop the test database
    conn = mysql.connector.connect(
        host=TEST_DB_CONFIG['host'],
        user=TEST_DB_CONFIG['user'],
        password=TEST_DB_CONFIG['password']
    )
    cursor = conn.cursor()
    cursor.execute(f"DROP DATABASE IF EXISTS {TEST_DB_CONFIG['database']}")
    conn.commit()
    cursor.close()
    conn.close()

@pytest.fixture
def client(app):
    return app.test_client()

def test_index(client):
    """Test the home page."""
    response = client.get('/')
    assert response.status_code == 200
    assert b"Welcome to the Library Portal." in response.data

def test_books_page(client):
    """Test the books page."""
    response = client.get('/books')
    assert response.status_code == 200
    assert b"All Books" in response.data

def test_login_page(client):
    """Test the login page loads."""
    response = client.get('/login')
    assert response.status_code == 200
    assert b"Login" in response.data

def test_successful_login(client):
    """Test a successful user login."""
    response = client.post('/login', data=dict(
        userid='student1',
        password='password123'
    ), follow_redirects=True)
    assert response.status_code == 200
    assert b"You were successfully logged in." in response.data
    assert b"Welcome, John Smith!" in response.data

def test_failed_login(client):
    """Test a failed user login with wrong password."""
    response = client.post('/login', data=dict(
        userid='student1',
        password='wrongpassword'
    ), follow_redirects=True)
    assert response.status_code == 200
    assert b"Invalid credentials." in response.data
    assert b"Welcome, John Smith!" not in response.data

def test_logout(client):
    """Test logging out."""
    # First, log in
    client.post('/login', data=dict(
        userid='student1',
        password='password123'
    ), follow_redirects=True)
    
    # Then, log out
    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b"You were logged out." in response.data
    assert b"Welcome, John Smith!" not in response.data

def test_my_reservations_page_logged_in(client):
    """Test that a logged-in user can view their reservations."""
    client.post('/login', data=dict(
        userid='student1',
        password='password123'
    ), follow_redirects=True)
    response = client.get('/my_reservations')
    assert response.status_code == 200
    assert b"My Reservations" in response.data

def test_my_reservations_page_logged_out(client):
    """Test that a logged-out user is redirected from the reservations page."""
    response = client.get('/my_reservations', follow_redirects=True)
    assert response.status_code == 200
    assert b"Login" in response.data
    assert b"You need to be logged in to view your reservations." in response.data

def test_admin_reservations_page_admin(client):
    """Test that an admin can view the admin reservations page."""
    client.post('/login', data=dict(
        userid='admin',
        password='password123'
    ), follow_redirects=True)
    response = client.get('/admin/reservations')
    assert response.status_code == 200
    assert b"Manage Reservations" in response.data

def test_admin_reservations_page_non_admin(client):
    """Test that a non-admin is redirected from the admin reservations page."""
    client.post('/login', data=dict(
        userid='student1',
        password='password123'
    ), follow_redirects=True)
    response = client.get('/admin/reservations', follow_redirects=True)
    assert response.status_code == 200
    assert b"You do not have permission to access this page." in response.data
    assert b"Welcome to the Library Portal." in response.data