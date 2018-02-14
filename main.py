from flask import Flask, flash, redirect, url_for, render_template, request, session, abort
from functools import wraps
import sqlite3 as lite

app = Flask(__name__)
app.secret_key = 'rcp54mpnoO'

# Checks the session to determine if a user is logged in
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            return redirect(url_for('login'))
    return wrap

@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        provided_username = request.form['username']
        provided_password = request.form['password']
        isAuthenticated = False
        try:
            con = lite.connect('users_and_posts.db')
            cur = con.cursor()
            cur.execute("SELECT * FROM USERS")
            isAuthenticated = checkAuthentication(cur.fetchall(),
                                                    provided_username,
                                                    provided_password)
        except lite.Error, e:
            print "Error %s:" % e.args[0]
        finally:
            if con:
                con.close()
        if isAuthenticated:
            session['logged_in'] = True
            return redirect(url_for('render_posts_page'))
        else:
            error = "Invalid login credentials"

    return render_template('login.html', error=error)

def checkAuthentication(result, provided_username, provided_password):
    for user in result:
        username_in_db = user[0].encode('utf-8')
        password_in_db = user[1].encode('utf-8')
        if provided_username == username_in_db and provided_password == password_in_db:
            return True


    return False

@app.route("/posts")
@login_required
#@basic_auth.required
def render_posts_page():
    con = None
    previous_posts = None
    try:
        con = lite.connect('users_and_posts.db')
        cur = con.cursor()
        cur.execute("SELECT CONTENT FROM POSTS")
        previous_posts = get_posts_content(cur.fetchall())
    except lite.Error, e:
        print "Error %s:" % e.args[0]
    finally:
        if con:
            con.close()
    return render_template('posts.html', previous_posts=previous_posts)

def get_posts_content(result):
    contents = []
    for row in result:
        contents.append(row[0].encode('utf-8'))
    return contents


@app.route("/submit/post", methods=['GET', 'POST'])
@login_required
def submit_post():
    #TODO: submit post to db
    if (request.method == 'POST'):
        add_post_to_database(request.form['new_post'])
    return redirect(url_for('render_posts_page'))


# Add the new post to the database
def add_post_to_database(post_content):
    con = None
    try:
        con = lite.connect('users_and_posts.db')
        cur = con.cursor()
        cur.execute("INSERT INTO Posts VALUES(NULL," + "'" + post_content + "'" + ")")
        con.commit()
    except lite.Error, e:
        print "Error %s:" % e.args[0]
    finally:
        if con:
            con.close()

@app.errorhandler(500)
def internal_error(error):
    print error

if __name__ == "__main__":
    app.run()
