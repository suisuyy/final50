import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from helpers import login_required, allowed_file, apology

UPLOAD_FOLDER = '/home/cyl/final-project-cs50/static/files'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif','zip'])

# Configure application
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True
#not support file >30M
app.config['MAX_CONTENT_LENGTH'] = 30 * 1024 * 1024

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///noty.db")

# if user not log in,they are noregister,set session[user_id]=0 default
#print("***session: ",type(session),session)
#session["user_id"] = 0

@app.route("/file",methods=["GET"])
def file():
    if  "user_id" not in session:
        session["user_id"]=0
    filelist=[]
    filerows=db.execute("SELECT * FROM files WHERE user_id='{}'".format(session["user_id"]))
    for row in filerows:
        filelist.insert(0,[ row['name'],row['size'],row['time'],row['id'] ])

    return render_template("file.html",filelist=filelist)


@app.route("/savefile",methods=["GET","POST"])
def savefile():
    if request.method =="GET":
        return render_template("file.html")
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return apology("file not found",404)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '' or request.form.get("filename") == '':
            flash('No selected file')
            return apology("not found file name",404)

        if db.execute("SELECT * FROM files WHERE name='{}'".format(request.form.get("filename"))):
            return apology("file name have used,choose another",406)
        if file and allowed_file(file.filename) and allowed_file(request.form.get("filename")):
            filename = secure_filename(request.form.get("filename"))
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        file.seek(0, os.SEEK_END)
        filesize=round(file.tell()/1024/1024,3)
        #insert to databse files table
        db.execute("INSERT INTO 'files' ('id','name','size') VALUES (NULL,'{}','{}')".format(filename,filesize))
        return apology("this not a error,file saved succefully",200)


@app.route("/getfile",methods=["GET"])
def getfile():
    filename=request.args.get("filename")
    if not filename:
        return jsonify("no file name to get a file")
    return app.send_static_file("files/{}".format(filename))


@app.route("/note", methods=["GET"])
#@login_required
def note():
    """
       neednot args
       return render_template("note.html",notes)
       notes is list of 3 element list, list like[ ["tag","text",id], ["game","CSgo",0],["book","the c program language",1] ] ,20 most recent notes are contained in notes
    """
    # if user not log in,he will use default id =0
    if  "user_id" not in session:
        session["user_id"]=0
    notes_rows=db.execute("SELECT * FROM notes WHERE user_id = :user_id",user_id=session["user_id"])
    noteslist=[]
    note_counter=0
    for row in notes_rows:
        noteslist.insert(0,[row["tag"],row["note"],row["id"]])
        note_counter+=1
        if note_counter>100:
            break
    #TODO
    return render_template("note.html", notes=noteslist, user_id=session["user_id"])


@app.route("/savenote", methods=["GET", "POST"])
#@login_required
def savenote():
    """
        deal with both POST and GET
        if GET return render_template("note.html")
        if POST, use request.form.get("usertag") and request.form.get("usernote") to get input
        then store them in database
        if every thing is ok return jsonify(True) ,or return  jsonify(False)
    """
    #if GET simply redirct to /note
    if request.method=="GET":
        return redirect("/note")
    #TODO
    usertag=request.form.get("usertag")
    usernote=request.form.get("usernote")
    db.execute("INSERT INTO notes (id,user_id,tag,note) VALUES (NULL,:user_id,:tag,:note) ",user_id=session["user_id"],tag=usertag,note=usernote)
    return jsonify(True)


@app.route("/deletenote",methods=["POST"])
@login_required
def deletenote():
    """
        use request.form.get("id") to get id of the note need to be deleted
        if delete successfully, return jsonify(True), else return jsonify(False)
    """
    note_id = request.form.get("id")
    db.execute("DELETE FROM notes WHERE id=:id", id=note_id)
    return jsonify(True)


@app.route("/searchnote",methods=["GET"])
def searchnote():
    """
        use request.args.get("keyword") to get keyword,then search the keyword
        return: a 3 elements list like[ ["tag","text",id], ["game","CSgo",0],["book","the c program language",1] ]
    """
    #TODO
    #here are return example ,u should return list like this use jsonify(),so i can use result easyly in javascript
    keyword=request.args.get("keyword")
    #print("****keyword",keyword)
    result_rows=db.execute("SELECT * FROM notes  WHERE note LIKE '%{}%'".format(keyword))
    result_list=[]
    for row in result_rows:
        if row["user_id"]==session["user_id"]:
            result_list.insert(0,[row["tag"],row["note"],row["id"]])
    return jsonify(result_list)


@app.route("/")
def index():
    # generate the homepage
    # if user did not login set the session's user_id to 0 to treat as no_register
    if  "user_id" not in session:
        session["user_id"]=0
    return redirect("/note")


@app.route("/check", methods=["GET"])
def check():
    """Return true if username available, else false, in JSON format"""

    # get the username
    username = request.args.get("username")

    # check if the user already exists
    rows = db.execute("SELECT * FROM users WHERE username = :username", username=username)
    if rows or not username:
        return jsonify(False)

    return jsonify(True)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id and set to 0
    session.clear()
    session["user_id"]=0

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id and set user_id to 0
    session.clear()
    session["user_id"]=0

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Forget any user_id and set to 0
    session.clear()
    session["user_id"]=0

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # assign varibles to username and password
        username = request.form.get("username")
        password = request.form.get("password")
        confirm_password = request.form.get("confirmation")

        # confirm that the user entered a username, password
        if not username:
            return apology("must provide username")
        if not password:
            return apology("must provide password")
        if not confirm_password:
            return apology("must confirm password",)
        # confirm that the user entered correct passwords
        if password != confirm_password:
            return apology("passwords do not match")

        # check the length of password is atleast 8
        if len(password) < 8:
            return apology("Password must be atleast 8 characters long")

        # check if the user already exists
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=username)
        if rows:
            return apology("this username is already taken")

        # add user to the database
        db.execute("INSERT INTO users ('username','hash') VALUES (:username,:password)",
                   username=username, password=generate_password_hash(password))

        # Remember which user has logged in
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=username)
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")

@app.route("/about",methods=["GET"])
def about():
    return render_template("about.html")

def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)


# run flask app by running the python file
if __name__ == "__main__":
  app.run()