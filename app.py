from flask import Flask, render_template, session
from dotenv import load_dotenv
import os
from extensions import db
from models import *
from auth import auth, oauth
from studio_booking import studio_booking
from student_home import student_home
load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

@app.route('/')
def index():
    user_id = session.get('user_id')
    if user_id is None:
        return render_template("index.html")
    user = db.session.get(User, user_id)
    if user is None:
        session.clear()
        return render_template("index.html")
    if user.role == UserRole.STUDENT:
        return render_template("student_home.html")
    elif user.role == UserRole.TEACHER:
        return render_template("teacher_home.html")
    elif user.role == UserRole.ADMIN:
        return render_template("admin_home.html")

  

@app.route('/reject')
def reject():
    return "You do not have access to KGV's sytem >:("

db.init_app(app)
oauth.init_app(app)
app.register_blueprint(auth)
app.register_blueprint(studio_booking)
app.register_blueprint(student_home)





if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        print("Tables created!")
    app.run(debug=True, port=5001)


