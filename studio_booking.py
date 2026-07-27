from flask import Blueprint, redirect, url_for, session, render_template, jsonify, request, flash
from extensions import db
from models import StudioSetupOptions, StudioSpace, TimeSlot, StudioBooking,StudioBookingStatus,StudioBookingSetupSelection
from auth import login_required
from sqlalchemy import select

studio_booking = Blueprint('studio_booking', __name__)

@studio_booking.route('/studiobooking')
@login_required
def data_fetch():
    studio_spaces = db.session.execute(select(StudioSpace)).scalars().all()
    setup_options = db.session.execute(select(StudioSetupOptions)).scalars().all()
    bookings = db.session.execute(select(StudioBooking)).scalars().all()
    time_slots= db.session.execute(select(TimeSlot)).scalars().all()
    booked_day_dict = {}
    fully_booked_days = {}
    for i in bookings:
        if (i.studio_booking_date, i.fk_studio_space_id) in booked_day_dict:
            booked_day_dict[(i.studio_booking_date, i.fk_studio_space_id)] += 1
        elif i.studio_booking_date not in booked_day_dict:
            booked_day_dict[(i.studio_booking_date, i.fk_studio_space_id)] = 1

    for key, value in booked_day_dict.items():
        if key[1] not in fully_booked_days:
            fully_booked_days[key[1]] = []
        if value >= len(time_slots):
            fully_booked_days[key[1]].append(key[0].strftime("%Y-%m-%d"))
    print(fully_booked_days)
    return render_template("studio_booking.html", studio_spaces = studio_spaces,setup_options = setup_options, time_slots = time_slots, fully_booked_days = fully_booked_days)

@studio_booking.route('/booked_slots')
@login_required
def get_booked_slots():
    selected_date = request.args.get('date')
    selected_studio = request.args.get('studio')
    if not selected_date or not selected_studio:
        return jsonify([])
    booked = db.session.execute(select(StudioBooking).where(StudioBooking.studio_booking_date == selected_date, StudioBooking.fk_studio_space_id == selected_studio)).scalars()
    booked_slot_id = []
    for i in booked:
        booked_slot_id.append(i.fk_slot_id)
    return jsonify(booked_slot_id)

def missing_input(message):
    flash(message)
    return redirect(url_for('studio_booking.data_fetch'))

@studio_booking.route('/submit_studio_booking', methods=['POST'])
@login_required
def submit_studio_booking():
    studio_booking_date = request.form.get('booking-date')
    student_studio_booking_reason = request.form.get('booking-reason')
    student_studio_booking_notes = request.form.get('booking-notes')
    timeslot = request.form.get('timeslot')
    studio_space = request.form.get('studio-space')
    fk_studio_setup_options_id = request.form.get('setup-select')
    
    if not studio_booking_date:
        return missing_input("Please select a booking date.")
    elif not timeslot:
        return missing_input("Please select a timeslot.")
    elif not studio_space:
        return missing_input("Please select a studio space.")
    elif not fk_studio_setup_options_id:
        return missing_input("Please select a studio setup option.")
    elif not student_studio_booking_reason:
        return missing_input("Please input a booking reason.")
    
    new_record = StudioBooking(
            studio_booking_date = studio_booking_date,
            studio_booking_status = StudioBookingStatus.PENDING,
            student_studio_booking_reason = student_studio_booking_reason,
            student_studio_booking_notes = student_studio_booking_notes,
            fk_slot_id = timeslot,
            fk_studio_space_id = studio_space,
            fk_user_id=session.get('user_id')
        )
    db.session.add(new_record)
    db.session.commit()

    setup = StudioBookingSetupSelection(
        fk_studio_setup_options_id = fk_studio_setup_options_id,
        fk_studio_booking_id = new_record.id
    )
    db.session.add(setup)
    db.session.commit()
    return redirect(url_for('studio_booking.success_booking'))

@studio_booking.route('/success_booking')
@login_required
def success_booking():
    return render_template("success_booking.html")



 