from flask import Blueprint, redirect, url_for, session, render_template, jsonify, request, flash
from flask_login import current_user
from extensions import db
from models import User, Asset, UserRole, EquipmentLoan, AssetStatus, EquipmentLoanItem, LoanStatus, EquipmentType, EquipmentCategory
from flask_login import login_required
from sqlalchemy import select
from datetime import datetime
import json
from utils import count_equip_booking_items,equip_type_lookup


equip_booking = Blueprint('equip_booking', __name__)


@equip_booking.route('/equipbooking')
@login_required
def data_fetch():
    equipment_types = db.session.execute(select(EquipmentType)).scalars().all() #Sets all equipment types to var
    equipment_category = db.session.execute(select(EquipmentCategory)).scalars().all()
    bookings = db.session.execute(select(EquipmentLoan).where(EquipmentLoan.fk_user_id == current_user.id)).scalars().all() #Sets all equipment bookings to var
    fully_booked_days = {} #structure of fully_booked is a dict where keys = studio_id and value = array of dates where it's fully booked for that studio
    equipment_id_list = []
    equip_avail_quantity_list = []
    equip_bookings = db.session.execute(select(EquipmentLoan).where(EquipmentLoan.fk_user_id == current_user.id)).scalars().all() 
    booking_counts = count_equip_booking_items(equip_bookings)
    overdue_loans = []
    type_lookup = equip_type_lookup()

    for i in bookings: #check if user has overdue bookings. Eventually need to figure out how to manually override this from admin panel
        if i.status != LoanStatus.FINISHED and i.loan_end_date < datetime.now().date():
            overdue_loans.append(i)
    print(bookings)
    
    for item in equipment_types:
        equipment_id_list.append(item.id)
        unavail = 0
        if item.min_year_group >= current_user.year_group:
            equip_avail_quantity_list.append('OFF_LIMITS') #if equipment is not permitted cuz too young
        else:
            for i in db.session.execute(select(Asset).where(Asset.fk_equipment_type_id == item.id)).scalars():
                if i.status != AssetStatus.AVAILABLE:
                    unavail += 1 #count up all assets in this category that are unavaliable 
                    print("unavail:",unavail)
            if ((item.quantity)-unavail) > item.loan_limit_quantity:
                equip_avail_quantity_list.append(item.loan_limit_quantity)
            else:
                equip_avail_quantity_list.append((item.quantity)-unavail)
    
    return render_template("main/equipment_booking.html", equipment_types = equipment_types, fully_booked_days = fully_booked_days,
    equipment_id_list = equipment_id_list, equipment_avail_quantity_list = equip_avail_quantity_list,
    equipment_category = equipment_category, overdue_loans = overdue_loans, booking_counts = booking_counts,
    equip_type_lookup = type_lookup)

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
        for j in range(selectedQuants[i]):
            loanItems = EquipmentLoanItem(
                fk_equipment_type_id = fk_equipment_type_id,
                fk_loan_id = fk_loan_id,
                created = datetime.now()
            )
            db.session.add(loanItems)
    db.session.commit()
    return redirect(url_for('success_booking')) #redirect user to success booking page

