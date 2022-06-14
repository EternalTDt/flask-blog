from flask import Flask, render_template, flash, session, request, redirect
from flask_bootstrap import Bootstrap
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
import yaml
import os


app = Flask(__name__)
Bootstrap(app)


db = yaml.safe_load(open('db.yaml'))
app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB'] = db['mysql_db']
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
app.config['SECRET_KEY'] = os.urandom(24)
mysql = MySQL(app)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/about/')
def about():
    return render_template('about.html')


@app.route('/my-posts/')
def my_posts():
    return render_template('my-posts.html')


@app.route('/posts/<int:id>')
def get_posts(id):
    return render_template('posts.html', post_id=id)


@app.route('/write-post/', methods=['GET', 'POST'])
def write_post():
    return render_template('write-post.html')


@app.route('/edit-post/<int:id>', methods=['GET', 'POST'])
def edit_post(id):
    return render_template('edit-post.html', post_id=id)


@app.route('/delete-post/<int:id>', methods=['POST'])
def delete_post():
    return 'Successfully deleted!'


@app.route('/registration/', methods=['GET', 'POST'])
def registration():
    if request.method == 'POST':
        user_details = request.form
        if user_details['password'] != user_details['passwordConfirm']:
            flash('Passwords mismatch! Please, re-enter your password', 'danger')
            return render_template('register.html')
        if len(user_details['password']) < 6:
            flash('Your password is too short!', 'danger')
            return render_template('register.html')
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO user(first_name, last_name, username, email, password) VALUES(%s, %s, %s, %s, %s)",
        (user_details['firstName'], user_details['lastName'], user_details['username'], user_details['email'],
        generate_password_hash(user_details['password'])))
        mysql.connection.commit()
        cursor.close()
        flash('User ' + user_details['username'] + ' successfully registered!', 'success')
        return redirect('/login')
    return render_template('register.html')


@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_details = request.form
        username = user_details['username']
        cursor = mysql.connection.cursor()
        check_username = cursor.execute("SELECT * FROM user WHERE username = %s", ([username]))
        if check_username > 0:
            user = cursor.fetchone()
            if check_password_hash(user['password'], user_details['password']):
                session['login'] = True
                session['first_name'] = user['first_name']
                session['last_name'] = user['last_name']
                flash('Welcome ' + session['first_name'] + '! You have been successfully logged in!', 'success')
            else:
                cursor.close()
                flash('Password is incorrect!', 'danger')
                return render_template('login.html')
        else:
            cursor.close()
            flash('User does not exists!', 'danger')
            return render_template('login.html')
        cursor.close()
        return redirect('/')
    return render_template('login.html')


@app.route('/logout/')
def logout():
    return render_template('logout.html')


if __name__ == '__main__':
    app.run(debug=True)