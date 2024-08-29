import mysql.connector
from mysql.connector import Error

try:
    connection = mysql.connector.connect(
        host='127.0.0.1',
        user='root',
        password='Mdmd@1383'
    )
    
    if connection.is_connected():
        cursor = connection.cursor()
        
        # ایجاد دیتابیس
        cursor.execute("CREATE DATABASE IF NOT EXISTS UKCalendar")
        print("دیتابیس UKCalendar با موفقیت ساخته شد.")
        
        # استفاده از دیتابیس
        cursor.execute("USE UKCalendar")
        
        # ایجاد جدول users با دو ستون جدید
        create_table_query = """
        CREATE TABLE IF NOT EXISTS users (
          id INT NOT NULL AUTO_INCREMENT,
          name VARCHAR(255) DEFAULT NULL,
          chat_id VARCHAR(255) DEFAULT NULL,
          nut_username VARCHAR(255) DEFAULT NULL,
          nut_password VARCHAR(255) DEFAULT NULL,
          last_reminder VARCHAR(255) DEFAULT NULL,
          PRIMARY KEY (id)
        )
        """
        cursor.execute(create_table_query)
        print("جدول users با موفقیت ساخته شد.")
        
except Error as e:
    print(f"خطا در اتصال به MySQL: {e}")
finally:
    if connection.is_connected():
        cursor.close()
        connection.close()
        print("اتصال به MySQL بسته شد.")