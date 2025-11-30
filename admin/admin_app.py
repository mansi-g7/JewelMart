# from flask import Flask, render_template

# app = Flask(__name__, template_folder='templates')

# @app.route('/')
# def admin_home():
#     return "Admin Dashboard Running!"

# if __name__ == '__main__':
#     app.run(debug=True)
# # //
from flask import Flask, render_template
import dashboard  # your dashboard.py

app = Flask(__name__, template_folder='templates')

@app.route('/dashboard')
def admin_dashboard():
    return render_template("dashboard.html")
