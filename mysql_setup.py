import mysql.connector
from mysql.connector import Error
from Variables import host_input , user_input , password_input , port_mysql


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
        
        # create table
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
        print("users tabale created successfully")
        
except Error as e:
    print(f"error in connect to Mysql: {e}")
finally:
    if connection.is_connected():
        cursor.close()
        connection.close()
        print("Mysql is disconnected.")