from flask import Flask, render_template, flash, session, redirect, request, url_for, jsonify
from datetime import timedelta
from helper import apology
from flask_socketio import SocketIO, emit, send
from flask_session import Session
from database import Database

app = Flask(__name__)
app.config["SECRET_KEY"] = b'9\xfa\x1e\x8e\xf4\x97A&\x03u\xbc\x90\x91\xc1\xef\xe5'
app.config['SESSION_TYPE'] = 'filesystem'
app.permanent_session_lifetime = timedelta(days=31)

socketio = SocketIO(app)
Session(app)


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    # Clear session content
    if "user" in session:
        return redirect("/")

    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("Must provide user name", 400)

        # Ensure password was submitted
        if not request.form.get("password"):
            return apology("Must provide password", 400)

        # Remember which user was logged in
        username = request.form.get("username")
        if db.user_exist(username):
            session.permanent = True
            session["user"] = username
        else:
            return apology("User not found", 400)

        # Flash message
        flash("Logged In")

        # Redirect to homepage
        return redirect("/")
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    # Forget user_id
    session.pop("user", None)

    # Flash message
    flash("logged Out")

    # Redirect to homepage
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # Ensure user input arguments
        username = request.form.get("username")
        password = request.form.get("password")
        confirm = request.form.get("confirm")

        if username==None:
            return apology("Must provide user name", 400) 
        elif password==None:
            return apology("Must provide password", 400) 
        elif confirm==None:
            return apology("Must confirm password again", 400) 
        elif password!=confirm:
            return apology("Password not match", 400)

        # Ensure the username is never used or save to to db
        if db.user_exist(username):
            return apology("User name used", 400)
        else:
            db.add_user(username, password)

        # flash and redirect to login page
        flash("Registered!")
        return redirect(url_for("login"))
    else:
        return render_template("register.html")

@app.route("/explore", methods=["GET", "POST"])
def explore():
    if request.method == "POST":
        return redirect("/")
    else:
        return render_template("explore.html")

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    
    # get user
    if 'user' not in session:
        flash("Log in first")
        redirect(url_for("addCourse"))
    username = session['user']

    if request.method == "POST":
        # get course name
        course = request.form.get('course_name')

        # delete course
        db.delete_course(course, username)

        # reload page
        return redirect(url_for("dashboard"))

    # fetch user data
    courses = db.get_all_course(username)
    print(courses, "\n\n\n")

    # get nearest ddls of each course
    ddls = db.get_nearest_ddl(courses)
    all_information = []
    for i in range(len(courses)):
        all_information.append([courses[i], ddls[i]])
    
    return render_template("dashboard.html", all_information=all_information)

ddls = []
dates = []
@app.route("/addCourse", methods=["GET", "POST"])
def addClass():

    global ddls
    global dates

    if request.method == "POST":

        if 'user' not in session:
            flash("Log in first")
            redirect(url_for("addCourse"))

        coursename = request.form.get("courseName")
        instituteName = request.form.get("instituteName")
        courseAbout = request.form.get("courseAbout")
        enrollDate = request.form.get("enrollDate")
        endDate = request.form.get("endDate")

        if endDate=='':
            endDate = "Unlimited"

        ddl_pairs = {}
        print(ddls)
        print(dates)
        for i in range(len(ddls)):
            ddl_pairs[ddls[i]] = dates[i]

        # course name
        """print("coursename: ", coursename, "\n",
            "instituteName: ", instituteName, "\n",
            "courseAbout: ", courseAbout, "\n",
            "enrollDate: ", enrollDate, "\n",
            "endDate: ", endDate, "\n",
            "ddls: ", ddl_pairs, "\n")"""

        result = db.add_course(coursename, instituteName, courseAbout, enrollDate, endDate, ddl_pairs, session['user'])
        ddl_pairs = {}
        if not result:
            return apology("course repeated", 400)
        
    return render_template("addCourse.html")

@socketio.on('newddl', namespace="/addCourse")
def handle_message(message):
    print(message + '\n')
    ddls.append(message)

@socketio.on('newdate', namespace="/addCourse")
def handle_message(message):
    dates.append(message)

if __name__ == "__main__":
    db = Database()
    socketio.run(app, debug=True)