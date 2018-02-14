from flask import Flask, flash, redirect, url_for, render_template, request, session, abort
import sqlite3 as lite
app = Flask(__name__)

#@app.route("/")
#def render_login_prompt():
#    return render_template('login.html')

@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        #TODO: authentication
        return redirect(url_for('render_posts_page'))
    return render_template('login.html', error=error)

@app.route("/posts")
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
