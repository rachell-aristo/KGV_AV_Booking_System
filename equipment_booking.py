from flask import Blueprint, redirect, url_for, session, render_template, jsonify, request, flash
from flask_login import current_user
from extensions import db
from models import User, Asset, UserRole, EquipmentLoan, AssetStatus, EquipmentLoanItem, LoanStatus, EquipmentType, EquipmentCategory
from flask_login import login_required
from sqlalchemy import select
from datetime import datetime
import json


equip_booking = Blueprint('equip_booking', __name__)


@equip_booking.route('/equipbooking')
@login_required
def data_fetch():
    equipment_types = db.session.execute(select(EquipmentType)).scalars().all() #Sets all equipment types to var
    equipment_category = db.session.execute(select(EquipmentCategory)).scalars().all()
    bookings = db.session.execute(select(EquipmentLoan)).scalars().all() #Sets all equipment bookings to var
    assets = db.session.execute(select(Asset))
    booked_day_dict = {} #in this dict, keys are tuples with (date,studio_id)
    fully_booked_days = {} #structure of fully_booked is a dict where keys = studio_id and value = array of dates where it's fully booked for that studio
    equipment_id_list = []
    equip_avail_quantity_list = []
    
    for item in equipment_types:
        equipment_id_list.append(item.id)
        unavail = 0
        for i in db.session.execute(select(Asset).where(Asset.fk_equipment_type_id == item.id)).scalars():
            if i.status != AssetStatus.AVAILABLE:
                unavail += 1 #count up all assets in this category that are unavaliable 
                print("unavail:",unavail)
        equip_avail_quantity_list.append((item.quantity)-unavail)
 


    #figure out how to calculate when an equipment item is booked
    #first you need to check its quantity, if quantity = 0, it's def booked and needs to show unavaliable. 
    # If not 0, give a input for user to select how much they want
    print("type list:", equipment_types)
    print('id list:', equipment_id_list)
    print("length id: ", len(equipment_id_list))
    print("quanity list:", equip_avail_quantity_list)
    print("length:",len(equip_avail_quantity_list))

    return render_template("equipment_booking.html", equipment_types = equipment_types, 
    bookings = bookings, fully_booked_days = fully_booked_days,
    equipment_id_list = equipment_id_list, equipment_avail_quantity_list = equip_avail_quantity_list,
    equipment_category = equipment_category)


@equip_booking.route('/submit_equip_booking', methods=['POST']) #using POST method so submitted data is not publicly shown in URL
@login_required
def submit_equip_booking():
    #gets all the needed values from html
    loan_start_date = request.form.get("loan-start-date")
    loan_end_date = request.form.get('loan-end-date')
    student_loan_reason = request.form.get('booking-reason')
    student_extra_notes = request.form.get('booking-notes')
    selectedEquip = json.loads(request.form.get('selected-equip')) #this is a list of equipmnet ids
    selectedQuants = json.loads(request.form.get('selected-quants'))

    new_equip_booking = EquipmentLoan(
            loan_start_date = datetime.fromisoformat(loan_start_date),
            loan_end_date = datetime.fromisoformat(loan_end_date),
            status = LoanStatus.PENDING,
            student_loan_reason = student_loan_reason,
            student_extra_notes = student_extra_notes,
            fk_user_id=current_user.id,
            created = datetime.now()
        )
    db.session.add(new_equip_booking)
    db.session.commit()

    for i in range(len(selectedEquip)):
        fk_equipment_type_id = selectedEquip[i]
        fk_loan_id = new_equip_booking.id

        loanItems = EquipmentLoanItem(
            fk_equipment_type_id = fk_equipment_type_id,
            fk_loan_id = fk_loan_id,
            created = datetime.now()
        )
        db.session.add(loanItems)
    db.session.commit()
    return redirect(url_for('success_booking')) #redirect user to success booking page

