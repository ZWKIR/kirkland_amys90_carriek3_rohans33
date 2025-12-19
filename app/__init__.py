# Amy Shrestha, Carrie Ko, Rohan Sen
# Kirkland
# SoftDev
# P01
# 2025-12-18
# time spent: 30.0
import pickle

from flask import Flask
from flask import render_template  # facilitate jinja templating
from flask import request, redirect, url_for  # facilitate form submission
from flask import session
import sqlite3   #enable control of an sqlite database
import urllib.request
import json
import random
from io import StringIO
import os
from datetime import datetime, timedelta

#FLASK Declaration
#====================================================================================#
app = Flask(__name__)  # create Flask object
app.secret_key = b'kirklandsignature'


#SQLITE3 Databases
#====================================================================================#
DB_FILE="catt.db"

db = sqlite3.connect(DB_FILE, check_same_thread=False) #open if file exists, otherwise create
c = db.cursor()

#profile
c.execute("""
CREATE TABLE IF NOT EXISTS user_profile(
    username TEXT PRIMARY KEY NOT NULL,
    password TEXT NOT NULL,
    sprite TEXT
);""")

c.execute("""
CREATE TABLE IF NOT EXISTS user_encounters(
    username TEXT,
    cat TEXT,
    affection INTEGER,
    level INTEGER
);""")

c.execute("""CREATE TABLE IF NOT EXISTS dialogue(
    encounter_type TEXT PRIMARY KEY,
    response1 TEXT,
    response2 TEXT,
    response3 TEXT,
    response4 TEXT
);""")

c.execute("""CREATE TABLE IF NOT EXISTS jokes(
    category TEXT,
    joke TEXT PRIMARY KEY,
    difficulty INTEGER
);""")

c.execute("""
CREATE TABLE IF NOT EXISTS encounter_maps(
    background TEXT,
    num_cats INTEGER,
    energy_lvl INTEGER,
    time TEXT,
    weather TEXT,
    id INTEGER PRIMARY KEY
);""")

c.execute("""CREATE TABLE IF NOT EXISTS trivia(
    difficulty TEXT,
        question TEXT,
    answer1 TEXT,
    answer2 TEXT,
    answer3 TEXT,
    answer4 TEXT,
    correct_answer TEXT
    );""")

c.execute("""CREATE TABLE IF NOT EXISTS cats(
    breed TEXT PRIMARY KEY,
    energy_lvl INTEGER,
    difficulty INTEGER,
    difficulty2 TEXT,
    response_type INTEGER
);""")

try:
    with urllib.request.urlopen("https://api.thecatapi.com/v1/breeds") as response:
        a = json.loads(response.read())
    for b in a:
        t = ""
        if(b['stranger_friendly'] == 5):
            t = "easy"
        if(b['stranger_friendly'] == 4 or b['stranger_friendly'] == 3):
            t = "medium"
        if(b['stranger_friendly'] == 2 or b['stranger_friendly'] == 1):
            t = "hard"
        q = "INSERT OR REPLACE INTO cats(breed, energy_lvl, difficulty, difficulty2, response_type) VALUES(?, ?, ?, ?, ?)"
        d = (b['name'], b['energy_level'], b['stranger_friendly'], t, random.randint(0,1))
        c.execute(q, d)
except:
    print("error with breeds")

try:
    for i in range(10):
        with urllib.request.urlopen("https://v2.jokeapi.dev/joke/Programming,Miscellaneous,Dark,Pun?blacklistFlags=nsfw,religious,political,racist,sexist,explicit&type=single&amount=10") as response:
            a = json.loads(response.read())
        for b in a['jokes']:
            t = 0
            if(b['category'] == "Dark"):
                t = 2
            if(b['category'] == "Misc"):
                t = 3
            if(b['category'] == "Pun"):
                t = 4
            if(b['category'] == "Programming"):
                t = 5
            if(b['safe'] == False):
                t = 1
            q = "INSERT OR IGNORE INTO jokes(category, joke, difficulty) VALUES(?, ?, ?)"
            d = (b['category'], b['joke'], t)
            c.execute(q, d)
except:
    print("error with joke")

try:
    for i in range(10):
        with urllib.request.urlopen("https://the-trivia-api.com/v2/questions") as response:
            a = json.loads(response.read())
        for b in a:
            t = [b['incorrectAnswers'][0], b['incorrectAnswers'][1], b['incorrectAnswers'][2], b['correctAnswer']]
            random.shuffle(t)
            q = "INSERT OR REPLACE INTO trivia(difficulty, question, answer1, answer2, answer3, answer4, correct_answer) VALUES (?, ?, ?, ?, ?, ?, ?)"
            d = (b['difficulty'], b['question']['text'], t[0], t[1], t[2], t[3], b['correctAnswer'])
            c.execute(q, d)
