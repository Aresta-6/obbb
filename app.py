from flask import Flask, session
from flask_wtf.csrf import CSRFProtect
from config import Config
from utils import get_db_cursor
import mysql.connector

app = Flask(__name__)
app.config.from_object(Config)
csrf = CSRFProtect(app)

# Register Blueprints
from routes.auth import auth_bp
from routes.main import main_bp
from routes.user import user_bp
from routes.admin import admin_bp

app.register_blueprint(auth_bp)
app.register_blueprint(main_bp)
app.register_blueprint(user_bp)
app.register_blueprint(admin_bp)

@app.context_processor
def inject_notifications():
    if 'user_id' not in session:
        return dict(unread_notification_count=0)

    count = 0
    try:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT COUNT(*) as count FROM Notifications WHERE UserID = %s AND IsRead = FALSE", (session['user_id'],))
            result = cursor.fetchone()
            if result:
                count = result['count']
    except mysql.connector.Error:
        count = 0
            
    return dict(unread_notification_count=count)

if __name__ == '__main__':
    app.run(debug=True)
