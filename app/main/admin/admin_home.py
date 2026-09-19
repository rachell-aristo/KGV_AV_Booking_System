from flask import Blueprint, abort, redirect, url_for, session, render_template, jsonify, request, flash
from flask_mail import Mail, Message
from ..extensions import db, mail
from ..models import User, LoanStatus, UserRole, StudioBooking, EquipmentLoan, StudioSpace, TimeSlot, StudioBookingStatus
from ..utils import count_equip_booking_items, equip_type_lookup


from flask_login import login_required, current_user
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import create_async_engine



admin_home = Blueprint('admin_home', __name__) #creates flask blueprint admin_home




@admin_home.route('/admin_home')
@login_required
def fetch_data():
    if current_user.role != UserRole.ADMIN:
        abort(401)
    else:
        equip_bookings = db.session.execute(select(EquipmentLoan)).scalars().all() 
        serialized_equip_bookings = [loan.to_dict() for loan in equip_bookings]

        studio_bookings = db.session.execute(select(StudioBooking)).scalars().all() 
        serialized_studio_bookings = [loan.to_dict() for loan in studio_bookings]
   

        users = db.session.execute(select(User)).scalars().all() 
        serialized_users = [user.to_dict() for user in users]

        loan_items = {booking_id: dict(counter) 
        for booking_id, counter in count_equip_booking_items(equip_bookings).items()}
        type_lookup = equip_type_lookup()

        user_lookup = {} #dict of user ids and corresponding name
        for i in db.session.execute(select(User)).scalars().all():
            user_lookup[i.id] = i.name

        studio_lookup = {}
        for i in db.session.execute(select(StudioSpace)).scalars().all():
            studio_lookup[i.id] = i.name

        slot_lookup = {}
        for i in db.session.execute(select(TimeSlot)).scalars().all():
            slot_lookup[i.id] = i.name

        return render_template("admin/admin_home.html", s_studio_bookings = serialized_studio_bookings, equip_bookings = equip_bookings, 
                            user_lookup = user_lookup, s_users = serialized_users,
                            loan_items = loan_items, type_lookup = type_lookup, s_equip_bookings = serialized_equip_bookings,
                            studio_lookup = studio_lookup, slot_lookup = slot_lookup)

@admin_home.route('/update_loan_status', methods=['POST'])
@login_required
def update_loan_status():
    if current_user.role != UserRole.ADMIN:
        abort(401)
    else:
        data = request.json
        loan_id = int(data.get('loan_id'))
        new_status = data.get('new_status')
        
        reject_reason = data.get('reject')
        type = data.get('type')
        if type == "EQUIP":
            enum_status = LoanStatus(new_status.lower())
            stmt = update(EquipmentLoan).where(EquipmentLoan.id == loan_id).values(status = enum_status, admin_reject_reason = reject_reason)
        elif type == "STUDIO":
            enum_status = StudioBookingStatus(new_status.lower())
            stmt = update(StudioBooking).where(StudioBooking.id == loan_id).values(studio_booking_status = enum_status, admin_reject_reason = reject_reason)
        db.session.execute(stmt)
        db.session.commit()
        return jsonify({'success': True})

@admin_home.route('/send_mail', methods=['POST'])
@login_required
def send_email():
    if current_user.role != UserRole.ADMIN:
        abort(401)
    else:
        try:
            data = request.json
            action = data.get('action')
            record_id = data.get('id')
            type = data.get('type')
            if type == "EQUIP":
                user_id = db.session.execute(select(EquipmentLoan.fk_user_id).where(EquipmentLoan.id == record_id)).scalar()
            elif type == "STUDIO":
                user_id = db.session.execute(select(StudioBooking.fk_user_id).where(StudioBooking.id == record_id)).scalar()
            user_email = db.session.execute(select(User.email).where(User.id == user_id)).scalar()
            # if action == "approve":
            #     msg = Message("Booking confirmed", sender = os.getenv("DEL_EMAIL"),recipients=[user_email]) 
            #     msg.body = "Yay your booking is confirmed!"
            # elif action == "remind":
            #     msg = Message("Overdue reminder", sender = os.getenv("DEL_EMAIL"),recipients=[user_email]) 
            #     msg.body = "Please return your overdue booking >:("
            # elif action == "cancel":
            #     msg = Message("Your booking has been cancelled", sender = os.getenv("DEL_EMAIL"),recipients=[user_email]) 
            #     msg.body = "Cancelled"
            # elif action == "reject":
            #     msg = Message("Your booking has been rejected", sender = os.getenv("DEL_EMAIL"),recipients=[user_email]) 
            #     msg.body = "for x reason"
            # mail.send(msg)
            print("Success!!")
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 500