except:
    print("error with TRIVIA")

# set up dialogues
c.execute("INSERT OR IGNORE INTO dialogue(encounter_type, response1, response2, response3, response4) VALUES (?, ?, ?, ?, ?)", ("joke", "Hilarious!", "That's a great joke!", "Meh.", "I've heard better..."))
c.execute("INSERT OR REPLACE INTO dialogue(encounter_type, response1, response2, response3, response4) VALUES (?, ?, ?, ?, ?)", ("trivia", "1", "2", "3", "4"))

#("trivia", "Wow, the cat is impressed!", "Beautiful.", "The cat looks down on your knowledge bank.", "Nope."))

totalCount = c.execute("SELECT COUNT(DISTINCT breed) FROM cats").fetchone()[0]
currCount = 0

def pick_city():
    while True:
        try:
            with open("app/locations", "r") as f:
                lines = f.read().strip().splitlines()
                city,lat,lon = random.choice(lines).split(",")
                print(city)
            with open("app/keys/key_pirateWeather.txt", "r") as f:
                key = f.read().strip()
            with urllib.request.urlopen(f"https://api.pirateweather.net/forecast/{key}/{lat},{lon}") as response:
                a = json.loads(response.read())
            break
        except:
            print("error fetching weather")
    return a, city

def get_time(a):
    sunrise = a["daily"]["data"][0]["sunriseTime"]
    sunset = a["daily"]["data"][0]["sunsetTime"]
    now = a["currently"]["time"]
    if sunrise <= now <= sunset:
        return "day"
    else:
        return "night"

weather = ["clear-day", "clear-night", "thunderstorm", "rain", "rain", "snow", "snow", "sleet", "sleet", "wind", "fog", "cloudy", "cloudy", "partly-cloudy-day", "partly-cloudy-night"]
time = ["", "", "", "day", "night", "day", "night", "day", "night", "", "", "day", "night", "", ""]
bkg_links = ["/static/clear_day.png", "/static/clear_night.png", "/static/thunderstorm.gif", "/static/rainy_day.gif", "/static/rainy_night.gif", "/static/snowy_day.gif", "/static/snowy_night.gif", "/static/snowy_day.gif", "/static/snowy_night.gif", "/static/windy.gif", "/static/fog.png", "/static/cloudy_day.png", "/static/cloudy_night.png", "/static/cloudy_day.png", "/static/cloudy_night.png"]
e_lvl = [5, 4, 1, 3, 2, 5, 3, 2, 1, 3, 2, 3, 1, 4, 2]
n_cats = [4, 3, 2, 3, 2, 3, 2, 2, 1, 3, 4, 3, 1, 5, 3]

for i in range(len(weather)):
    q = "INSERT OR REPLACE INTO encounter_maps(background, num_cats, energy_lvl, time, weather, id) VALUES(?, ?, ?, ?, ?, ?)"
    d = (bkg_links[i], n_cats[i], e_lvl[i], time[i], weather[i], i)
    c.execute(q, d)

def get_icon(a):
    weather = a["currently"]["icon"]
    return weather

def get_temp(a):
    return a["currently"]["temperature"]

def map_info(a):
    w = get_icon(a)
    print(w)
    t = c.execute("SELECT * FROM encounter_maps WHERE weather = ?", (w,))
    d = t.fetchall()
    print (d)
    if (len(d) > 1):
        if get_time(a) == "day":
            return d[0]
        else:
            return d[1]
    else:
        return d[0]


db.commit()

#Helper Functions
#====================================================================================#
usernames = {}
for row in c.execute("SELECT username, password FROM user_profile"):
    usernames[row[0]] = row[1]

print(usernames)

def loggedin():
    if 'username' in session:
        return True
    return False

#Webpage Sites
#====================================================================================#
@app.route("/startscreen", methods=['GET', 'POST'])
def startscreen():
    return startscreenpage()

@app.route("/choose", methods=['GET', 'POST'])
def choose():
    if loggedin():
        return redirect(url_for('encounters'))
    return choosepage()

@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if loggedin():
        return redirect(url_for('start'))
    else:
        if request.method == 'POST':
            with sqlite3.connect(DB_FILE) as db:
                c = db.cursor()
                c.execute("SELECT username FROM user_profile WHERE username = ?", (request.form['username'],))
                if c.fetchone():
                    return registerpage(False, "Duplicate username")
                session.permanent = True

                # for invalid requests / empty form responses
                t = ""
                if(request.form['username'] == "" or request.form['password'] == ""):
                    t = "Please enter a valid "
                    if(request.form['username'] == ""):
                        t = t + "username "
                    if(request.form['password'] == ""):
                        t = t + "password "
                    return registerpage(False, t)

                c.execute("INSERT INTO user_profile VALUES (?, ?, ?);", (request.form['username'], request.form['password'], "/static/placeholder.jpg"))
                session['username'] = request.form['username']
                session['password'] = request.form['password']
                return redirect(url_for('start'))
    return registerpage()

