#creates all tables from models.py in the database at DATABASE_URL (only ones that don't exist yet)
from app.main.app import app
from app.main.extensions import db

with app.app_context():
    db.create_all()
    print("tables created:", sorted(db.metadata.tables))
