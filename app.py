import datetime
import hashlib
import random

from flask import Flask, render_template, request, flash, redirect, url_for, session, jsonify

from DatabaseHandler import Database
from DatabaseHandler.models import User, Account, Transaction, Loan, AccountLoan
from constants import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASS, BANK_ACCOUNT_NUMBER

app = Flask(__name__)
app.static_url_path = ""
app.static_folder = "templates/static/"
app.template_folder = "templates"
app.secret_key = '1234'

db = Database(DB_HOST, DB_PORT, DB_NAME.lower(), DB_USER, DB_PASS)


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == "GET":
        if 'user' in session:  # user already logged in !
            user = User.from_dict(session['user'])
            if user.type == "admin":
                return redirect(url_for('admin_panel'))
            elif user.type == "employee":
                return redirect(url_for('employee_panel'))
            elif user.type == "customer":
                return redirect(url_for('customer_panel'))
            else:
                return "<h1>Invalid usertype</h1>"
        return render_template('./login.html')
    else:  # POST
        username = request.form['username']
        password = request.form['password']
        pswd_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
        res = db.select('Users', Model=User, filters=f"username = '{username}' AND passwordHash = '{pswd_hash}'")
        if res[0]:  # login successful !
            obj = res[0][0]
            session['user'] = obj.to_dict()
            flash(f'{obj}  خوش آمدید !', 'success')
            if obj.type == "admin":
                return redirect(url_for('admin_panel'))
            elif obj.type == "employee":
                return redirect(url_for('employee_panel'))
            elif obj.type == "customer":
                return redirect(url_for('customer_panel'))
            else:
                return "<h1>Invalid usertype</h1>"
        else:  # login failed :(
            flash('کاربر یافت نشد', 'danger')
            return render_template('./login.html')


@app.route('/logout')
def logout():
    if 'user' in session:
        del session['user']
    return redirect(url_for('login'))


@app.route('/update_profile/', methods=['POST'])
def update_profile():
    if 'user' in session:
        user = User.from_dict(session['user'])
        test_username = request.form['username']
        records = db.select('Users', ['username'])[0]
        usernames = [record[0] for record in records]
        if test_username in usernames and test_username != user.username:
            flash('این نام کاربری قبلا استفاده شده', 'danger')
            if user.type == 'admin':
                return redirect(url_for('admin_panel'))
            elif user.type == 'employee':
                return redirect(url_for('employee_panel'))
            else:
                return redirect(url_for('customer_panel'))
        else:
            user.username = test_username
            user.first_name = request.form['first_name']
            user.last_name = request.form['last_name']
            user.phone_number = request.form['phone_number']
            user.birthdate = request.form['birthdate']
            user.save()
            session['user'] = user.to_dict()
            flash('مشخصات کاربری با موفقیت به روز شدند', 'success')
            if user.type == 'admin':
                return redirect(url_for('admin_panel'))
            elif user.type == 'employee':
                return redirect(url_for('employee_panel'))
            elif user.type == 'user':
                return redirect(url_for('customer_panel'))
    else:  # user not authenticated
        flash('ابتدا به حساب کاربری خود وارد شوید', 'warning')
        return redirect(url_for('login'))


@app.route('/change_password', methods=['POST'])
def change_password():
    if 'user' in session:
        user = User.from_dict(session['user'])
        old_password = request.form['old_password']
        new_password1 = request.form['password1']
        new_password2 = request.form['password2']
        user_pass = db.select('Users', ('passwordHash',), f"username = '{user.username}'")[0][0][0]
        old_pswd_hash = hashlib.sha256(old_password.encode('utf-8')).hexdigest()
        if old_pswd_hash != user_pass:
            flash('کلمه عبور فعلی اشتباه است', 'danger')
            if user.type == 'admin':
                return redirect(url_for('admin_panel'))
            elif user.type == 'employee':
                return redirect(url_for('employee_panel'))
            else:
                return redirect(url_for('customer_panel'))
        if new_password1 != new_password2:
            flash('کلمه عبور و تکرار آن یکی نیستند', 'danger')
            if user.type == 'admin':
                return redirect(url_for('admin_panel'))
            elif user.type == 'employee':
                return redirect(url_for('employee_panel'))
            else:
                return redirect(url_for('customer_panel'))

        pswd_hash = hashlib.sha256(new_password1.encode('utf-8')).hexdigest()
        res = db.exact_exec(f"UPDATE Users SET passwordHash = '{pswd_hash}' WHERE username = '{user.username}';")[0]
        if res:
            del session['user']
            flash('کلمه عبور با موفقیت تغییر کرد. دوباره وارد شوید.', 'success')
            return redirect(url_for('login'))
    else:
        flash('ابتدا به حساب کاربری خود وارد شوید', 'warning')
        return redirect(url_for('login'))


