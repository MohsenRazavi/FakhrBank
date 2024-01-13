from flask import Flask, render_template

app = Flask(__name__)
app.static_folder = 'templates/static/'

@app.route('/')
def login():
    return render_template('./login.html')

@app.route('/admin')
def admin_panel():
    return render_template('./admin_main_page.html')

if __name__ == "__main__":
    app.run(debug=True)
