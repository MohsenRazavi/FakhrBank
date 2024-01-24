import hashlib
import datetime

from flask import Flask, render_template, request, flash, redirect, url_for, session

from DatabaseHandler import Database
from DatabaseHandler.models import User
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
                return render_template('./employee_dashboard.html', user=user)
            elif user.type == "user":
                return render_template('./user_dashboard.html', user=user)
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
            if obj.first_name and obj.last_name:
                flash(f'{obj.first_name} {obj.last_name}  خوش آمدید !', 'success')
            else:
                flash(f'{obj.username} خوش آمدید !', 'success')
            if obj.type == "admin":
                return redirect(url_for('admin_panel'))
            elif obj.type == "employee":
                return render_template('./employee_dashboard.html', user=obj)
            elif obj.type == "user":
                return render_template('./user_dashboard.html', user=obj)
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
        if test_username in usernames:
            flash('این نام کاربری قبلا استفاده شده', 'danger')
            if user.type == 'admin':
                return redirect(url_for('admin_panel'))
            elif user.type == 'employee':
                return redirect(url_for('employee_panel'))
            else:
                return redirect(url_for('user_panel'))
        else:
            user.username = test_username
            user.first_name = request.form['first_name']
            user.last_name = request.form['last_name']
            user.phone_number = request.form['phone_number']
            user.birthdate = request.form['birthdate']
            user.save('Users')
            session['user'] = user.to_dict()
            flash('مشخصات کاربری با موفقیت به روز شدند', 'success')
            if user.type == 'admin':
                return redirect(url_for('admin_panel'))
            elif user.type == 'employee':
                return redirect(url_for('employee_panel'))
            elif user.type == 'user':
                return redirect(url_for('user_panel'))
    else:  # user not authenticated
        flash('ابتدا به حساب کاربری خود وارد شوید', 'warning')
        return redirect(url_for('login'))


@app.route('/admin/')
def admin_panel():
    if 'user' in session:
        user = User.from_dict(session['user'])
        context = {
            'user': user,
        }
        return render_template('./admin_dashboard.html', **context)
    else:  # user not authenticated
        flash('ابتدا به حساب کاربری خود وارد شوید', 'warning')
        return redirect(url_for('login'))


@app.route('/employee')
def employee_panel():
    if 'user' in session:
        user = User.from_dict(session['user'])
        context = {
            'user': user,
        }
        return render_template('./employee_dashboard.html', **context)
    else:  # user not authenticated
        flash('ابتدا به حساب کاربری خود وارد شوید', 'warning')
        return redirect(url_for('login'))


@app.route('/user')
def user_panel():
    if 'user' in session:
        user = User.from_dict(session['user'])
        context = {
            'user': user,
        }
        return render_template('./employee_dashboard.html', **context)
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
            context['emp_username'] = emp_username
            context['emp_firstname'] = emp_firstname
            context['emp_lastname'] = emp_lastname
            context['emp_phone_number'] = emp_phone_number
            flash('این نام کاربری قبلا استفاده شده', 'danger')
            return redirect(url_for('admin_panel', **context))
        if emp_password1 != emp_password2:
            context['emp_username'] = emp_username
            context['emp_firstname'] = emp_firstname
            context['emp_lastname'] = emp_lastname
            context['emp_phone_number'] = emp_phone_number
            flash('کلمه عبور و تکرار آن یکی نیستند', 'danger')
            return redirect(url_for('admin_panel', **context))
        else:
            pswd_hash = hashlib.sha256(emp_password1.encode('utf-8')).hexdigest()
        created_at = datetime.datetime.now()
        res = db.insert('Users', ('username', 'passwordHash', 'firstname', 'lastname', 'birthdate', 'gender', 'phonenumber', 'createdat', 'type'),
                  (emp_username, pswd_hash, emp_firstname, emp_lastname, emp_birthdate, emp_gender, emp_phone_number, created_at, 'employee'))

        if res[0]:
            flash('کارمند با موفقیت اضافه شد', 'success')
            return redirect(url_for('admin_panel', **context))
        else:
            print(res)


if __name__ == "__main__":
    app.run(debug=True)
