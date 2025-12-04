from flask import Flask
from flask import render_template  # facilitate jinja templating
from flask import request, redirect, url_for  # facilitate form submission
from flask import session
import sqlite3   #enable control of an sqlite database

#FLASK Declaration
#====================================================================================#
app = Flask(__name__)  # create Flask object
app.secret_key = b'kirklandsignature'


#SQLITE3 Databases
#====================================================================================#
DB_FILE="catt.db"

db = sqlite3.connect(DB_FILE) #open if file exists, otherwise create
c = db.cursor()

#Helper Functions
#====================================================================================#
def loggedin():
    if 'username' in session:
        return True
    return False

#Webpage Sites
#====================================================================================#
@app.route("/signup", methods=['GET', 'POST'])
def signup():
    return 0

@app.route("/login", methods=['GET', 'POST'])
def login():
    if loggedin():
        return redirect(url_for('home'))
    if request.method == 'POST':
        session.permanent = True
        with sqlite3.connect(DB_FILE) as db:
                c = db.cursor()
                for row in c.execute(f"SELECT * FROM user_profile WHERE username LIKE '{request.form['id']}';"):
                    if(row[1] == request.form['pass']):
                        session['username'] = request.form['id']
                        session['password'] = request.form['pass']
                        return redirect(url_for('home'))
                    else:
                        #return loginpage(valid=False)
                        return loginpage()
        #return loginpage(valid=False)
        return loginpage()
    else:
        #return loginpage(valid=True)
        return loginpage()
        
@app.route("/profile", methods=['GET', 'POST'])
def profile():
    return 0

@app.route("/logout", methods=['GET', 'POST'])
def logout():
    if loggedin():
        return redirect(url_for('logout'))
    return redirect(url_for('login'))

@app.route("/start", methods=['GET', 'POST'])
def startscreen():
    return 0

'''
def settings():
    return 0
'''

@app.route("/encounters", methods=['GET', 'POST'])
def encounters():
    return 0

@app.route("/encounters/<weather>", methods=['GET', 'POST'])
def weatherEncounter(weather):
    return 0

#HTML Pages
#====================================================================================#
def loginpage(valid=True):
    if(valid==True):
        return render_template('login.html',username=user)
    else:
        return render_template('login.html',invalid="Your username or password was incorrect")
    
    