from datetime import date


class User:
    def __init__(self, user_id, username, password, first_name, last_name, birthdate, phone_number, created_at,
                 user_type, gender):
        self.user_id = user_id
        self.username = username
        self._password = password
        self.first_name = first_name
        self.last_name = last_name
        self.birthdate = birthdate
        self.phone_number = phone_number
        self.created_at = created_at
        self.type = user_type
        self.gender = gender

    def __str__(self):
        return f"{self.type} - {self.first_name} {self.last_name} ({self.username})"

    def get_age(self):
        today = date.today()
        age = today - self.birthdate
        return age


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