@app.route('/admin/')
def admin_panel():
    if 'user' in session:
        user = User.from_dict(session['user'])
        if user.type == 'admin':
            employees = db.select('Users', filters="type = 'employee'", Model=User)[0]
            customers = db.select('Users', filters="type = 'customer'", Model=User)[0]
            accounts = db.select('Accounts', Model=Account)[0]
            transactions = db.select('Transactions', Model=Transaction)[0]
            loans = db.select('Loans', Model=Loan)[0]
            account_loans = db.select('AccountLoans', Model=AccountLoan)[0]
            bank_account = db.select('Accounts', filters=f"accountNumber = '{BANK_ACCOUNT_NUMBER}'", Model=Account)[0][
                0]
            try:
                debtors_count = \
                    db.exact_exec(f"SELECT COUNT(DISTINCT(accountId)) FROM AccountLoans WHERE status = 1", fetch=True)[
                        1][0][0]
            except IndexError:
                debtors_count = 0
            try:
                sum_of_debts = db.exact_exec(
                    f"SELECT SUM(amount*(100+profit)/100-paid) AS Debt FROM AccountLoans INNER JOIN Loans ON AccountLoans.loanId = Loans.loanId WHERE AccountLoans.status = 1;",
                    fetch=True)[1][0][0]
                if not sum_of_debts:
                    sum_of_debts = 0
            except IndexError:
                sum_of_debts = 0

            context = {
                'user': user,
                'employees': employees,
                'employees_count': len(employees),
                'customers': customers,
                'customers_count': len(customers),
                'accounts': accounts,
                'accounts_count': len(accounts),
                'transactions': transactions,
                'transactions_count': len(transactions),
                'loans': loans,
                'account_loans': account_loans,
                'account_loans_count': len(account_loans),
                'debtors_count': debtors_count,
                'sum_of_debts': sum_of_debts,
                'bank_account': bank_account,
                'active_accounts_count': len([account for account in accounts if account.status])
            }
            return render_template('./admin_dashboard.html', **context)
        else:  # user is not admin
            del session['user']
            flash('پایتان را به اندازه گلیمتان دراز کنید !', 'warning')
            return redirect(url_for('login'))
    else:  # user not authenticated
        flash('ابتدا به حساب کاربری خود وارد شوید', 'warning')
        return redirect(url_for('login'))


@app.route('/employee')
def employee_panel():
    if 'user' in session:
        user = User.from_dict(session['user'])
        customers = db.select('Users', filters="type = 'customer'", Model=User)[0]
        accounts = db.select('Accounts', Model=Account)[0]
        transactions = db.select('Transactions', Model=Transaction)[0]
        loans = db.select('Loans', Model=Loan)[0]
        account_loans = db.select('AccountLoans', Model=AccountLoan)[0]
        bank_account = db.select('Accounts', filters=f"accountNumber = '{BANK_ACCOUNT_NUMBER}'", Model=Account)[0][
            0]
        if user.type == 'employee':
            context = {
                'user': user,
                'customers': customers,
                'customers_count': len(customers),
                'accounts': accounts,
                'accounts_count': len(accounts),
                'transactions': transactions,
                'transactions_count': len(transactions),
                'loans': loans,
                'account_loans': account_loans,
                'account_loans_count': len(account_loans),
                'bank_account': bank_account,
                'active_accounts_count': len([account for account in accounts if account.status])
            }
            return render_template('./employee_dashboard.html', **context)
        else:  # user is not employee
            del session['user']
            flash('پایتان را به اندازه گلیمتان دراز کنید !', 'warning')
            return redirect(url_for('login'))
    else:  # user not authenticated
        flash('ابتدا به حساب کاربری خود وارد شوید', 'warning')
        return redirect(url_for('login'))


