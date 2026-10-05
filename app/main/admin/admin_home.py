from flask import Blueprint, abort, current_app, url_for, session, render_template, jsonify, request, flash
from flask_mail import Mail, Message
from ..extensions import db, mail
from ..models import User, LoanStatus, UserRole, StudioBooking, EquipmentCategory, Asset, EquipmentLoan, StudioSpace, TimeSlot, StudioBookingStatus, EquipmentType, StudioBookingSetupSelection
from ..utils import count_equip_booking_items, equip_type_lookup, studio_type_lookup, slot_type_lookup, studio_setup_lookup
import os

from flask_login import login_required, current_user
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import create_async_engine

#next step: include booking reason + extra notes in approve email


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
        type_lookup = equip_type_lookup("table")

        assets = db.session.execute(select(Asset)).scalars().all()
        serialized_assets = [item.to_dict() for item in assets]

        user_lookup = {} #dict of user ids and corresponding name
        for i in db.session.execute(select(User)).scalars().all():
            user_lookup[i.id] = i.name

        studio_lookup = {}
        for i in db.session.execute(select(StudioSpace)).scalars().all():
            studio_lookup[i.id] = i.name

        slot_lookup = {}
        for i in db.session.execute(select(TimeSlot)).scalars().all():
            slot_lookup[i.id] = i.name

        type_to_cat_lookup = {}
        for i in db.session.execute(select(EquipmentType)).scalars().all():
            category = db.session.execute(select(EquipmentCategory.name).where(i.fk_equipment_category_id == EquipmentCategory.id)).scalar()
            type_to_cat_lookup[i.id] = category

        loan_status = []
        for i in LoanStatus:
            loan_status.append(i.value)
        loan_status.remove("overdue")

        return render_template("admin/admin_home.html", s_studio_bookings = serialized_studio_bookings, equip_bookings = equip_bookings, 
                            user_lookup = user_lookup, s_users = serialized_users,
                            loan_items = loan_items, type_lookup = type_lookup, s_equip_bookings = serialized_equip_bookings,
                            studio_lookup = studio_lookup, slot_lookup = slot_lookup, s_assets = serialized_assets,
                            type_to_cat_lookup = type_to_cat_lookup, loan_status = loan_status
                            )

@admin_home.route('/update_loan_status', methods=['POST'])
@login_required
def update_loan_status():

    action_dict = {
        "confirmed" : "approve",
        "rejected" : "reject",
        "canceled" : "cancel"
    }

    if current_user.role != UserRole.ADMIN:
        abort(401)
    else:
        data = request.json
        loan_id = int(data.get('loan_id'))
        new_status = data.get('new_status')
        reject_reason = data.get('reject')
        type = data.get('type')

        try:
            if type == "EQUIP":
                enum_status = LoanStatus(new_status.lower())
                stmt = update(EquipmentLoan).where(EquipmentLoan.id == loan_id).values(status = enum_status, admin_reject_reason = reject_reason)
            elif type == "STUDIO":
                enum_status = StudioBookingStatus(new_status.lower())
                stmt = update(StudioBooking).where(StudioBooking.id == loan_id).values(studio_booking_status = enum_status, admin_reject_reason = reject_reason)
            else:
                return jsonify({'success': False, 'message': "Unknown loan type"}),400
            db.session.execute(stmt)
            db.session.commit()
        except Exception as e:
            current_app.logger.exception(e)
            db.session.rollback()
            return jsonify({'success': False, 'message': "Failed to update to database"}),500
        
        action = action_dict.get(new_status.lower())
        email_message = None
        email_sent = None
        if action is not None:
            email, error, name, book_date, book_content = get_student_email(type,loan_id)
            if error:
                email_sent = False
                email_message = "Student email not found on file"
            else:
                email_success, email_error = send_booking_email(action, loan_id, email, name, book_date, book_content)
                if email_success:
                    email_sent = True
                elif email_error:
                    email_sent = False
                    email_message = email_error
        return jsonify({"success":True, "email_sent":email_sent,"email_message":email_message})
        


