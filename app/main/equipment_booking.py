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

    for i in bookings: #Checks if user has overdue bookings. Eventually need to figure out how to manually override this from admin panel
        if i.status == LoanStatus.OVERDUE:
            overdue_loans.append(i)
    

    print(equip_avail_quantity_list)
    
    return render_template("main/equipment_booking.html", equipment_types = equipment_types, fully_booked_days = fully_booked_days,
    equipment_category = equipment_category, overdue_loans = overdue_loans, booking_counts = booking_counts,
    equip_type_lookup = type_lookup)

@equip_booking.route('/get_available_equipment', methods=['POST'])
@login_required
def get_available_equipment():
    data = request.json
    new_loan_start_date = datetime.fromisoformat(data.get('loan_start_date')).date()
    newloan_end_date = datetime.fromisoformat(data.get('loan_end_date')).date()

    equipment_types = db.session.execute(select(EquipmentType)).scalars().all() #Sets all equipment types to var
    updated_quantity_dict = {}

    for item in equipment_types:
        if item.min_year_group > current_user.year_group:
            updated_quantity = 'OFF_LIMITS'
             #if equipment is not permitted for their year group
        else:
            unavail = 0
            stmt = db.session.execute(select(EquipmentLoan)
            .where(EquipmentLoan.status.in_([LoanStatus.CONFIRMED, LoanStatus.PENDING])))
            for loan in stmt.scalars().all():
                for loanitem in db.session.execute(select(EquipmentLoanItem)
                .where(EquipmentLoanItem.fk_loan_id == loan.id, 
                EquipmentLoanItem.fk_equipment_type_id == item.id)).scalars().all():
                    if loan.loan_end_date >= new_loan_start_date and newloan_end_date >= loan.loan_start_date:
                        unavail += 1 #count up all assets in this category that are unavaliable 
            if ((item.quantity)-unavail) > item.loan_limit_quantity:
                updated_quantity = item.loan_limit_quantity
            else:
                updated_quantity = item.quantity-unavail
        updated_quantity_dict[item.id] = updated_quantity
    print(updated_quantity_dict)
    return jsonify(updated_quantity_dict)



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

