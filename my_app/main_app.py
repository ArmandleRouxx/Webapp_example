from flask import render_template, request, redirect, session, Blueprint
from flask_login import login_required, current_user, login_user, logout_user
from . import db
from .models import User
from hashlib import sha512


main_app = Blueprint('main_app', __name__)


# Directs user to login if not logged in otherwise to home page
@main_app.route('/')
def index():
    if not session.get('name'):
        return redirect('/login')
    return redirect('/home')


# Register page allows user to add username and sport
@main_app.route("/register")
def register():
    return render_template('register.html')
    

# Render login page for user
@main_app.route("/login")
def login():
    return render_template('login.html')


# Log user out and return to them to login page
@main_app.route("/logout")
def logout():
    logout_user()
    session['name'] = None
    return redirect('/login')


# Provides user with home page if they are logged in
@main_app.route('/home')
@login_required
def home_page():
    username = session.get('name')
    return render_template('sign_in_home.html', username=username)


# Check user login data and log them in.
@main_app.route('/submitlogin', methods=["POST"])
def submit_login():
    username = request.form.get('username')
    password = request.form.get('password')
    password = sha512(password.encode('utf-8')).hexdigest()
    print(username)
    user = User.query.filter_by(username=username).first()
    print(user)
    if user and user.password == password:     
        session['name'] = username
        login_user(user) 
        return redirect("/home")
    return render_template('login_fail.html', message="Login has failed!", fail_type='Login', route='/login')


# Determine if user entered valid credential and 
@main_app.route('/submitregister', methods=["POST"])
def submit_register():
    username = request.form.get('username')
    password = request.form.get('password')
    confirm_pw = request.form.get('conf_pw')
    if password != confirm_pw or not auth_password(password):
        return render_template('register_fail.html', 
                               message="Please note that your password entries have to match and should be more than 8 characters.",
                               fail_type='Register', route='/register')
    password = sha512(password.encode('utf-8')).hexdigest()
    try:
        new_user = User(username=username, password=password, fav_colour=None, birth_date=None)
        db.session.add(new_user)
        db.session.commit()
    except:
        return render_template('register_fail.html', message="Username in unavailable!",
                               fail_type='Register', route='/register')
    new_user = User.query.filter_by(username = username).first()
    if new_user:
        login_user(new_user)
    return render_template('sign_in_home.html', message= "Register Success",
                           username=username)
        
        

# Return html file displaying users for post request and returns JSON of users for get request
@main_app.route('/users', methods=["POST", "GET"])
@login_required
def users():
    result = User.query.order_by(User.username).all()
    print(result)
    if request.method == "POST":
        output = []
        output.append("Users")
        for user in result:
            output.append(f"{user.username}")
        return render_template('users.html', users=output)
    elif request.method == "GET":
        output = {}
        for i, user in enumerate(result):
            output[i] = {'username': user.username,
                         'fav_colour' : user.fav_colour,
                         'birth_date': user.birth_date}
        return output
    

# Render page for user to edit their data
@main_app.route('/edit_user_data')
@login_required
def edit_user_data():
    username = session['name']
    user = User.query.filter_by(username = username).first()
    colour = user.fav_colour
    return render_template('add_user_data.html', colour=colour)


# Submit user data and add to database
@main_app.route('/submitdata', methods=['POST'])
@login_required
def update_user_data():
    birth_date = request.form.get('birth_date')
    colour = request.form.get('colour')
    user = User.query.filter_by(username=current_user.username).first()
    print(user)
    # user.birth_date = birth_date
    user.fav_colour = colour
    db.session.commit()
    return redirect('/home')
    

# Basic authentication for password
def auth_password(password):
    if 8 <= len(password) <= 24:
        return True
    return False
        
    
    
if __name__ == '__main__':
    main_app.run(debug=True)