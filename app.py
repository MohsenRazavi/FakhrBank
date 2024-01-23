import hashlib

from flask import Flask, render_template, request, flash, redirect, url_for

from DatabaseHandler import Database
from DatabaseHandler.models import User
from constants import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASS

app = Flask(__name__)
app.static_folder = 'templates/static/'
app.secret_key = '1234'

db = Database(DB_HOST, DB_PORT, DB_NAME.lower(), DB_USER, DB_PASS)


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == "GET":
        return render_template('./login.html')
    else:  # POST
        username = request.form['username']
        password = request.form['password']
        pswd_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
        res = db.select('Users', Model=User, filters=f"username = '{username}' AND passwordHash = '{pswd_hash}'")
        print(res)
        if res[0]:  # login successful !
            obj = res[0][0]
            if obj.first_name and obj.last_name:
                flash(f'خوش آمدید{obj.first_name} {obj.last_name}', 'success')
            else:
                flash(f'خوش آمدید {obj.username}', 'success')
            if obj.type == "admin":
                return admin_panel(obj)
            elif obj.type == "employee":
                return redirect(url_for('employee_panel'))
            elif obj.type == "user":
                return redirect(url_for('user_panel'))
            else:
                flash('User not found', 'danger')
                return render_template('./login.html')


@app.route('/logout')
def logout():
    return redirect(url_for('login'))


@app.route('/update_profile')
def update_profile():
    return render_template('')


def admin_panel(admin):
    context = {
        'user_obj': admin,
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
