import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev_key_change_in_production'
    DB_CONFIG = {
        'host': 'localhost',
        'user': 'root',
        'password': 'YQR050917.', # 建议从 os.environ.get('DB_PASSWORD') 获取
        'database': 'library_db'
    }
    PER_PAGE = 10 # 每页显示的书籍数量
    DAILY_FINE = 0.5 # 逾期每天罚款金额
