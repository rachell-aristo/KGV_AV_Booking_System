from flask import Blueprint, redirect, url_for, session, render_template, jsonify, request, flash
from extensions import db
from models import StudioSetupOptions, StudioSpace, TimeSlot, StudioBooking,StudioBookingStatus,StudioBookingSetupSelection
from auth import login_required
from sqlalchemy import select

student_home = Blueprint('student_home', __name__)

@student_home.route('/student_home')
@login_required
def fetch_date():
    user_id = session.get('user_id')
    current_bookings = []
    past_bookings = []
    studio_bookings = db.session.execute(select(StudioBooking).where(StudioBooking.fk_user_id == user_id)).scalars().all()
    for i in studio_bookings:
        if i.studio_booking_status == (StudioBookingStatus.PENDING) or i.studio_booking_status == (StudioBookingStatus.CONFIRMED):
            current_bookings.append(i)
        elif i.studio_booking_status == (StudioBookingStatus.FINISHED) or i.studio_booking_status == (StudioBookingStatus.REJECTED):
            past_bookings.append(i)
    for i in studio_bookings:
        print(i.id, i.setup_selections)
    return render_template("student_home.html", current_bookings = current_bookings, past_bookings = past_bookings)
