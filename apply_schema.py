import mysql.connector
from mysql.connector import errorcode

# --- Database Configuration (from app.py) ---
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'YQR050917.',
    'database': 'library_db'
}

def apply_schema():
    """Connects to the database and applies the SQL schema from a file."""
    try:
        # Read the SQL file
        with open('temp_schema.sql', 'r') as f:
            sql_script = f.read()
    except FileNotFoundError:
        print("Error: temp_schema.sql not found.")
        return

    try:
        # Connect to the database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        # Split the script into individual statements
        sql_commands = [cmd.strip() for cmd in sql_script.split(';') if cmd.strip()]

        # Execute each command
        for command in sql_commands:
            cursor.execute(command)
            print(f"Executed: {command[:50]}...")
        
        conn.commit()
        print("Successfully applied schema from temp_schema.sql")

    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()
            print("MySQL connection is closed")

if __name__ == '__main__':
    apply_schema()
