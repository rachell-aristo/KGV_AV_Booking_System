from flask import Blueprint, abort, redirect, url_for, session, render_template, jsonify, request, flash
from flask_mail import Mail, Message
from extensions import db, mail
from models import User, LoanStatus, UserRole, StudioBooking,StudioBookingStatus, EquipmentLoan
from flask_login import login_required, current_user
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import create_async_engine
from utils import count_equip_booking_items, equip_type_lookup
import os



admin_home = Blueprint('admin_home', __name__) #creates flask blueprint admin_home




@admin_home.route('/admin_home')
@login_required
def fetch_data():
    equip_bookings = db.session.execute(select(EquipmentLoan)).scalars().all() 
    serialized_equip_bookings = [loan.to_dict() for loan in equip_bookings]
    studio_bookings = db.session.execute(select(StudioBooking)).scalars().all() 
    serialized_studio_bookings = [loan.to_dict() for loan in studio_bookings]
    loan_items = {booking_id: dict(counter) 
    for booking_id, counter in count_equip_booking_items(equip_bookings).items()}
    type_lookup = equip_type_lookup()

    print(serialized_studio_bookings)
    user_lookup = {} #dict of user ids and corresponding name
    for i in db.session.execute(select(User)).scalars().all():
        user_lookup[i.id] = i.name

    return render_template("admin/admin_home.html", s_studio_bookings = serialized_studio_bookings, equip_bookings = equip_bookings, user_lookup = user_lookup, 
                           loan_items = loan_items, type_lookup = type_lookup, s_equip_bookings = serialized_equip_bookings)

@admin_home.route('/update_loan_status', methods=['POST'])
@login_required
def update_loan_status():
    if current_user.role != UserRole.ADMIN:
        abort(401)
    else:
        data = request.json
        loan_id = int(data.get('loan_id'))
        new_status = data.get('new_status')
        enum_status = LoanStatus(new_status.lower())

        stmt = update(EquipmentLoan).where(EquipmentLoan.id == loan_id).values(status = enum_status)
        db.session.execute(stmt)
        db.session.commit()
        return jsonify({'success': True})

@admin_home.route('/send_mail', methods=['POST'])
@login_required
def send_email():
    try:
        data = request.json
        action = data.get('action')
        record_id = data.get('id')
        user_id = db.session.execute(select(EquipmentLoan.fk_user_id).where(EquipmentLoan.id == record_id)).scalar()
        user_email = db.session.execute(select(User.email).where(User.id == user_id)).scalar()
        if action == "approve":
            msg = Message("Booking confirmed", sender = os.getenv("DEL_EMAIL"),recipients=[user_email]) 
            msg.body = "Yay your booking is confirmed!"
        elif action == "remind":
            msg = Message("Overdue reminder", sender = os.getenv("DEL_EMAIL"),recipients=[user_email]) 
            msg.body = "Please return your overdue booking >:("
        elif action == "cancel":
            msg = Message("Your booking has been cancelled", sender = os.getenv("DEL_EMAIL"),recipients=[user_email]) 
            msg.body = "Cancelled"
        elif action == "reject":
            msg = Message("Your booking has been rejected", sender = os.getenv("DEL_EMAIL"),recipients=[user_email]) 
            msg.body = "for x reason"
        mail.send(msg)
        print("Success!!")
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


