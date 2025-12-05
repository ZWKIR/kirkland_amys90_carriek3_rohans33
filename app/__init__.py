from flask import Flask
from flask import render_template  # facilitate jinja templating
from flask import request, redirect, url_for  # facilitate form submission
from flask import session
import sqlite3   #enable control of an sqlite database
import urllib.request
import json
import random
from io import StringIO

#FLASK Declaration
#====================================================================================#
app = Flask(__name__)  # create Flask object
app.secret_key = b'kirklandsignature'


#SQLITE3 Databases
#====================================================================================#
DB_FILE="catt.db"

db = sqlite3.connect(DB_FILE) #open if file exists, otherwise create
c = db.cursor()

#profile
c.execute("""
CREATE TABLE IF NOT EXISTS user_profile(
	username TEXT PRIMARY KEY NOT NULL,
	password TEXT NOT NULL,
	sprite TEXT
);""")

c.execute("""
CREATE TABLE IF NOT EXISTS encounter_maps(
	background TEXT,
	num_cats INTEGER,
	energy_lvl INTEGER,
	weather TEXT
);""")

c.execute("""
CREATE TABLE IF NOT EXISTS user_encounters(
	username TEXT,
	cat TEXT,
	affection INTEGER,
	level INTEGER
);""")

c.execute("""CREATE TABLE IF NOT EXISTS dialogue(
	encounter_type TEXT,
	response1 TEXT,
	response2 TEXT,
	response3 TEXT,
	response4 TEXT
);""")

c.execute("""CREATE TABLE IF NOT EXISTS jokes(
	category TEXT, 
	joke TEXT, 
	difficulty INTEGER, 
	desired_response TEXT
);""")

c.execute("""CREATE TABLE IF NOT EXISTS trivia(
	difficulty TEXT,
	answer1 TEXT,
	answer2 TEXT,
	answer3 TEXT,
	answer4 TEXT,
	correct_answer TEXT
	);""")

c.execute("""CREATE TABLE IF NOT EXISTS cats(
	breed TEXT,
	energy_lvl INTEGER,
	difficulty INTEGER,
	response_type INTEGER
);""")

with urllib.request.urlopen("https://api.thecatapi.com/v1/breeds") as response:
    a = json.loads(response.read())
for b in a:
    q = "INSERT OR REPLACE INTO cats(breed, energy_lvl, difficulty, response_type) VALUES(?, ?, ?, ?)"
    d = (b['name'], b['energy_level'], b['stranger_friendly'], random.randint(0,1))
    c.execute(q, d)
    db.commit()

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
    if loggedin():
        return redirect(url_for('home'))
    else:
        if request.method == 'POST':
            session.permanent = True
            with sqlite3.connect(DB_FILE) as db:
                c = db.cursor()
                for row in c.execute("SELECT * FROM user_profile WHERE username LIKE ?;", (request.form['id'],)):
                    if(row[1] == request.form['pass']):
                        session['username'] = request.form['id']
                        session['password'] = request.form['pass']
    return registerpage()

@app.route("/login", methods=['GET', 'POST'])
def login():
    if loggedin():
        return redirect(url_for('home'))
    if request.method == 'POST':
        session.permanent = True
        with sqlite3.connect(DB_FILE) as db:
                c = db.cursor()
                for row in c.execute("SELECT * FROM user_profile WHERE username LIKE ?;", (request.form['id'],)):
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
    return profilepage()

@app.route("/logout", methods=['GET', 'POST'])
def logout():
    if loggedin():
        return logoutpage()
    return loginpage()

@app.route("/start", methods=['GET', 'POST'])
def startscreen():
    return startpage()

@app.route("/settings", methods=['GET', 'POST'])
def settings():
    return settingspage()

@app.route("/encounters", methods=['GET', 'POST'])
def encounters():
    return encounterspage()

@app.route("/encounters/<weather>", methods=['GET', 'POST'])
def weatherencounters(weather):
    return weatherspage()

#HTML Pages
#====================================================================================#
def registerpage():
    return render_template('signup.html')

def loginpage(valid=True):
    return render_template('login.html')
    '''
    if(valid==True):
        return render_template('login.html',username=user)
    else:
        return render_template('login.html',invalid="Your username or password was incorrect")
    '''

def profilepage():
    return render_template('profile.html')

def logoutpage():
    return render_template('logout.html')

def startpage():
    return render_template('start.html')

def settingspage():
    return render_template('settings.html')

def encounterspage():
    return render_template('encounters.html')

def weatherspage():
	return render_template('weatherencounters.html')
#====================================================================================#
if __name__ == "__main__":  # false if this file imported as module
    #app.debug = True  # enable PSOD, auto-server-restart on code chg
    app.run(port=8900)