@app.route('/customer')
def customer_panel():
    if 'user' in session:
        user = User.from_dict(session['user'])
        accounts = db.select('Accounts', filters=f"userId = {user.user_id}", Model=Account)[0]
        transaction_records = db.exact_exec(
            f"SELECT Transactions.* FROM Transactions INNER JOIN Accounts ON Transactions.srcAccount = Accounts.accountId OR Transactions.dstAccount = Accounts.accountId WHERE userId = {user.user_id};",
            fetch=True)[1]
        loans = db.select('Loans', filters=f"status = 'true'", Model=Loan)[0]
        sum_of_debts = db.exact_exec(
            f"SELECT SUM(amount*(100+profit)/100-paid) AS Debt FROM AccountLoans INNER JOIN Loans ON AccountLoans.loanId = Loans.loanId WHERE AccountLoans.status = 1 AND accountId IN (SELECT accountId FROM Accounts WHERE userId = {user.user_id});",
            fetch=True)[1][0][0]
        if not sum_of_debts:
            sum_of_debts = 0
        transactions = []
        for record in transaction_records:
            transactions.append(Transaction(*record))

        account_loans_records = db.exact_exec(
            f"SELECT AccountLoans.* FROM AccountLoans INNER JOIN Accounts ON AccountLoans.accountId = Accounts.accountId WHERE userId = {user.user_id};",
            fetch=True)[1]
        paying_account_loans = []
        account_loans = []
        for record in account_loans_records:
            if record[-1] == 1:
                paying_account_loans.append(AccountLoan(*record))

            account_loans.append(AccountLoan(*record))
        if user.type == 'customer':
            context = {
                'user': user,
                'accounts': accounts,
                'transactions': transactions,
                'loans': loans,
                'account_loans': account_loans,
                'sum_of_debts': sum_of_debts,
                'paying_account_loans': paying_account_loans
            }
            return render_template('./customer_dashboard.html', **context)
        else:  # user is not customer
            del session['user']
            flash('پایتان را به اندازه گلیمتان دراز کنید !', 'warning')
            return redirect(url_for('login'))
    else:  # user not authenticated
        flash('ابتدا به حساب کاربری خود وارد شوید', 'warning')
        return redirect(url_for('login'))


@app.route('/add_employee', methods=['POST'])
def add_employee():
    if 'user' in session:
        user = User.from_dict(session['user'])
        if user.type != 'admin':
            return "<h1>این عملیات برای شما مجاز نیست</h1>", 403

        emp_username = request.form['username']
        emp_firstname = request.form['first_name']
        emp_lastname = request.form['last_name']
        emp_gender = request.form['gender']
        emp_birthdate = request.form['birth_date']
        emp_phone_number = request.form['phone_number']
        emp_password1 = request.form['password1']
        emp_password2 = request.form['password2']

        records = db.select('Users', ['username'])[0]
        usernames = [record[0] for record in records]
        context = {
            'user': user,
        }
        if emp_username in usernames:
            flash('این نام کاربری قبلا استفاده شده', 'danger')
            return redirect(url_for('admin_panel', **context))
        if emp_password1 != emp_password2:
            flash('کلمه عبور و تکرار آن یکی نیستند', 'danger')
            return redirect(url_for('admin_panel', **context))
        else:
            pswd_hash = hashlib.sha256(emp_password1.encode('utf-8')).hexdigest()
        created_at = datetime.datetime.now()
        res = db.insert('Users', (
            'username', 'passwordHash', 'firstname', 'lastname', 'birthdate', 'gender', 'phonenumber', 'createdat',
            'type'),
                        (emp_username, pswd_hash, emp_firstname, emp_lastname, emp_birthdate, emp_gender,
                         emp_phone_number, created_at, 'employee'))

        if res[0]:
            flash('کارمند با موفقیت اضافه شد', 'success')
            return redirect(url_for('admin_panel', **context))
        else:
            print(res)
    else:  # user not authenticated
        flash('ابتدا به حساب کاربری خود وارد شوید', 'warning')
        return redirect(url_for('login'))


