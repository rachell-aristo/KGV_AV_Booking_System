from flask import Blueprint, redirect, url_for, session, render_template, jsonify, request, flash
from extensions import db
from models import EquipmentType, LoanStatus, EquipmentLoanItem, StudioBooking,StudioBookingStatus, EquipmentLoan
from flask_login import login_required, current_user
from sqlalchemy import select
from collections import Counter

student_home = Blueprint('student_home', __name__) #creates flask blueprint student_home

@student_home.route('/student_home')
@login_required
def fetch_date():
    user_id = current_user.id
    print(user_id)
    studio_current_bookings = []
    studio_past_bookings = []

    equip_current_bookings = []
    equip_past_bookings = []
    equip_bookings = db.session.execute(select(EquipmentLoan).where(EquipmentLoan.fk_user_id == user_id)).scalars().all() 
    equip_booking_ids = [b.id for b in equip_bookings]
    # equip_types_in_booking = [] #list of fk_equipment_type ids
    equip_type_lookup = {} #dict of equipment_type ids and corresponding name of item

    # for i in equip_bookings:
    #     equip_types_in_booking.append(i.id)

    for i in db.session.execute(select(EquipmentType)).scalars().all():
        equip_type_lookup[i.id] = i.name

    loan_items = db.session.execute(select(EquipmentLoanItem).where(EquipmentLoanItem.fk_loan_id.in_(equip_booking_ids))).scalars().all() 
    item_names = []
    equipment_counts = Counter(item_names)
    booking_counts = {}

    for booking in equip_booking_ids:
        item_names = []
        for item in loan_items:
            if item.fk_loan_id == booking:
                item_names.append(item.fk_equipment_type_id)
        booking_counts[booking] = Counter(item_names)

    print('equipt',booking_counts)

    studio_bookings = db.session.execute(select(StudioBooking).where(StudioBooking.fk_user_id == user_id)).scalars().all() 
    #selects all bookings this student had made
    for i in studio_bookings: #for loops to categorize studio bookings into current and past ones
        if i.studio_booking_status == (StudioBookingStatus.PENDING) or i.studio_booking_status == (StudioBookingStatus.CONFIRMED):
            studio_current_bookings.append(i)
        elif i.studio_booking_status == (StudioBookingStatus.FINISHED) or i.studio_booking_status == (StudioBookingStatus.REJECTED):
            studio_past_bookings.append(i)

        
    for i in equip_bookings:
        if i.status == (LoanStatus.PENDING) or i.status == (LoanStatus.CONFIRMED):
            equip_current_bookings.append(i)
        elif i.status == (LoanStatus.FINISHED) or i.status == (LoanStatus.REJECTED):
            equip_past_bookings.append(i)

    print('books',equip_bookings)

    print('past',studio_past_bookings)

    return render_template("student_home.html", loan_items = loan_items, equipment_counts = equipment_counts, studio_current_bookings = studio_current_bookings, 
                           studio_past_bookings = studio_past_bookings, booking_counts = booking_counts, equip_current_bookings = equip_current_bookings, 
                           equip_past_bookings = equip_past_bookings,
                           equip_type_lookup = equip_type_lookup)
#render the html page and pass values into it that html page will show with jinga
