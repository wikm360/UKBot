import mysql.connector
from mysql.connector import Error
from Variables import host_input, user_input, password_input, port_mysql

try:
    connection = mysql.connector.connect(
        host=host_input,
        user=user_input,
        password=password_input,
        port=port_mysql
    )
    
    if connection.is_connected():
        cursor = connection.cursor()
        
        cursor.execute("CREATE DATABASE IF NOT EXISTS UKCalendar")
        print("UKCalendar database created successfully")
        
        cursor.execute("USE UKCalendar")
        
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
        print("users table created successfully")
        
        cursor.execute("SHOW COLUMNS FROM users")
        existing_columns = [column[0] for column in cursor.fetchall()]
        
        columns_to_add = []

        if 'id' not in existing_columns:
            columns_to_add.append("ADD COLUMN id INT NOT NULL AUTO_INCREMENT")
        if 'name' not in existing_columns:
            columns_to_add.append("ADD COLUMN name VARCHAR(255) DEFAULT NULL")
        if 'chat_id' not in existing_columns:
            columns_to_add.append("ADD COLUMN chat_id VARCHAR(255) DEFAULT NULL")
        if 'nut_username' not in existing_columns:
            columns_to_add.append("ADD COLUMN nut_username VARCHAR(255) DEFAULT NULL")
        if 'nut_password' not in existing_columns:
            columns_to_add.append("ADD COLUMN nut_password VARCHAR(255) DEFAULT NULL")
        if 'last_reminder' not in existing_columns:
            columns_to_add.append("ADD COLUMN last_reminder VARCHAR(255) DEFAULT NULL")
        
        if columns_to_add:
            alter_table_query = f"ALTER TABLE users {', '.join(columns_to_add)}"
            cursor.execute(alter_table_query)
            print("Missing columns added successfully")
        else:
            print("All necessary columns already exist")

except Error as e:
    print(f"Error in connect to MySQL: {e}")
finally:
    if connection.is_connected():
        cursor.close()
        connection.close()
        print("MySQL connection closed.")
