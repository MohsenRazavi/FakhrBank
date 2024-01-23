
from db import Database

DB_HOST = input("host: ")
DB_PORT = input("port: ")
DB_USER = input("username: ")
DB_PASSWORD = input("password: ")
DB_NAME = "FakhrBank"

db = Database(DB_HOST, DB_PORT, "", DB_USER, DB_PASSWORD)
res = db.create_database(DB_NAME)

if res[0]:
    db._name = DB_NAME
else:
    print(res)
    exit()

"""
Users Table

userId | username | passwordHash | firstName | lastName | birthdate | gender | phoneNumber | createdAt | type
=======|==========|==============|===========|==========|===========|========|=============|===========|=========
       |          |              |           |          |           |        |             |           |
"""
user_fields = {
    'userId': 'SERIAL PRIMARY KEY',
    'username': 'VARCHAR (50) UNIQUE',
    'firstName': 'VARCHAR (50)',
    'lastName': 'VARCHAR (50)',
    'birthdate': 'DATE',
    'gender': 'VARCHAR (5)',
    'phoneNumber': 'VARCHAR (13)',
    'createdAt': 'DATE',
    'type': 'VARCHAR (10)'
}
db.create_table('Users', user_fields)





