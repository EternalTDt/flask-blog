from flask import Flask, render_template
from flask_bootstrap import Bootstrap


app = Flask(__name__)
Bootstrap(app)


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
    return render_template('register.html')


@app.route('/login/', methods=['GET', 'POST'])
def login():
    return render_template('login.html')


@app.route('/logout/')
def logout():
    return render_template('logout.html')


if __name__ == '__main__':
    app.run(debug=True)