@app.route('/add_customer', methods=['POST'])
def add_customer():
    if 'user' in session:
        user = User.from_dict(session['user'])
        if user.type != 'admin' and user.type != 'employee':
            return "<h1>این عملیات برای شما مجاز نیست</h1>", 403
        cstmr_username = request.form['username']
        cstmr_firstname = request.form['firstname']
        cstmr_lastname = request.form['lastname']
        cstmr_gender = request.form['gender']
        cstmr_birthdate = request.form['birthdate']
        cstmr_phone_number = request.form['phone_number']
        cstmr_password1 = request.form['password1']
        cstmr_password2 = request.form['password2']

        records = db.select('Users', ['username'])[0]
        usernames = [record[0] for record in records]
        context = {
            'user': user,
        }
        if cstmr_username in usernames:
            flash('این نام کاربری قبلا استفاده شده', 'danger')
            return redirect(url_for('admin_panel', **context))
        if cstmr_password1 != cstmr_password2:
            flash('کلمه عبور و تکرار آن یکی نیستند', 'danger')
            return redirect(url_for('admin_panel', **context))
        else:
            pswd_hash = hashlib.sha256(cstmr_password1.encode('utf-8')).hexdigest()
        created_at = datetime.datetime.now()
        res = db.insert('Users', (
            'username', 'passwordHash', 'firstname', 'lastname', 'birthdate', 'gender', 'phonenumber', 'createdat',
            'type'),
                        (cstmr_username, pswd_hash, cstmr_firstname, cstmr_lastname, cstmr_birthdate, cstmr_gender,
                         cstmr_phone_number, created_at, 'customer'))

        if res[0]:
            flash('مشتری با موفقیت اضافه شد', 'success')
            if user.type == 'admin':
                return redirect(url_for('admin_panel'))
            else:
                return redirect(url_for('employee_panel'))
        else:
            print(res)
    else:  # user not authenticated
        flash('ابتدا به حساب کاربری خود وارد شوید', 'warning')
        return redirect(url_for('login'))


@app.route('/add_account', methods=['POST'])
def add_account():
    if 'user' in session:
        user = User.from_dict(session['user'])
        if user.type in ('admin', 'employee'):
            user_id = request.form['user_id']
            account_type = request.form['type']
            account_number = []
            for _ in range(4):
                account_number.append(str(random.randint(0, 9999)).zfill(4))
            account_number = '-'.join(account_number)
            balance = 0
            created_at = datetime.datetime.now()
            res = db.insert('Accounts', ('userId', 'accountNumber', 'balance', 'type', 'createdAt', 'status'),
                            (user_id, account_number, balance, account_type, created_at, 1))[0]
            if res:
                flash('حساب با موفقیت ایجاد شد', 'success')
                if user.type == 'admin':
                    return redirect(url_for('admin_panel'))
                else:  # user is employee
                    return redirect(url_for('employee_panel'))
            else:
                print(res)
        else:
            return "<h1>این عملیات برای شما مجاز نیست</h1>", 403

    else:  # user not authenticated
        flash('ابتدا به حساب کاربری خود وارد شوید', 'warning')
        return redirect(url_for('login'))


@app.route('/edit_user/<int:user_id>/', methods=['POST'])
def edit_user(user_id):
    if 'user' in session:
        user = User.from_dict(session['user'])
        if user.type in ('admin', 'employee'):
            editing_user = db.select('Users', filters=f"userId = '{user_id}'", Model=User)[0][0]
            username = request.form['username']
            first_name = request.form['first_name']
            last_name = request.form['last_name']
            phone_number = request.form['phone_number']
            birthdate = request.form['birthdate']
            records = db.select('Users', ['username'])[0]
            usernames = [record[0] for record in records]
            if username in usernames and username != editing_user.username:
                flash('این نام کاربری قبلا استفاده شده', 'danger')
                if user.type == 'admin':
                    return redirect(url_for('admin_panel'))
                elif user.type == 'employee':
                    return redirect(url_for('employee_panel'))
            else:
                editing_user.username = username
                editing_user.first_name = first_name
                editing_user.last_name = last_name
                editing_user.phone_number = phone_number
                editing_user.birthdate = birthdate
                editing_user.save()
                if editing_user.type == 'employee':
                    flash('مشخصات کارمند با موفقیت به روز شدند', 'success')
                else:
                    flash('مشخصات مشتری با موفقیت به روز شدند', 'success')
                if user.type == 'admin':
                    return redirect(url_for('admin_panel'))
                elif user.type == 'employee':
                    return redirect(url_for('employee_panel'))
        else:
            return "<h1>این عملیات برای شما مجاز نیست</h1>", 403

    else:  # user not authenticated
        flash('ابتدا به حساب کاربری خود وارد شوید', 'warning')
        return redirect(url_for('login'))


