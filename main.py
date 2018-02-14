from flask import Flask, flash, redirect, url_for, render_template, request, session, abort
from functools import wraps
import sqlite3 as lite

app = Flask(__name__)
app.secret_key = 'rcp54mpnoO' # secret key required for sessions

# Checks the session to determine if a user is logged in
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            return redirect(url_for('login'))
    return wrap

# '/' route used for the login page
@app.route('/', methods=['GET', 'POST'])
# Handle authentication through the login page
def login():
    error = None
    # If a username and password are provided, check them against the database,
    # and login if they are valid
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
        # if credentials provided are valid, log in user to the new session
        # and redirect to the posts page
        if isAuthenticated:
            session['logged_in'] = True
            return redirect(url_for('render_posts_page'))
        # if credentials provided are invalid, display an error on login page
        else:
            error = "Invalid login credentials"

    return render_template('login.html', error=error)

# Is the given username found and does the given password match?
def checkAuthentication(result, provided_username, provided_password):
    for user in result:
        # Required because database stores all data in unicode
        username_in_db = user[0].encode('utf-8')
        password_in_db = user[1].encode('utf-8')
        if provided_username == username_in_db and provided_password == password_in_db:
            return True
    return False

# '/posts' used for page to view and create posts
@app.route("/posts")
@login_required
# Show previously submitted posts, queried from the database
def render_posts_page():
    con = None
    previous_posts = None
    try:
        # Query the database for all previous posts
        con = lite.connect('users_and_posts.db')
        cur = con.cursor()
        cur.execute("SELECT CONTENT FROM POSTS")
        # Convert the previous posts from Unicode to a readable format
        previous_posts = get_posts_content(cur.fetchall())
    except lite.Error, e:
        print "Error %s:" % e.args[0]
    finally:
        if con:
            con.close()
    # re-render the posts page with any new posts
    return render_template('posts.html', previous_posts=previous_posts)

# Convert each of the posts from unicode and put into a list to be displayed
def get_posts_content(result):
    contents = []
    for row in result:
        contents.append(row[0].encode('utf-8'))
    return contents


#'/submit/post' used to submit a new post when the POST http method is called
# and always redirects back to the posts page
@app.route("/submit/post", methods=['GET', 'POST'])
@login_required
# If a new posted was submitted, add to the existing list of posts
def submit_post():
    # If the url was called using POST method, the user submitted a new post.
    if (request.method == 'POST'):
        add_post_to_database(request.form['new_post'])
    return redirect(url_for('render_posts_page'))


# Add the new post to the database
def add_post_to_database(post_content):
    con = None
    try:
        # Call an insert statement to add a new row to the Posts table
        # First argument is the unique id for the post. Setting the param to
        # null causes the id to autoincrement
        con = lite.connect('users_and_posts.db')
        cur = con.cursor()
        cur.execute("INSERT INTO Posts VALUES(NULL," + "'" + post_content + "'" + ")")
        # Commit the changes to the db
        con.commit()
    except lite.Error, e:
        print "Error %s:" % e.args[0]
    finally:
        if con:
            con.close()

# Print any internal errors for debugging
@app.errorhandler(500)
def internal_error(error):
    print error

if __name__ == "__main__":
    app.run()
