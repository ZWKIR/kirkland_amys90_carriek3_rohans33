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