@app.route('/delete_user/<int:user_id>/', methods=['POST'])
def delete_user(user_id):
    if 'user' in session:
        user = User.from_dict(session['user'])
        if user.type in ('admin', 'employee'):
            deleted_user = db.select('Users', filters=f"userId = {user_id}", Model=User)[0][0]
            res = db.delete('Users', filters=f"userId = {user_id}")[0]
            if res:
                if deleted_user.type == 'employee':
                    flash(f'کارمند "{deleted_user}" با موفقیت حذف شد', 'success')
                else:
                    flash(f'مشتری "{deleted_user}" با موفقیت حذف شد', 'success')
                if user.type == 'admin':
                    return redirect(url_for('admin_panel'))
                elif user.type == 'employee':
                    return redirect(url_for('employee_panel'))
        else:
            return "<h1>این عملیات برای شما مجاز نیست</h1>", 403

    else:  # user not authenticated
        flash('ابتدا به حساب کاربری خود وارد شوید', 'warning')
        return redirect(url_for('login'))


@app.route('/edit_account/<int:account_id>', methods=['POST'])
def edit_account(account_id):
    if 'user' in session:
        user = User.from_dict(session['user'])
        editing_account = db.select('Accounts', filters=f"accountId = '{account_id}'", Model=Account)[0][0]
        if user.type in ('admin', 'employee') or (user.type == 'customer' and editing_account.user_id == user.user_id):
            if user.type == 'customer':
                name = request.form['name']
                editing_account.name = name
            else:
                user_id = request.form['user_id']
                type = request.form['type']
                account_number = request.form['account_number']
                balance = request.form['balance']
                status = request.form['status']
                name = request.form['name']
                editing_account.user_id = user_id
                editing_account.type = type
                editing_account.account_number = account_number
                editing_account.balance = balance
                editing_account.name = name
                editing_account.status = status
            editing_account.save()

            flash('حساب با موفقیت به روز شد', 'success')
            if user.type == 'admin':
                return redirect(url_for('admin_panel'))
            elif user.type == 'employee':
                return redirect(url_for('employee_panel'))
            else:
                return redirect(url_for('customer_panel'))
        else:
            return "<h1>این عملیات برای شما مجاز نیست</h1>", 403

    else:  # user not authenticated
        flash('ابتدا به حساب کاربری خود وارد شوید', 'warning')
        return redirect(url_for('login'))


@app.route('/delete_account/<int:account_id>/', methods=['POST'])
def delete_account(account_id):
    if 'user' in session:
        user = User.from_dict(session['user'])
        deleted_account = db.select('Accounts', filters=f"accountId = '{account_id}'", Model=Account)[0][0]
        if user.type in ('admin', 'employee') or (user.type == 'customer' and deleted_account.user_id == user.user_id):
            res = db.delete('Accounts', filters=f"accountId = {account_id}")[0]
            if res:
                flash(
                    f'حساب "{deleted_account.get_owner()}" با شماره حساب {deleted_account.account_number} با موفقیت حذف شد',
                    'success')
                if user.type == 'admin':
                    return redirect(url_for('admin_panel'))
                elif user.type == 'employee':
                    return redirect(url_for('employee_panel'))
                else:
                    return redirect(url_for('customer_panel'))
        else:
            return "<h1>این عملیات برای شما مجاز نیست</h1>", 403

    else:  # user not authenticated
        flash('ابتدا به حساب کاربری خود وارد شوید', 'warning')
        return redirect(url_for('login'))


