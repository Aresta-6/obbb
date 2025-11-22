import types
import logging
from functools import wraps
from flask import session, flash, redirect, url_for, current_app
from contextlib import contextmanager

# Try to import the real MySQL connector; if missing, provide a dummy connector module
try:
    import mysql.connector as _mysql_connector
    mysql = types.SimpleNamespace(connector=_mysql_connector)
except ImportError:
    logging.warning(
        "MySQL 驱动未找到。数据库相关操作会返回错误提示。建议在虚拟环境中运行：\n"
        "    pip install mysql-connector-python\n\n"
        "请不要运行 `pip install mysql` —— 该包会尝试构建 mysqlclient，"
        "在 Windows 上通常需要安装 Microsoft C++ Build Tools（编译器）。"
    )

    class DummyMySQLError(Exception):
        """Raised when DB driver is not available."""
        pass

    class _DummyConnectorModule:
        Error = DummyMySQLError

        @staticmethod
        def connect(*args, **kwargs):
            raise DummyMySQLError(
                "MySQL 驱动未安装。请在虚拟环境中运行：pip install mysql-connector-python。"
                " 不要运行 `pip install mysql`（会触发编译 mysqlclient）。"
            )

    mysql = types.SimpleNamespace(connector=_DummyConnectorModule)


@contextmanager
def get_db_cursor(commit=False):
    """
    Context manager for database cursor.
    Uses current_app.config to get DB connection details.
    """
    conn = mysql.connector.connect(**current_app.config['DB_CONFIG'])
    cursor = conn.cursor(dictionary=True)
    try:
        yield cursor
        if commit:
            conn.commit()
    except mysql.connector.Error as err:
        if commit:
            conn.rollback()
        raise err
    finally:
        cursor.close()
        conn.close()


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('user_type') != 'Teacher':
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('main.index')) # Assuming index is in main blueprint
        return f(*args, **kwargs)
    return decorated_function


