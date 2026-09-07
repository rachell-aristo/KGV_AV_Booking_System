#This file sets up Rachell's email as admin if it doesn't exit

from app import app
from extensions import db
from models import User, UserRole
from sqlalchemy import select
from datetime import datetime



with app.app_context():
    if db.session.execute(select(User).where(User.email == "leer17@kgv.hk")).scalar() is None:
        admin = User(
            google_sub_id="placeholder",
            name="Rachell Admin",
            email="leer17@kgv.hk",
            role=UserRole.ADMIN,
            created = datetime.now()
        )
        db.session.add(admin)
        db.session.commit()
        print("Admin created!")

    
    