@app.route('/check_transaction', methods=['POST'])
def check_transaction():
    if 'user' in session:
        user = User.from_dict(session['user'])
        if user.type == 'customer':
            src_account_number = request.json['src_account'].split(' ')[0]
            dst_account_number = request.json['dst_account']
            amount = int(request.json['amount'])
            password = request.json['password']
            user_password = db.select('Users', columns=('passwordHash',), filters=f"userId = {user.user_id}")[0][0][0]
            src_account_obj = \
                db.select('Accounts', filters=f"accountNumber = '{src_account_number}'", Model=Account)[0][0]
            dst_account = \
                db.select('Accounts', filters=f"accountNumber = '{dst_account_number}'", Model=Account)[0]

            if dst_account:
                dst_account_obj = dst_account[0]
            else:
                return jsonify(
                    {'status': 'DNF', 'dst_account_owner': None, 'amount': amount,
                     'src_account_number': src_account_number, 'dst_account_number': dst_account_number,
                     'src_account_owner': src_account_obj.get_owner().__repr__()})

            if hashlib.sha256(password.encode('utf-8')).hexdigest() != user_password:
                return jsonify(
                    {'status': 'WP', 'dst_account_owner': dst_account_obj.get_owner().__repr__(), 'amount': amount,
                     'src_account_number': src_account_number, 'dst_account_number': dst_account_number,
                     'src_account_owner': src_account_obj.get_owner().__repr__()})

            if src_account_obj.balance >= amount:
                return jsonify(
                    {'status': 'Ok', 'dst_account_owner': dst_account_obj.get_owner().__repr__(), 'amount': amount,
                     'src_account_number': src_account_number, 'dst_account_number': dst_account_number,
                     'src_account_owner': src_account_obj.get_owner().__repr__()})
            else:
                return jsonify(
                    {'status': 'NEB', 'dst_account_owner': dst_account_obj.get_owner().__repr__(), 'amount': amount,
                     'src_account_number': src_account_number, 'dst_account_number': dst_account_number,
                     'src_account_owner': src_account_obj.get_owner().__repr__(),
                     'src_account': src_account_obj.__repr__()})
        else:
            return "<h1>این عملیات برای شما مجاز نیست</h1>", 403
    else:  # user not authenticated
        flash('ابتدا به حساب کاربری خود وارد شوید', 'warning')
        return redirect(url_for('login'))


@app.route('/new_transaction', methods=['POST'])
def new_transaction():
    if 'user' in session:
        user = User.from_dict(session['user'])
        if user.type == 'customer':
            src_account_number = request.form['src_account_number']
            dst_account_number = request.form['dst_account_number']
            amount = int(request.form['amount'])

            src_account = db.select('Accounts', filters=f"accountNumber = '{src_account_number}'", Model=Account)[0][0]
            dst_account = db.select('Accounts', filters=f"accountNumber = '{dst_account_number}'", Model=Account)[0][0]

            src_account.balance -= amount
            dst_account.balance += amount

            src_account.save()
            dst_account.save()

            created_at = datetime.datetime.now()
            status = True

            res = db.insert('Transactions', ('srcAccount', 'dstAccount', 'amount', 'status', 'createdAt'),
                            (src_account.account_id, dst_account.account_id, amount, status, created_at))
            if res[0]:
                flash('تراکنش با موفقیت انجام شد', 'success')
                return redirect(url_for('customer_panel'))
            else:
                print(res)
        else:
            return "<h1>این عملیات برای شما مجاز نیست</h1>", 403
    else:  # user not authenticated
        flash('ابتدا به حساب کاربری خود وارد شوید', 'warning')
        return redirect(url_for('login'))


@app.route('/check_loan', methods=['POST'])
def check_loan():
    if 'user' in session:
        user = User.from_dict(session['user'])
        if user.type == 'customer':
            loan_id = request.json['loan_id']
            account_id = request.json['account_id']
            amount = int(request.json['loan_amount'])
            password = request.json['loan_password']
            pswd_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
            customer_password = db.exact_exec(
                f"SELECT passwordHash FROM Users INNER JOIN Accounts ON Users.userId = Accounts.userId WHERE accountId = '{account_id}';",
                fetch=True)[1][0][0]
            if customer_password != pswd_hash:
                return jsonify({'status': 'WP'})
            else:
                loan = db.select('Loans', filters=f"loanId = '{loan_id}'", Model=Loan)[0][0]
                account = db.select('Accounts', filters=f"accountId = '{account_id}'", Model=Account)[0][0]
                today = datetime.datetime.today().date()
                if today.month == 1:
                    last_month_date = today.replace(month=12)
                else:
                    last_month_date = today.replace(month=today.month - 1)
                sum_of_settlements = db.exact_exec(
                    f"SELECT SUM(amount) FROM Transactions WHERE dstAccount = {account.account_id} AND createdAt <= TIMESTAMP '{last_month_date}';",
                    fetch=True)[1][0][0]
            try:
                sum_of_settlements = int(sum_of_settlements)
            except TypeError:
                sum_of_settlements = 0

            if (sum_of_settlements >= loan.at_least_income and amount <= 2 * sum_of_settlements) or (
                    loan.at_least_income == 0):
                return jsonify(
                    {'status': 'Ok', 'loan': loan.__repr__(), 'account_number': account.account_number,
                     'amount': amount,
                     'amount_with_profit': (100 + loan.profit) * amount / 100, 'owner': account.get_owner().__repr__(),
                     'loan_id': loan.loan_id})
            elif sum_of_settlements < loan.at_least_income:
                return jsonify(
                    {'status': 'NEI', 'at_least_income': loan.at_least_income, 'sum_of_settlements': sum_of_settlements,
                     'account': account.__repr__()})
            elif amount > 2 * sum_of_settlements:
                return jsonify(
                    {'status': 'MLA', 'amount': amount, 'max_amount': 2 * sum_of_settlements,
                     'account': account.__repr__()})
        else:
            return "<h1>این عملیات برای شما مجاز نیست</h1>", 403
    else:  # user not authenticated
        flash('ابتدا به حساب کاربری خود وارد شوید', 'warning')
        return redirect(url_for('login'))


