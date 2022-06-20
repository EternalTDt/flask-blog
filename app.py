from flask import Flask, render_template, flash, session, request, redirect
from flask_bootstrap import Bootstrap
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from flask_ckeditor import CKEditor
import yaml
import os
from datetime import timedelta


app = Flask(__name__)
Bootstrap(app)
CKEditor(app)


db = yaml.safe_load(open('db.yaml'))
app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB'] = db['mysql_db']
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
app.config['SECRET_KEY'] = os.urandom(24)
mysql = MySQL(app)


@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=60)


@app.route('/')
def index():
    cursor = mysql.connection.cursor()
    all_posts = cursor.execute("SELECT * FROM post")
    if all_posts > 0:
        posts = cursor.fetchall()
        cursor.close()
        return render_template('index.html', posts=posts)
    return render_template('index.html', posts=None)


@app.route('/about/')
def about():
    return render_template('about.html')


@app.route('/my-posts/')
def my_posts():
    author = session['first_name'] + ' ' + session['last_name']
    cursor = mysql.connection.cursor()
    get_author_posts = cursor.execute("SELECT * FROM post WHERE author = %s", [author])
    if get_author_posts > 0:
        my_posts = cursor.fetchall()
        return render_template('my-posts.html', my_posts=my_posts)
    else:
        return render_template('my-posts.html', my_posts=None)


@app.route('/posts/<int:id>')
def get_posts(id):
    cursor = mysql.connection.cursor()
    post_find = cursor.execute("SELECT * FROM post WHERE post_id = {}".format(id))
    if post_find > 0:
        post = cursor.fetchone()
        return render_template('posts.html', post=post)
    return 'Post is not found'


@app.route('/add-post/', methods=['GET', 'POST'])
def add_post():
    if request.method == 'POST':
        post_form = request.form
        title = post_form['title']
        body = post_form['body']
        author = session['first_name'] + ' ' + session['last_name']
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO post (title, body, author) VALUES (%s, %s, %s)", (title, body, author))
        mysql.connection.commit()
        cursor.close()
        flash('Post was successfully created!', 'success')
        return redirect('/')
    return render_template('write-post.html')


@app.route('/edit-post/<int:id>', methods=['GET', 'POST'])
def edit_post(id):
    if request.method == 'POST':
        cursor = mysql.connection.cursor()
        title = request.form['title']
        body = request.form['body']
        cursor.execute("UPDATE post SET title = %s, body = %s WHERE post_id = %s", (title, body, id))
        mysql.connection.commit()
        cursor.close()
        flash('Post was updated successfully!', 'success')
        return redirect('/posts/{}'.format(id))
    cursor = mysql.connection.cursor()
    get_post = cursor.execute("SELECT * from post WHERE post_id = {}".format(id))
    if get_post > 0:
        post = cursor.fetchone()
        post_form = {}
        post_form['title'] = post['title']
        post_form['body'] = post['body']
        return render_template('edit-post.html', post_form=post_form)


@app.route('/delete-post/<int:id>')
def delete_post(id):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM post WHERE post_id = {}".format(id))
    mysql.connection.commit()
    flash("Post was successfully deleted!", 'success')
    return redirect('/my-posts/')


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
        flash('User ' + user_details['username'] + ' was successfully registered!', 'success')
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
                flash('Welcome ' + session['first_name'] + '! You have successfully logged in!', 'success')
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
    session.clear()
    flash('You have successfully logged out', 'info')
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)