from flask import Flask, render_template

app = Flask(__name__)
app.static_folder = 'templates/static/'

@app.route('/')
def login():
    return render_template('./login.html')

@app.route('/admin')
def admin_panel():
    return render_template('./admin_dashboard.html')

@app.route('/employee')
def employee_panel():
    return render_template('./employee_dashboard.html')

@app.route('/user')
def user_panel():
    return render_template('./user_dashboard.html')

@app.route('/admin_profile')
def admin_profile():
    return render_template('./admin_profile.html')

@app.route('/employee_profile')
def employee_profile():
    return render_template('./employee_profile.html')

@app.route('/user_profile')
def user_profile():
    return render_template('./user_profile.html')

@app.route('/admin_customers_list')
def admin_customer_list():
    return render_template('./admin_customers_list.html')

if __name__ == "__main__":
    app.run(debug=True)