@app.route("/login", methods=['GET', 'POST'])
def login():
    if loggedin():
        return redirect(url_for('start'))

    if request.method == 'POST':
        session.permanent = True
        with sqlite3.connect(DB_FILE) as db:
                c = db.cursor()
                for row in c.execute("SELECT * FROM user_profile WHERE username LIKE ?;", (request.form['username'],)):
                    if(row[1] == request.form['password']):
                        session['username'] = request.form['username']
                        session['password'] = request.form['password']
                        return redirect(url_for('start'))
                    else:
                        return loginpage(valid=False)
        return loginpage(valid=False)
    else:
        return loginpage(valid=True)

@app.route("/profile", methods=['GET', 'POST'])
def profile():
    if not loggedin():
        return redirect(url_for('login'))

    profile_icons = [
        "/static/cat1.jpg",
        "/static/cat2.jpeg",
        "/static/cat3.jpg",
        "/static/cat4.jpg",
        "/static/cat5.jpg"
    ]

    with sqlite3.connect(DB_FILE) as db:
        c = db.cursor()
        c.execute("SELECT * FROM user_profile WHERE username = ?", (session["username"],))
        user = c.fetchone()

        if user is None:
            session.pop("username")
            return redirect(url_for('login'))

        if request.method == 'POST':
            icon = request.form.get("profile_icon")
            c.execute("UPDATE user_profile SET sprite = ? WHERE username = ?", (icon, session["username"]))
            db.commit()
            return redirect(url_for('profile'))

        c.execute("SELECT cat, affection, level FROM user_encounters WHERE username = ?", (session["username"],))
        infoRow = c.fetchall()
        
        currCount = c.execute("SELECT COUNT(DISTINCT cat) FROM user_encounters WHERE username = ?", (session["username"],)).fetchone()[0]

    sprite = user[2]
    return profilepage(profile_icons, sprite, infoRow, currCount, totalCount, user[0])

@app.route("/logout", methods=['GET', 'POST'])
def logout():
    if loggedin():
        session.pop('username')
        return logoutpage()
    return redirect(url_for('login'))

@app.route("/start", methods=['GET', 'POST'])
def start():
    if loggedin():
        return startpage()
    return redirect(url_for('login'))

@app.route("/settings", methods=['GET', 'POST'])
def settings():
    if not loggedin():
        return redirect(url_for('login'))

    with sqlite3.connect(DB_FILE) as db:
        c = db.cursor()
        c.execute("SELECT * FROM user_profile WHERE username = ?", (session["username"],))
        user = c.fetchone()

        if request.method == 'POST':
            oldP = request.form.get('old_pass')
            newP = request.form.get('new_pass')
            # both fields are filled out
            if oldP and newP:
                if oldP == user[1]:
                    c.execute("UPDATE user_profile SET password = ? WHERE username = ?", (newP, session['username']))
                    db.commit()
                else:
                    return render_template('settings.html', username=session['username'], error="Incorrect old password")
            else:
                return render_template('settings.html', username=session['username'], error="Both fields must be filled")
    return settingspage(username=session['username'])

@app.route("/encounters", methods=['GET', 'POST'])
def encounters():
    if loggedin():
        global a
        a, city = pick_city()
        info = map_info(a)
        temperature = get_temp(a)
        path = info[0]
        e = info[1]
        w = info[4]
        time = info[3]
        with sqlite3.connect(DB_FILE) as db:
            c = db.cursor()
            t = c.execute("SELECT breed FROM cats WHERE energy_lvl = ?", (e,))
            d = []
            for i in t.fetchall():
                d.append(i)
        random.shuffle(d)
        print(d)
        return encounterspage(path, w, time, e, city, d, temperature)
    return loginpage()

