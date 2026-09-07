#seed code to set TimeSlot and SetUp for studio booking if not already there

from app import app
from extensions import db
from models import StudioSetupOptions, StudioSpace, TimeSlot, User, UserRole
from datetime import time
from sqlalchemy import select
from datetime import datetime

with app.app_context():
    if db.session.execute(select(StudioSpace)).first() is None:
        photography = StudioSpace(name="Photography Studio", descript = "Media studio for photography and more", image = "uploads/temp_studio_image.png", created = datetime.now())
        audio = StudioSpace(name="Audio Booth", descript = "Audio booth for voice recording and foley", image = "uploads/temp_sound_image.jpg", created = datetime.now())

        db.session.add_all([photography,audio])
        db.session.commit() 

    photography = db.session.execute(select(StudioSpace).where(StudioSpace.name == "Photography Studio")).scalar()
    audio = db.session.execute(select(StudioSpace).where(StudioSpace.name == "Audio Booth")).scalar()


    p1 = TimeSlot(
        name = "Period 1",
        time_start = time(8,15),
        time_end = time(9,15),
        created = datetime.now()
    )

    p2 = TimeSlot(
        name = "Period 2",
        time_start = time(9,25),
        time_end = time(10,25),
        created = datetime.now()
    )

    break_time = TimeSlot(
        name = "Break time",
        time_start = time(10,55),
        time_end = time(11,15),
        created = datetime.now()
    )

    p3 = TimeSlot(
        name = "Period 3",
        time_start = time(11,15),
        time_end = time(12,15),
        created = datetime.now()
    )

    p4 = TimeSlot(
        name = "Period 4",
        time_start = time(12,25),
        time_end = time(13,25),
        created = datetime.now()
    )

    lunch = TimeSlot(
        name = "Lunch",
        time_start = time(13,25),
        time_end = time(14,20),
        created = datetime.now()
    )

    p5 = TimeSlot(
        name = "Period 5",
        time_start = time(14,20),
        time_end = time(15,20),
        created = datetime.now()
    )
 
    if db.session.execute(select(TimeSlot)).scalars().first() is None:
        db.session.add_all([p1,p2,p3,p4,p5,lunch,break_time])
        db.session.commit()  

    green_screen = StudioSetupOptions(
        name = "Green Screen",
        fk_studio_space_id = photography.id,
        created = datetime.now()
        )
    black_bg = StudioSetupOptions(
        name = "Black Background",
        fk_studio_space_id = photography.id,
        created = datetime.now()
        )
    
    white_bg = StudioSetupOptions(
        name = "White Background",
        fk_studio_space_id = photography.id,
        created = datetime.now()
        )
    
    voice = StudioSetupOptions(
        name = "Voice Recording",
        fk_studio_space_id = audio.id,
        created = datetime.now()
        )
    
    foley = StudioSetupOptions(
        name = "Foley Recording",
        fk_studio_space_id = audio.id,
        created = datetime.now()
        )
    
    if db.session.execute(select(StudioSetupOptions)).scalars().first() is None:
        db.session.add_all([green_screen,black_bg,white_bg,voice,foley])
        db.session.commit()    
        print("Studio seed data inputed!")
   
        

    #admin seed data
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
        print("Admin seed data inputed!")



    




    

    
    