@app.route('/new_loan_request', methods=['POST'])
def new_loan_request():
    if 'user' in session:
        user = User.from_dict(session['user'])
        if user.type == 'customer':
            loan_id = request.form['loan_id']
            loan_amount = int(request.form['loan_amount'])
            loan_account_number = request.form['loan_account_number']
            account = db.select('Accounts', filters=f"accountNumber = '{loan_account_number}'", Model=Account)[0][0]
            res = db.insert('AccountLoans', ('accountId', 'loanId', 'amount', 'paid', 'status'),
                            (account.account_id, loan_id, loan_amount, 0, 0))
            if res[0]:
                flash('درخواست وام با موفقیت ثبت شد', 'success')
                return redirect(url_for('customer_panel'))
            else:
                print(res)
        else:
            return "<h1>این عملیات برای شما مجاز نیست</h1>", 403
    else:  # user not authenticated
        flash('ابتدا به حساب کاربری خود وارد شوید', 'warning')
        return redirect(url_for('login'))


@app.route('/new_loan_type', methods=['POST'])
def new_loan_type():
    if 'user' in session:
        user = User.from_dict(session['user'])
        if user.type == 'admin':
            profit = request.form['profit']
            deadline = request.form['deadline']
            at_least_income = request.form['at_least_income']

            res = db.insert('Loans', ('profit', 'deadline', 'atLeastIncome', 'status'),
                            (profit, deadline, at_least_income, True))
            if res[0]:
                flash('وام با موفقیت اضافه شد', 'success')
                return redirect(url_for('admin_panel'))
            else:
                print(res)
        else:
            return "<h1>این عملیات برای شما مجاز نیست</h1>", 403
    else:  # user not authenticated
        flash('ابتدا به حساب کاربری خود وارد شوید', 'warning')
        return redirect(url_for('login'))


@app.route('/switch_loan_status', methods=['POST'])
def switch_loan_status():
    if 'user' in session:
        user = User.from_dict(session['user'])
        if user.type == 'admin':
            loan_id = request.form['loan_id']
            loan = db.select('Loans', filters=f"loanId = '{loan_id}'", Model=Loan)[0][0]
            if loan.status:
                loan.status = False
            else:
                loan.status = True

            res = loan.save()
            if res:
                flash('تغییر وضعیت وام با موفقیت انجام شد', 'success')
                return redirect(url_for('admin_panel'))
        else:
            return "<h1>این عملیات برای شما مجاز نیست</h1>", 403

    else:  # user not authenticated
        flash('ابتدا به حساب کاربری خود وارد شوید', 'warning')
        return redirect(url_for('login'))


@app.route('/delete_loan', methods=['POST'])
def delete_loan():
    if 'user' in session:
        user = User.from_dict(session['user'])
        if user.type == 'admin':
            loan_id = request.form['loan_id']
            res = db.delete('Loans', filters=f"loanId = '{loan_id}'")[0]
            if res:
                flash('وام با موفقیت حذف شد', 'success')
                return redirect(url_for('admin_panel'))
            else:
                print(res)
        else:
            return "<h1>این عملیات برای شما مجاز نیست</h1>", 403
    else:  # user not authenticated
        flash('ابتدا به حساب کاربری خود وارد شوید', 'warning')
        return redirect(url_for('login'))


