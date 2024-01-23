import hashlib

from flask import Flask, render_template, request, flash, redirect, url_for

from DatabaseHandler import Database
from DatabaseHandler.models import User
from constants import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASS

app = Flask(__name__)
app.static_url_path = ""
app.static_folder = "templates/static/"
app.template_folder = "templates"
app.secret_key = '1234'

db = Database(DB_HOST, DB_PORT, DB_NAME.lower(), DB_USER, DB_PASS)
USER = None


@app.route('/', methods=['GET', 'POST'])
def login():
    global USER
    if request.method == "GET":
        return render_template('./login.html')
    else:  # POST
        username = request.form['username']
        password = request.form['password']
        pswd_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
        res = db.select('Users', Model=User, filters=f"username = '{username}' AND passwordHash = '{pswd_hash}'")
        if res[0]:  # login successful !
            obj = res[0][0]
            USER = obj
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
    return redirect(url_for('login'))


@app.route('/update_profile/', methods=['POST'])
def update_profile():
    global USER
    USER.username = request.form['username']
    USER.first_name = request.form['first_name']
    USER.last_name = request.form['last_name']
    USER.phone_number = request.form['phone_number']
    USER.birthdate = request.form['birthdate']
    USER.save('Users')

    if USER.type == 'admin':
        return redirect(url_for('admin_panel'))
    elif USER.type == 'employee':
        return render_template('./employee_dashboard.html', user=USER)
    elif USER.type == 'user':
        return render_template('./user_dashboard.html', user=USER)


@app.route('/admin/')
def admin_panel():
    global USER
    context = {
        'user': USER,
    }
    return render_template('./admin_dashboard.html', **context)


@app.route('/employee')
def employee_panel():
    return render_template('./employee_dashboard.html')


@app.route('/user')
def user_panel():
    return render_template('./user_dashboard.html')


if __name__ == "__main__":
    app.run(debug=True)
