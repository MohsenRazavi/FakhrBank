import datetime
import hashlib
import random

from flask import Flask, render_template, request, flash, redirect, url_for, session

from DatabaseHandler import Database
from DatabaseHandler.models import User, Account
from constants import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASS

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
            context = {
                'user': user,
                'employees': employees,
                'customers': customers,
                'accounts': accounts,
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
        if user.type == 'employee':
            context = {
                'user': user,
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
        if user.type == 'customer':
            context = {
                'user': user,
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
            return redirect(url_for('admin_panel', **context))
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
def delete(user_id):
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


if __name__ == "__main__":
    app.run(debug=True)
