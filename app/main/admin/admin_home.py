from flask import Blueprint, redirect, url_for, session, render_template, jsonify, request, flash
from extensions import db
from models import User, LoanStatus, EquipmentLoanItem, StudioBooking,StudioBookingStatus, EquipmentLoan
from flask_login import login_required, current_user
from sqlalchemy import select
from utils import count_equip_booking_items, equip_type_lookup

admin_home = Blueprint('admin_home', __name__) #creates flask blueprint admin_home


@admin_home.route('/admin_home')
@login_required
def fetch_data():
    equip_bookings = db.session.execute(select(EquipmentLoan)).scalars().all() 
    serialized_equip_bookings = [loan.to_dict() for loan in equip_bookings]
    studio_bookings = db.session.execute(select(StudioBooking)).scalars().all() 
    equip_bookings = db.session.execute(select(EquipmentLoan)).scalars().all() 
    loan_items = count_equip_booking_items(equip_bookings)
    type_lookup = equip_type_lookup()
    print(serialized_equip_bookings)

    
    user_lookup = {} #dict of user ids and corresponding name
    for i in db.session.execute(select(User)).scalars().all():
        user_lookup[i.id] = i.name




    return render_template("admin/admin_home.html", equip_bookings = equip_bookings, user_lookup = user_lookup, 
                           loan_items = loan_items, type_lookup = type_lookup, s_equip_bookings = serialized_equip_bookings)