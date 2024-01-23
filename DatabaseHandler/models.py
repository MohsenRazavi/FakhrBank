from datetime import date

from constants import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASS


class User:
    def __init__(self, user_id, username, password, first_name, last_name, birthdate, gender, phone_number, created_at,
                 user_type):
        self.user_id = user_id
        self.username = username
        self._password = password
        self.first_name = first_name
        self.last_name = last_name
        self.birthdate = birthdate.strftime("%d")
        self.phone_number = phone_number
        self.created_at = created_at
        self.type = user_type
        self.gender = gender

    def __repr__(self):
        return f"{self.type} - {self.first_name} {self.last_name} ({self.username})"

    def get_age(self):
        today = date.today()
        age = today - self.birthdate
        return age

    def save(self, table_name):
        from DatabaseHandler import Database
        db = Database(DB_HOST, DB_PORT, DB_NAME.lower(), DB_USER, DB_PASS)
        update_list = {
            'username': self.username,
            'passwordHash': self._password,
            'firstName': self.first_name,
            'lastName': self.last_name,
            'birthdate': self.birthdate,
            'phoneNumber': self.phone_number,
            'gender': self.gender,
            'createdAt': self.created_at,
        }
        res = db.update(table_name, update_list, f'userId = {self.user_id}')
        if res[0]:
            return True
        else:
            print(res)

    class Accounts:
        def __init__(self, account_id, account_number, user_id, balance, account_type, created_at, name, status):
            self.account_id = account_id
            self.account_number = account_number
            self.user_id = user_id
            self.balance = balance
            self.type = account_type
            self.created_at = created_at
            self.name = name
            self.status = status

        def __str__(self):
            return f"{self.type} - {self.name} ({self.status})"

    class Transactions:
        def __init__(self, transaction_id, src_account, dst_account, amount, transaction_dt, status):
            self.transaction_id = transaction_id
            self.src_account = src_account
            self.dst_account = dst_account
            self.amount = amount
            self.date_time = transaction_dt
            self.status = status

        def __str__(self):
            return f"{self.src_account} to {self.dst_account} at {self.date_time} ({self.status})"

    class Loans:
        def __init__(self, loan_id, profit, dead_line, at_least_income):
            self.loan_id = loan_id
            self.profit = profit
            self.dead_line = dead_line
            self.at_least_income = at_least_income

        def __str__(self):
            return f"{self.dead_line} - {self.profit}"

    class LoansAccounts:
        def __init__(self, loan_account_id, loan_type, account_id, amount, paid, acceptor, status):
            self.loan_account_id = loan_account_id
            self.loan_type = loan_type
            self.account_id = account_id
            self.amount = amount
            self.paid = paid
            self.acceptor = acceptor
            self.status = status