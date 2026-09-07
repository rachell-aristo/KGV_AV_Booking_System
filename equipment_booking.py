from flask import Blueprint, redirect, url_for, session, render_template, jsonify, request, flash
from flask_login import current_user
from extensions import db
from models import User, UserRole, EquipmentLoan, EquipmentLoanItem, LoanStatus, EquipmentType, PickUpTime, EquipmentCategory
from flask_login import login_required
from sqlalchemy import select
from datetime import datetime


equip_booking = Blueprint('equip_booking', __name__)


@equip_booking.route('/equipbooking')
@login_required
def data_fetch():
    equipment_types = db.session.execute(select(EquipmentType)).scalars().all() #Sets all equipment types to var
    equipment_category = db.session.execute(select(EquipmentCategory)).scalars().all()
    bookings = db.session.execute(select(EquipmentLoan)).scalars().all() #Sets all equipment bookings to var
    pickup_times = [value for value in PickUpTime]
    booked_day_dict = {} #in this dict, keys are tuples with (date,studio_id)
    fully_booked_days = {} #structure of fully_booked is a dict where keys = studio_id and value = array of dates where it's fully booked for that studio
    equipment_id_list = []
    equipment_quantity_list = []
    for item in equipment_types:
        equipment_id_list.append(item.id)
        equipment_quantity_list.append(item.quantity)

    print(equipment_id_list)
    print(equipment_quantity_list)

    #figure out how to calculate when an equipment item is booked
    #first you need to check its quantity, if quantity = 0, it's def booked and needs to show unavaliable. 
    # If not 0, give a input for user to select how much they want
    
    return render_template("equipment_booking.html", equipment_types = equipment_types, 
    bookings = bookings, pickup_times = pickup_times, fully_booked_days = fully_booked_days,
    equipment_id_list = equipment_id_list, equipment_quantity_list = equipment_quantity_list,
    equipment_category = equipment_category)


@equip_booking.route('/submit_studio_booking', methods=['POST']) #using POST method so submitted data is not publicly shown in URL
@login_required
def submit_equip_booking():
    #gets all the needed values from html
    loan_start_date = request.form.get('loan-start-date')
    loan_end_date = request.form.get('loan-end-date')
    pickup_time = request.form.get('pickup-time')
    student_loan_reason = request.form.get('booking-reason')
    student_extra_notes = request.form.get('booking-notes')
    
    new_equip_booking = EquipmentLoan(
            loan_start_date = loan_start_date,
            loan_end_date = loan_end_date,
            pickup_time = pickup_time,
            status = LoanStatus.PENDING,
            student_loan_reason = student_loan_reason,
            student_extra_notes = student_extra_notes,
            fk_user_id=current_user.id,
            created = datetime.now()
        )
    db.session.add(new_equip_booking)
    db.session.commit()

    for i in range():
        fk_equipment_type_id = request.form.get('equipment-type-id')
        fk_asset_id = request.form.get('asset-id')
        fk_loan_id = request.form.get('loan-id')

        loanItems = EquipmentLoanItem(
            fk_equipment_type_id = fk_equipment_type_id,
            fk_asset_id = fk_asset_id,
            fk_loan_id = fk_loan_id,
            created = datetime.now()
        )

    db.session.add(loanItems)
    db.session.commit()
    return redirect(url_for('app.success_booking')) #redirect user to success booking page

