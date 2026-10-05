from flask import Blueprint, redirect, url_for, session, render_template, jsonify, request, flash
from .extensions import db
from .models import EquipmentType,EquipmentLoanItem, StudioSpace, TimeSlot, StudioSetupOptions
# from extensions import db
# from models import EquipmentType,EquipmentLoanItem
from flask_login import login_required, current_user
from sqlalchemy import select
from collections import Counter

#COUNTS UP THE NUMBER OF EQUIPMENT/TYPE FOR ALL USER'S BOOKINGS#
def count_equip_booking_items(equip_bookings):
        booking_counts = {}
        equip_booking_ids = [b.id for b in equip_bookings]
        loan_items = db.session.execute(select(EquipmentLoanItem)
                                        .where(EquipmentLoanItem.fk_loan_id.in_(equip_booking_ids))).scalars().all() 
        for booking in equip_booking_ids:
            item_names = []
            for item in loan_items:
                if item.fk_loan_id == booking:
                    item_names.append(item.fk_equipment_type_id)
            booking_counts[booking] = Counter(item_names)
        return booking_counts

###########################
#LOOK UP TABLE TO CONVERT EQUIPMENT TYPE IDs TO NAME STRINGS#

def equip_type_lookup(id):
    equip_type_lookup = {} #dict of equipment_type ids and corresponding name of item
    for i in db.session.execute(select(EquipmentType)).scalars().all():
        equip_type_lookup[i.id] = i.name
    if id == "table":
        return(equip_type_lookup)
    else:
        return(equip_type_lookup[id])

###########################
#LOOK UP TABLE TO CONVERT STUDIO SPACE IDs TO NAME STRINGS#
def studio_type_lookup(id):
    studio_lookup = {}
    for i in db.session.execute(select(StudioSpace)).scalars().all():
        studio_lookup[i.id] = i.name
    return(studio_lookup[id])

###########################
#LOOK UP TABLE TO CONVERT TIME SLOT IDs TO NAME STRINGS#
def slot_type_lookup(id):
    slot_lookup = {}
    for i in db.session.execute(select(TimeSlot)).scalars().all():
        slot_lookup[i.id] = i.name
    return(slot_lookup[id])

###########################
#LOOK UP TABLE TO CONVERT STUDIO SETUP IDs TO NAME STRINGS#

def studio_setup_lookup(id):
    setup_lookup = {}
    for i in db.session.execute(select(StudioSetupOptions)).scalars().all():
        setup_lookup[i.id] = i.name
    if id == "table":
        return(setup_lookup)
    else:
        return(setup_lookup[id])

     




#Check overdue bookings

# def update_overdue():
#     equip_bookings = db.session.execute(select(EquipmentType)).scalars().all()