@app.route('/accept_loan', methods=['POST'])
def accept_loan():
    if 'user' in session:
        user = User.from_dict(session['user'])
        if user.type in ('admin', 'employee'):
            account_loan_id = request.form['account_loan_id']
            password = request.form['password']
            user_password = db.select('Users', columns=('passwordHash',), filters=f"userId = '{user.user_id}'")[0][0][0]
            pswd_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
            if pswd_hash == user_password:
                account_loan = \
                    db.select('AccountLoans', filters=f"accountLoanId = '{account_loan_id}'", Model=AccountLoan)[0][0]
                if account_loan.status == 0:
                    account_loan.status = 1
                    account_loan.acceptor = user.user_id
                    account_loan.save()
                    bank_account = \
                        db.select('Accounts', filters=f"accountNumber = '{BANK_ACCOUNT_NUMBER}'", Model=Account)[0][0]
                    customer_account = \
                        db.select('Accounts', filters=f"accountId = '{account_loan.account_id}'", Model=Account)[0][0]

                    bank_account.balance -= account_loan.amount
                    customer_account.balance += account_loan.amount

                    bank_account.save()
                    customer_account.save()

                    created_at = datetime.datetime.now()
                    status = True

                    res = db.insert('Transactions', ('srcAccount', 'dstAccount', 'amount', 'status', 'createdAt'),
                                    (bank_account.account_id, customer_account.account_id, account_loan.amount, status,
                                     created_at))
                    if res[0]:
                        flash('وام با موفقیت تایید شد', 'success')
                        if user.type == 'admin':
                            return redirect(url_for('admin_panel'))
                        elif user.type == 'employee':
                            return redirect(url_for('employee_panel'))
                    else:
                        print(res)
                else:
                    return "<h1>این درخواست قبلا تایید شده</h1>", 403
            else:
                flash('کلمه عبور اشتباه است', 'danger')
                if user.type == 'admin':
                    return redirect(url_for('admin_panel'))
                elif user.type == 'employee':
                    return redirect(url_for('employee_panel'))
        else:
            return "<h1>این عملیات برای شما مجاز نیست</h1>", 403

    else:  # user not authenticated
        flash('ابتدا به حساب کاربری خود وارد شوید', 'warning')
        return redirect(url_for('login'))


@app.route('/pay_instalment', methods=['POST'])
def pay_instalment():
    if 'user' in session:
        user = User.from_dict(session['user'])
        if user.type == 'customer':
            account_loan_id = request.form['account_loan_id']
            password = request.form['instalmentPassword']
            account_loan = \
                db.select('AccountLoans', filters=f"accountLoanId = '{account_loan_id}'", Model=AccountLoan)[0][0]
            customer_password = db.exact_exec(
                f"SELECT passwordHash FROM Users INNER JOIN Accounts ON Users.userId = Accounts.userId WHERE accountId = '{account_loan.get_account().account_id}';",
                fetch=True)[1][0][0]
            pswd_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
            if pswd_hash == customer_password:
                instalment_amount = account_loan.get_instalment()
                bank_account = \
                    db.select('Accounts', filters=f"accountNumber = '{BANK_ACCOUNT_NUMBER}'", Model=Account)[0][0]
                customer_account = \
                    db.select('Accounts', filters=f"accountId = '{account_loan.account_id}'", Model=Account)[0][0]

                bank_account.balance += instalment_amount
                customer_account.balance -= instalment_amount
                account_loan.paid += instalment_amount

                if account_loan.paid == account_loan.get_amount_with_profit():
                    account_loan.status = 2

                bank_account.save()
                customer_account.save()
                account_loan.save()

                created_at = datetime.datetime.now()
                status = True

                res = db.insert('Transactions', ('srcAccount', 'dstAccount', 'amount', 'status', 'createdAt'),
                                (customer_account.account_id, bank_account.account_id, instalment_amount, status,
                                 created_at))
                if res[0]:
                    flash('با موفقیت پرداخت شد', 'success')
                    return redirect(url_for('customer_panel'))
                else:
                    print(res)
            else:
                flash('کلمه عبور اشتباه است', 'danger')
                return redirect(url_for('customer_panel'))

        else:
            return "<h1>این عملیات برای شما مجاز نیست</h1>", 403

    else:  # user not authenticated
        flash('ابتدا به حساب کاربری خود وارد شوید', 'warning')
        return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(debug=True)
