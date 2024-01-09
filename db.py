from flask_mysqldb import MySQL
from flask import current_app

mysql = MySQL()

def create_tables():
    with current_app.app_context():
        with mysql.connection.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(20) NOT NULL,
                    password VARCHAR(60) NOT NULL
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS recipe (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    title VARCHAR(100) NOT NULL,
                    content TEXT NOT NULL,
                    category VARCHAR(50) NOT NULL,
                    user_id INT,
                    FOREIGN KEY (user_id) REFERENCES user(id)
                )
            """)

            mysql.connection.commit()
