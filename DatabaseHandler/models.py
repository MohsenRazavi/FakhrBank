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
        self.birthdate = birthdate
        self.phone_number = phone_number
        self.created_at = created_at
        self.type = user_type
        self.gender = gender

    def __repr__(self):
        if self.first_name and self.last_name:
            return f'{self.first_name} {self.last_name}'
        return f"{self.username}"

    def get_age(self):
        today = date.today().year
        if self.birthdate:
            age = today - int(self.birthdate.split('-')[0])
            return age

    def get_created_at(self):
        return self.created_at.strftime('%Y/%m/%d %H:%M:%S')

    def save(self):
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
        }
        res = db.update('Users', update_list, f'userId = {self.user_id}')
        if res[0]:
            return True
        else:
            print(res)

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'username': self.username,
            'password': self._password,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'birthdate': self.birthdate,
            'gender': self.gender,
            'phone_number': self.phone_number,
            'created_at': self.created_at,
            'user_type': self.type,
        }

    @classmethod
    def from_dict(cls, user_dict):
        return cls(
            user_dict['user_id'],
            user_dict['username'],
            user_dict['password'],
            user_dict['first_name'],
            user_dict['last_name'],
            user_dict['birthdate'],
            user_dict['gender'],
            user_dict['phone_number'],
            user_dict['created_at'],
            user_dict['user_type'],
        )


class Account:
    def __init__(self, account_id, user_id, account_number, balance, account_type, created_at, name, status):
        self.account_id = account_id
        self.account_number = account_number
        self.user_id = user_id
        self.balance = balance
        self.type = account_type
        self.created_at = created_at
        self.name = name
        self.status = status

    def __repr__(self):
        if self.name and self.name != 'None':
            return self.name
        else:
            return f"{self.type}-{self.account_number[15:]}"

    def get_owner(self):
        from DatabaseHandler import Database
        db = Database(DB_HOST, DB_PORT, DB_NAME.lower(), DB_USER, DB_PASS)
        owner = db.select('Users', filters=f"userId = {self.user_id}", Model=User)[0][0]
        return owner

    def get_account_number(self):
        return self.account_number.replace('-', ' ')

    def get_created_at_date(self):
        return self.created_at.date()

    def get_created_at(self):
        return self.created_at.strftime('%Y/%m/%d %H:%M:%S')

    def save(self):
        from DatabaseHandler import Database
        db = Database(DB_HOST, DB_PORT, DB_NAME.lower(), DB_USER, DB_PASS)  
        update_list = {
            'accountId': self.account_id,
            'accountNumber': self.account_number,
            'userId': self.user_id,
            'balance': self.balance,
            'type': self.type,
            'name': self.name,
            'status': self.status,
        }
        res = db.update('Accounts', update_list, filters=f"accountId = '{self.account_id}'")
        if res[0]:
            return True
        else:
            print(res)


class Transaction:
    def __init__(self, transaction_id, src_account, dst_account, amount, created_at, status):
        self.transaction_id = transaction_id
        self.src_account = src_account
        self.dst_account = dst_account
        self.amount = amount
        self.created_at = created_at
        self.status = status

    def __str__(self):
        return f"{self.src_account} to {self.dst_account} at {self.created_at} ({self.status})"

    def get_created_at(self):
        return self.created_at.strftime('%Y/%m/%d %H:%M:%S')

    def get_src_account(self):
        from DatabaseHandler import Database
        db = Database(DB_HOST, DB_PORT, DB_NAME.lower(), DB_USER, DB_PASS)
        account = db.select('Accounts', filters=f"accountId = '{self.src_account}'", Model=Account)[0][0]
        return account

    def get_dst_account(self):
        from DatabaseHandler import Database
        db = Database(DB_HOST, DB_PORT, DB_NAME.lower(), DB_USER, DB_PASS)
        account = db.select('Accounts', filters=f"accountId = '{self.dst_account}'", Model=Account)[0][0]
        return account


class Loan:
    def __init__(self, loan_id, profit, dead_line, at_least_income, status):
        self.loan_id = loan_id
        self.profit = profit
        self.dead_line = dead_line
        self.at_least_income = at_least_income
        self.status = status

    def __repr__(self):
        return f"{self.dead_line} ماهه با {self.profit} درصد سود و حداقل مقدار واریز در ماه {self.at_least_income} تومان"

    def save(self):
        from DatabaseHandler import Database
        db = Database(DB_HOST, DB_PORT, DB_NAME.lower(), DB_USER, DB_PASS)
        updates = {
            'loanId': self.loan_id,
            'profit': self.profit,
            'deadline': self.dead_line,
            'atLeastIncome': self.at_least_income,
            'status': self.status
        }
        res = db.update('Loans', updates=updates, filters=f"loanId = '{self.loan_id}'")

        if res[0]:
            return True
        else:
            print(res)

    def is_deletable(self):
        from DatabaseHandler import Database
        db = Database(DB_HOST, DB_PORT, DB_NAME.lower(), DB_USER, DB_PASS)
        res = db.select('AccountLoans', filters=f"loanId = '{self.loan_id}' AND status < 2")[0]
        if len(res) > 0:
            return False
        return True


class AccountLoan:
    def __init__(self, loan_account_id, account_id, loan_id, amount, paid, acceptor, status):
        self.account_loan_id = loan_account_id
        self.loan_id = loan_id
        self.account_id = account_id
        self.amount = amount
        self.paid = paid
        self.acceptor = acceptor
        self.status = status

    def get_account(self):
        from DatabaseHandler import Database
        db = Database(DB_HOST, DB_PORT, DB_NAME.lower(), DB_USER, DB_PASS)
        account = db.select('Accounts', filters=f"accountId = '{self.account_id}'", Model=Account)[0][0]
        return account

    def get_loan(self):
        from DatabaseHandler import Database
        db = Database(DB_HOST, DB_PORT, DB_NAME.lower(), DB_USER, DB_PASS)
        loan = db.select('Loans', filters=f"loanId = '{self.loan_id}'", Model=Loan)[0][0]
        return loan

    def get_amount_with_profit(self):
        return int((100 + self.get_loan().profit) / 100 * self.amount)

    def get_acceptor(self):
        from DatabaseHandler import Database
        db = Database(DB_HOST, DB_PORT, DB_NAME.lower(), DB_USER, DB_PASS)
        if self.acceptor and self.acceptor != 'None':
            acceptor = db.select('Users', filters=f"userId = '{self.acceptor}'", Model=User)[0][0]
            return acceptor
        else:
            return "-"

    def save(self):
        from DatabaseHandler import Database
        db = Database(DB_HOST, DB_PORT, DB_NAME.lower(), DB_USER, DB_PASS)
        updates = {
            'accountLoanId': self.account_loan_id,
            'loanId': self.loan_id,
            'accountId': self.account_id,
            'amount': self.amount,
            'paid': self.paid,
            'acceptor': self.acceptor,
            'status': self.status,
        }
        res = db.update('AccountLoans', filters=f"accountLoanId = '{self.account_loan_id}'", updates=updates)[0]
        if res:
            return True
        else:
            print(res)

    def get_instalment(self):
        loan = self.get_loan()
        return int((100 + loan.profit) / 100 * self.amount // loan.dead_line)
