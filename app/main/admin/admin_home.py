from flask import Blueprint, abort, redirect, url_for, session, render_template, jsonify, request, flash
from extensions import db
from models import User, LoanStatus, UserRole, StudioBooking,StudioBookingStatus, EquipmentLoan
from flask_login import login_required, current_user
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import create_async_engine
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

    loan_items = {booking_id: dict(counter) 
    for booking_id, counter in count_equip_booking_items(equip_bookings).items()}
    type_lookup = equip_type_lookup()

    print(serialized_equip_bookings)
    user_lookup = {} #dict of user ids and corresponding name
    for i in db.session.execute(select(User)).scalars().all():
        user_lookup[i.id] = i.name

    return render_template("admin/admin_home.html", equip_bookings = equip_bookings, user_lookup = user_lookup, 
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
                                        