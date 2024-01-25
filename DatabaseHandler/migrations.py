import hashlib
from datetime import datetime

from constants import CGRN, CRED, CEND, DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASS, BANK_ACCOUNT_NAME, \
    BANK_ACCOUNT_TYPE, BANK_ACCOUNT_BALANCE, BANK_ACCOUNT_NUMBER, BASE_LOAN_PROFIT, BASE_LOAN_DEADLINE, \
    BASE_LOAN_ATLEAST_INCOME
from db import Database

print('Fakhr Bank Database Configuration')
print(f'Connecting to database {DB_NAME} on {DB_HOST}:{DB_PORT} with {DB_USER}')

db = Database(DB_HOST, DB_PORT, "", DB_USER, DB_PASS)
res = db.create_database(DB_NAME)

if res[0]:
    print(f'{CGRN}Database created successfully!{CEND}')
    db._name = DB_NAME.lower()
else:
    print(f'{CRED}Database creation failed. more details: \n{res}{CEND}')
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
    'passwordHash': 'VARCHAR (260)',
    'firstName': 'VARCHAR (50)',
    'lastName': 'VARCHAR (50)',
    'birthdate': 'VARCHAR (12)',
    'gender': 'VARCHAR (5)',
    'phoneNumber': 'VARCHAR (13)',
    'createdAt': 'TIMESTAMP',
    'type': 'VARCHAR (10)'
}
res0 = db.create_table('Users', user_fields)

if res0[0]:
    print(f'{CGRN}Users table created successfully!{CEND}')
else:
    print(f'{CRED}Users table creation failed. more details: \n{res}{CEND}')

"""
Accounts Table

accountId | userId | accountNumber | balance | type | createdAt | name | status 
==========|========|===============|=========|======|===========|======|===========
          |        |               |         |      |           |      |
"""

account_fields = {
    'accountId': 'SERIAL PRIMARY KEY',
    'userId': 'INTEGER REFERENCES Users(userId)',
    'accountNumber': 'VARCHAR(20) UNIQUE',
    'balance': 'BIGINT',
    'type': 'VARCHAR(10)',
    'createdAt': 'TIMESTAMP',
    'name': 'VARCHAR (50)',
    'status': 'BOOLEAN DEFAULT True'
}
res1 = db.create_table('Accounts', account_fields)
if res1[0]:
    print(f'{CGRN}Accounts table created successfully!{CEND}')
else:
    print(f'{CRED}Accounts table creation failed. more details: \n{res}{CEND}')

"""
Transactions Table

transactionId | srcAccount | dstAccount | amount | createdAt | status 
==============|============|============|========|===========|==========
              |            |            |        |
"""
transaction_fields = {
    'transactionId': 'SERIAL PRIMARY KEY',
    'srcAccount': 'INTEGER REFERENCES Accounts(accountId)',
    'dstAccount': 'INTEGER REFERENCES Accounts(accountId)',
    'amount': 'BIGINT',
    'createdAt': 'TIMESTAMP',
    'status': 'BOOLEAN'
}
res2 = db.create_table('Transactions', transaction_fields)
if res2[0]:
    print(f'{CGRN}Transactions table created successfully!{CEND}')
else:
    print(f'{CRED}Transactions table creation failed. more details: \n{res}{CEND}')

"""
Loans Table

loanId | profit | deadline | atLeastIncome 
=======|========|==========|====================
       |        |          |          
"""
loan_fields = {
    'loanId': 'SERIAL PRIMARY KEY',
    'profit': 'SMALLINT',
    'deadline': 'SMALLINT',
    'atLeastIncome': 'BIGINT'
}
res3 = db.create_table('Loans', loan_fields)
if res3[0]:
    print(f'{CGRN}Loans table created successfully!{CEND}')
else:
    print(f'{CRED}Loans table creation failed. more details: \n{res}{CEND}')

"""
AccountLoans Table

accountLoanId | accountId | loanId | amount | paid | acceptor | status 
==============|===========|========|========|======|==========|===========
              |           |        |        |      |          |          
"""
account_loan_fields = {
    'accountLoanId': 'SERIAL PRIMARY KEY',
    'accountId': 'INTEGER REFERENCES Accounts(accountId)',
    'loanId': 'INTEGER REFERENCES Loans(loanId)',
    'amount': 'BIGINT',
    'paid': 'BIGINT',
    'acceptor': 'INTEGER REFERENCES USERS(userId)',
    'status': 'SMALLINT'
}
res4 = db.create_table('AccountLoans', account_loan_fields)
if res4[0]:
    print(f'{CGRN}AccountLoans table created successfully!{CEND}')
else:
    print(f'{CRED}AccountLoans table creation failed. more details: \n{res}{CEND}')

if res0 and res1 and res2 and res3 and res4:
    print(f'\n{CGRN}DATABASE SCHEMA CREATED SUCCESSFULLY{CEND}\n')

    admin_username = input('Enter admin username: ')
    admin_password = input('Enter admin password: ')
    pswd_hash = hashlib.sha256(admin_password.encode('utf-8')).hexdigest()
    creation_time = datetime.now()
    res_admin = db.insert('Users', ('username', 'passwordHash', 'createdAt', 'type'),
                    (admin_username, pswd_hash, creation_time, 'admin'))
    admin_id = int(db.select('Users', ('userId',))[0][0][0])
    if res_admin[0]:
        print(f'{CGRN}Admin {admin_username} created successfully. Now you can login to your account !{CEND}')
        res_account = db.insert('Accounts',
                                 ('account_number', 'user_id', 'balance', 'type', 'created_at', 'name', 'status',), (
                                     BANK_ACCOUNT_NUMBER, admin_id, BANK_ACCOUNT_BALANCE, BANK_ACCOUNT_TYPE,
                                     creation_time,
                                     BANK_ACCOUNT_NAME, True))
        if res_account[0]:
            print(f'{CGRN}Bank account created successfully.{CEND}')
        else:
            print(f'{CRED}Bank account creation failed. more details:\n{res_account}{CEND}')

    else:
        res_account = None, None
        print(f'{CRED}Admin creation failed. more details:\n{res_admin}{CEND}')

    res_loan = db.insert('Loans', ('profit', 'deadline', 'atLeastIncome'),
                    (BASE_LOAN_PROFIT, BASE_LOAN_DEADLINE, BASE_LOAN_ATLEAST_INCOME))
    if res_loan[0]:
        print(f'{CGRN}Base loan created successfully.{CEND}')
    else:
        print(f'{CRED}Base loan creation failed. more details:\n{res_loan}{CEND}')

    if res_admin[0] and res_account[0] and res_loan[0]:

        with open('FakhrBank.log', 'w') as file:
            text = f"""
FAKHR BANK PROJECT REPORT

The project is started at {creation_time}

Bank account name: {BANK_ACCOUNT_NAME}
Bank account number: {BANK_ACCOUNT_NUMBER}
Bank account balance: {BANK_ACCOUNT_BALANCE}

Admin: {admin_username}
Password: {'*' * len(admin_password)} :)
Password hash: {pswd_hash}

have a good day 😉😉
                """
            file.write(text)
