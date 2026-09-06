from flask import Flask, render_template, session, redirect, url_for
from flask_login import current_user
from dotenv import load_dotenv
import os
from extensions import db
from models import *
from auth import auth, oauth, login_manager #these lines loads blueprints so they can be registered
from studio_booking import studio_booking
from student_home import student_home
load_dotenv() #loads values from .env file into here so can access

app = Flask(__name__) #Creates this file as a Flask application
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL') #sets the app's values to the things in .env so not hard coded
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config["SESSION_PERMANENT"] = False #Sessions expire when the browser is closed

@app.route('/') #what happens on index main page
def index():
    if not current_user.is_authenticated: #if not logged in
        return render_template("index.html")
    if current_user.role == UserRole.STUDENT:
        return redirect(url_for('student_home.fetch_date'))
    elif current_user.role == UserRole.TEACHER:
        return redirect(url_for('teacher_home'))
    elif current_user.role == UserRole.ADMIN:
        return render_template("admin_home.html")

@app.route('/reject') 
def reject():
    return "Access denied."

db.init_app(app) #connects SQL database with Flask app
oauth.init_app(app) #connects the oauth extension to the app
#blueprints = breaking up your code so it's modular. 
#These lines register the blueprints so that it knows they exist
login_manager.init_app(app) #connects flask-login with app
app.register_blueprint(auth) 
app.register_blueprint(studio_booking)
app.register_blueprint(student_home)





if __name__ == "__main__": #when you run this file directly
    with app.app_context():
        db.create_all() #creates tables defined ONLY if they are not already created
        print("Tables created!")
    app.run(debug=True, port=5001) #opens on port 5001 with debug mode on

