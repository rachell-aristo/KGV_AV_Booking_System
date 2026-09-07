#to do: incorperate this into the Admin space so that Arthur can upload too. Make sure to give him strict formatting rules

import pandas as pd
from flask import Blueprint, redirect, url_for, session, render_template, jsonify, request, flash
from flask_login import current_user
from extensions import db
from models import User, UserRole, Asset, EquipmentLoanItem, AssetStatus, EquipmentType, EquipmentCategory
from flask_login import login_required
from sqlalchemy import select, update
from app import app
from datetime import datetime


df = pd.read_csv('harder_test.csv')
df.drop(df.query('`Item ID`.isnull() | `Item Name`.isnull()').index, inplace = True) #you should add error message here when this happens so user knows
#remove bad data with empty space
df['Status'] = df['Status'].map(lambda x: AssetStatus(x.lower().strip()) if pd.notna(x) else None) 
df['Contents'] = df['Contents'].fillna("None")
#converts the status and empty vals to enum and None so that sql can understand
columns = ['Category', 'Item Name', 'Item ID', 'Status', 'Contents']
df_data = df[columns] #new df with clean data
records = df_data.values.tolist() #convert to list

for row in records:
    type = row[1]
    barcode = row[2]
    status = row[3]
    descript = row[4]
    equipment_category = row[0]
    with app.app_context():
        if db.session.execute(select(EquipmentCategory).where(EquipmentCategory.name == equipment_category)).scalar() == None:
            #if this equipmentcategory, doesn't exist, make one. TO DO: add a confirmation for admin before creating
            new_category = EquipmentCategory(
                name = equipment_category,
                created = datetime.now()
            )
            print(equipment_category,'created!')
            db.session.add(new_category)
            db.session.commit()
        if db.session.execute(select(EquipmentType).where(EquipmentType.name == type)).scalar() == None:
            category_id = db.session.execute(select(EquipmentCategory.id).where(EquipmentCategory.name == equipment_category)).scalar()
            new_type = EquipmentType(
                name = type,
                image = "uploads/placeholder_image.png",
                descript = descript,
                quantity = 1,
                fk_equipment_category_id = category_id,
                created = datetime.now()
            )
            print(type,'created!')
            db.session.add(new_type)
            db.session.commit()
            #You should do a thing where min year group and loan limit quality and 
            # max loan days are asked for whenever a new equipment type is created. 
            #right now it's just using default
            #same for needing system to add new images
        else:
            stmt = select(EquipmentType).where(EquipmentType.name == type)
            equipment = db.session.execute(stmt).scalar_one_or_none()
            equipment.quantity += 1
            db.session.commit()
        new_asset = Asset(
            name = type,
            barcode = barcode,
            status = status,
            descript = descript,
            is_active = True,
            fk_equipment_type_id = db.session.execute(select(EquipmentType.id).where(EquipmentType.name == type)).scalar(),
            created = datetime.now()
            )
        db.session.add(new_asset)
        print("New asset created!")
        db.session.commit()


with app.app_context():
    print(db.session.execute(select(EquipmentCategory)).scalars().all())




# #the structure of what this should be is: you need to set each value/row to a record