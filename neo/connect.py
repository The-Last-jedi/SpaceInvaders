import mysql.connector
mydb = mysql.connector.connect(host = 'localhost', user = 'root', passwd = '#@password', database = 'starwars')
mycursor = mydb.cursor()
query = 'create table neo(\
         roll_no int primary key,\
         name varchar(20) not null,\
         class int,\
         percentage float)'
mycursor.execute(query)
mydb.commit()
print("query successful")