@app.route("/encounters/<breed>", methods=['GET', 'POST'])
def weatherencounters(breed):
    if loggedin():
        with sqlite3.connect(DB_FILE) as db:
            c = db.cursor()
            encounter = map_info(a)
            # get energy level for weather
            currNRG = encounter[2]

            # get cats for energy level
            c.execute("SELECT * FROM cats WHERE energy_lvl = ?", (currNRG,))
            cats = c.fetchall()

            # get a random cat
            myCatRow = random.choice(cats)

            # get values
            jokeDiff = myCatRow[2] #difficulty in int for jokes
            trivDiff = myCatRow[3] #difficulty in text for trivia

            # set default vals for joke and triv
            currJoke = None
            currTriv = None

            # 0 for joke
            # 1 for trivia
            if myCatRow[4] == 0:
                # now pull from jokes tbl for response 1 and 2
                # check difficulty or difficulty2 of cat for joke
                c.execute("SELECT joke FROM jokes WHERE difficulty <= ? ORDER BY RANDOM() LIMIT 1", (jokeDiff,))

                # category, joke, difficulty, desired_response
                currJoke = c.fetchone()

                # get dialogue
                c.execute("SELECT response1, response2, response3, response4 FROM dialogue WHERE encounter_type = ?", ("joke",))
                dialogue = c.fetchone()

            else: #elif myCatRow[4] == 1:
                # for trivia options, pull from trivia tbl
                # check difficulty or difficulty2 of cat for trivia
                c.execute("SELECT * FROM trivia WHERE difficulty = ? ORDER BY RANDOM() LIMIT 1", (trivDiff,))

                # difficulty, question, a1, a2, a3, a4, correct
                currTriv = c.fetchone()
                print(currTriv)

                # get dialogue
                c.execute("SELECT response1, response2, response3, response4 FROM dialogue WHERE encounter_type = ?", ("trivia",))
                dialogue = c.fetchone()

            # ------CHECKING AFFECTION-----
            # using breed for now, but may need ID for each cat***(NEEDS FIX)
            cat = myCatRow[0]

            # if pressed answer == currTrivia[6], add affection
            # leave encounter after clicking answer
            c.execute("SELECT affection, level FROM user_encounters WHERE username = ? AND cat = ?", (session["username"], breed))

            thisEncounter = c.fetchone()
            # check for 1st encounter without row
            if thisEncounter == None:
                newAffec = 0
                lvl = 1
                c.execute("INSERT OR REPLACE INTO user_encounters(username, cat, affection, level) VALUES (?, ?, ?, ?)", (session["username"], breed, newAffec, lvl))
            else:
                newAffec = thisEncounter[0]
                lvl = thisEncounter[1]

            # if get the answer right in trivia (use buttons for prompts)
            # add 10 extra points from interaction
            # newAffec += 10
            # ------INCOMPLETE-------

            # if interact, get affectoin thru energy_lvl
            addedAffec = myCatRow[1] * random.randint(1,6)
            newAffec += addedAffec

            # keep track of whether or not level updates
            lev = False
            if newAffec >= 100:
                lvl += 1
                newAffec -= 100
            c.execute("UPDATE user_encounters SET affection = ?, level = ? WHERE username = ? AND cat = ?", (newAffec, lvl, session["username"], breed))
    return weatherspage(weather, currJoke, currTriv, myCatRow, dialogue, breed, addedAffec, lvl)

@app.route("/")
def index():
    return startscreenpage()

#HTML Pages
#====================================================================================#
def startscreenpage():
    return render_template('startscreen.html')

def choosepage():
    return render_template('choose.html')

def registerpage(valid=True, invalid=''):
    if(valid==True):
        return render_template('signup.html',invalid=invalid)
    else:
        return render_template('signup.html',invalid=invalid)
    return render_template('signup.html')

def loginpage(valid=True):
    if(valid==True):
        return render_template('login.html',invalid='')
    else:
        return render_template('login.html',invalid="Your username or password was incorrect")

def profilepage(profile_icons, icon, infoRow, currCats, totalCats, user=''):
    return render_template('profile.html', profile_icons=profile_icons, icon=icon, infoRow=infoRow, currCats=currCats, totalCats=totalCats, username=user)

def logoutpage():
    return render_template('logout.html')

def startpage():
    return render_template('start.html')

def settingspage(username='', error=''):
    return render_template('settings.html', username=username, error=error)

def encounterspage(url, weather, time, energy, city, breed, temperature):
    return render_template(f'/backgrounds/{weather}{time}.html', url=url, city=city, breed=breed[0], weather=weather, temperature=temperature)

def weatherspage(r, currJoke, currTrivia, currCat, dialogue, breed, addedAffec, lvl):
    return render_template('weather_encounters.html', weather=r, currJoke=currJoke,
                           currTrivia=currTrivia, currCat=currCat, dialogue=dialogue,
                           breed=breed, addedAffec=addedAffec, lvl=lvl)
#====================================================================================#
if __name__ == "__main__":  # false if this file imported as module
    app.debug = True  # enable PSOD, auto-server-restart on code chg
    app.run(port=6767)
