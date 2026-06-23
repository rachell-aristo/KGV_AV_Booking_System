from app import app
from extensions import db
from models import User, UserRole

with app.app_context():
    if User.query.filter_by(email="leer17@kgv.hk").first() is None:
        admin = User(
            google_sub_id="placeholder",
            name="Rachell Admin",
            email="leer17@kgv.hk",
            role=UserRole.ADMIN
        )
        db.session.add(admin)
        db.session.commit()
        print("Admin created!")
    