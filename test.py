import mysql.connector

db = mysql.connector.connect(user='wikm', password='mmd123',
                              host='127.0.0.1', database = 'UKCalendar' )
cursor = db.cursor()
#create database :
#cursor.execute("CREATE DATABASE UKCalendar")
#create Tables in database :
#cursor.execute("CREATE TABLE users (name VARCHAR(255), chat_id VARCHAR(255))")
## defining the Query
#query = "INSERT INTO users (name, chat_id) VALUES (%s, %s)"
## storing values in a variable
#values = ("MOhammad Shafie", "8814")
## executing the query with values
#cursor.execute(query, values)
## to make final output we have to run the 'commit()' method of the database object
#db.commit()
## adding 'id' column to the 'users' table
## 'FIRST' keyword in the statement will add a column in the starting of the table
# cursor.execute("ALTER TABLE users ADD COLUMN id INT(11) NOT NULL AUTO_INCREMENT PRIMARY KEY FIRST")
# cursor.execute("DESC users")
## defining the Query
query = "SELECT * FROM users"
## getting records from the table
cursor.execute(query)
## fetching all records from the 'cursor' object
records = cursor.fetchall()
## Showing the data
for record in records:
    print(record)

#when table is created print it
#print(cursor.rowcount, "record inserted")
print(db)