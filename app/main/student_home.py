from flask import Blueprint, render_template
from extensions import db
from models import LoanStatus, EquipmentLoanItem, StudioBooking,StudioBookingStatus, EquipmentLoan
from flask_login import login_required, current_user
from sqlalchemy import select
from utils import count_equip_booking_items, equip_type_lookup

student_home = Blueprint('student_home', __name__) #creates flask blueprint student_home


@student_home.route('/student_home')
@login_required
def fetch_data():
    user_id = current_user.id
    studio_current_bookings = []
    studio_past_bookings = []

    equip_current_bookings = []
    equip_past_bookings = []

    equip_bookings = db.session.execute(select(EquipmentLoan).where(EquipmentLoan.fk_user_id == current_user.id)).scalars().all() 
    equip_booking_ids = [b.id for b in equip_bookings]
    loan_items = db.session.execute(select(EquipmentLoanItem).where(EquipmentLoanItem.fk_loan_id.in_(equip_booking_ids))).scalars().all() 
    type_lookup = equip_type_lookup()
    # equip_types_in_booking = [] #list of fk_equipment_type ids
    
    item_names = []
    equip_bookings = db.session.execute(select(EquipmentLoan)
                                        .where(EquipmentLoan.fk_user_id == current_user.id)).scalars().all() 
    booking_counts = count_equip_booking_items(equip_bookings)
    print(booking_counts)

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


    return render_template("main/student_home.html", loan_items = loan_items, studio_current_bookings = studio_current_bookings, 
                           studio_past_bookings = studio_past_bookings, booking_counts = booking_counts, equip_current_bookings = equip_current_bookings, 
                           equip_past_bookings = equip_past_bookings,
                           type_lookup = type_lookup)
#render the html page and pass values into it that html page will show with jinga