def get_student_email(booking_type, booking_id):
    if booking_type not in ("EQUIP", "STUDIO"):
        return None, "Unknown booking type"  
        #in case of potential typos in type etc
    elif booking_type == "EQUIP":
        user_id = db.session.execute(select(EquipmentLoan.fk_user_id).where(EquipmentLoan.id == booking_id)).scalar()
        user_name = db.session.execute(select(User.name).where(User.id == user_id)).scalar()
        book_start = db.session.execute(select(EquipmentLoan.loan_start_date).where(EquipmentLoan.id == booking_id)).scalar()
        book_end = db.session.execute(select(EquipmentLoan.loan_end_date).where(EquipmentLoan.id == booking_id)).scalar()
        book_date = str(book_start) + ' to ' + str(book_end)
        equip_bookings = db.session.execute(select(EquipmentLoan).where(EquipmentLoan.id == booking_id)).scalars().all()
        book_counter_obj = count_equip_booking_items(equip_bookings)
        book_content = ""
        for id, items in book_counter_obj.items():
            for item, quantity in items.items():
                item_string = str(equip_type_lookup(item))
                book_content += item_string + " | Quantity: " + str(quantity) + "\n"
    elif booking_type == "STUDIO":
        user_id = db.session.execute(select(StudioBooking.fk_user_id).where(StudioBooking.id == booking_id)).scalar()
        user_name = db.session.execute(select(User.name).where(User.id == user_id)).scalar()
        book_date = db.session.execute(select(StudioBooking.studio_booking_date).where(StudioBooking.id == booking_id)).scalar()
        book_slot= db.session.execute(select(StudioBooking.fk_slot_id).where(StudioBooking.id == booking_id)).scalar()
        book_space_id = db.session.execute(select(StudioBooking.fk_studio_space_id).where(StudioBooking.id == booking_id)).scalar()
        setup_id = db.session.execute(select(StudioBookingSetupSelection.fk_studio_setup_options_id).where(StudioBookingSetupSelection.fk_studio_booking_id == booking_id)).scalar()
        book_content = studio_type_lookup(book_space_id) + "\n" + "Time Slot: " + slot_type_lookup(book_slot) + "\n" + "Set up: " + studio_setup_lookup(setup_id)
    if user_id is None:
        return None, "Booking not found"

    user_email = db.session.execute(select(User.email).where(User.id == user_id)).scalar()
    if not user_email:
        return None, "No email address on file"
    else:
        return user_email, None, user_name, book_date, book_content

def send_booking_email(action, booking_id, user_email, user_name, book_date, book_content, reason=None):
    if action == "approve":
        msg = Message("Booking confirmed (#)", sender = os.getenv("DEL_EMAIL"),recipients=[user_email]) 
        print(user_name,book_date,book_content)
        msg.body = render_template("admin/booking_success_email.txt", name = user_name, book_date = book_date, book_content = book_content)
    elif action == "remind":
        msg = Message("Overdue reminder", sender = os.getenv("DEL_EMAIL"),recipients=[user_email]) 
        msg.body = "Please return your overdue booking >:("
    elif action == "cancel":
        msg = Message("Your booking has been cancelled", sender = os.getenv("DEL_EMAIL"),recipients=[user_email]) 
        msg.body = "Cancelled"
    elif action == "reject":
        msg = Message("Your booking has been rejected", sender = os.getenv("DEL_EMAIL"),recipients=[user_email]) 
        msg.body = "Your booking was rejected because:"+ (reason or "No reason given")
    else:
        return False, "Unknown action, email not sent"
    try:
        mail.send(msg)
        print("Email sent!")
        return True, None
    except Exception as e:
        current_app.logger.exception(e)
        return False, "Email failed to send."


@admin_home.route('/send_mail', methods=['POST'])
@login_required
def send_email():
    if current_user.role != UserRole.ADMIN:
        abort(401)
    else:
        data = request.json
        action = data.get('action')
        record_id = data.get('id')
        type = data.get('type')

        if action not in ("approve","remind","cancel","reject"):
            return jsonify({'success': False, 'message': 'Unknown action.'}), 400    
        
        email, error, name, book_date, book_content = get_student_email(type,record_id)
        if error:
            return jsonify({'success': False, 'message':error}), 404  
        success, message = send_booking_email(action, record_id, email, name, book_date, book_content)

        if success:
            return jsonify({'success': True, 'message': "Email sent"})
        else:
            return jsonify({'success': False, 'message': message}), 500


        


