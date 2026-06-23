from flask import Flask
from dotenv import load_dotenv
import os
from extensions import db
from models import *
from auth import auth, oauth

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

@app.route('/')
def index():
    return "KGV AV Booking System — coming soon"

@app.route('/reject')
def reject():
    return "You do not have access to KGV's sytem >:("

db.init_app(app)
oauth.init_app(app)
app.register_blueprint(auth)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        print("Tables created!")
    app.run(debug=True, port=5001)


