from flask import Flask
from dotenv import load_dotenv
import os
from extensions import db
from models import *

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

@app.route('/')
def index():
    return "KGV AV Booking System — coming soon"

db.init_app(app)



if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        print("Tables created!")
    app.run(debug=True, port=5001)


