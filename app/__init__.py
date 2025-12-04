from flask import Flask
from flask import render_template  # facilitate jinja templating
from flask import request, redirect, url_for  # facilitate form submission
from flask import session
import sqlite3   #enable control of an sqlite database

#FLASK declaration
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
	part1 TEXT, 
	part2 TEXT, 
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
	joke_type TEXT
);""")

