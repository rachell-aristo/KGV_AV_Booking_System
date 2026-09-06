from flask import Blueprint, redirect, url_for, session, render_template, jsonify, request, flash
from flask_login import current_user
from extensions import db
from models import StudioSetupOptions, StudioSpace, TimeSlot, StudioBooking,StudioBookingStatus,StudioBookingSetupSelection, User, UserRole
from flask_login import login_required
from sqlalchemy import select

studio_booking = Blueprint('studio_booking', __name__)

@studio_booking.route('/studiobooking')
@login_required
def data_fetch():
    studio_spaces = db.session.execute(select(StudioSpace)).scalars().all() #Sets all studio spaces to var
    setup_options = db.session.execute(select(StudioSetupOptions)).scalars().all() #Sets all studio setup options to var
    bookings = db.session.execute(select(StudioBooking)).scalars().all() #Sets all studio bookings to var
    time_slots= db.session.execute(select(TimeSlot)).scalars().all() #Sets all timeslots to var
    booked_day_dict = {} #in this dict, keys are tuples with (date,studio_id)
    fully_booked_days = {} #structure of fully_booked is a dict where keys = studio_id and value = array of dates where it's fully booked for that studio
    for i in bookings: 
        #for loop to go through all bookings. Finds out how many times each studio space is booked on that day. 
        # Since only limited slots a day, can use that to compare later if the day is fully booked
        if (i.studio_booking_date, i.fk_studio_space_id) in booked_day_dict:
            booked_day_dict[(i.studio_booking_date, i.fk_studio_space_id)] += 1
        elif i.studio_booking_date not in booked_day_dict: 
            #if this studio/date combo has not been seen, start the count at 1
            booked_day_dict[(i.studio_booking_date, i.fk_studio_space_id)] = 1

    for key, value in booked_day_dict.items(): #loop through booked_day_dict, 
        if key[1] not in fully_booked_days: #if this studio_id is not in fully_booked_days, make a new array for its values
            fully_booked_days[key[1]] = []
        if value >= len(time_slots): 
            # if the number of booked slots for that studio on that day is more or equal to # of timeslots, add to fully-booked
            fully_booked_days[key[1]].append(key[0].strftime("%Y-%m-%d")) #appends the formatted date of when studio is fully booked to fully_booked_days
    print(fully_booked_days)
    print(studio_spaces)
    return render_template("studio_booking.html", studio_spaces = studio_spaces,setup_options = setup_options, time_slots = time_slots, fully_booked_days = fully_booked_days)

@studio_booking.route('/booked_slots')
@login_required
def get_booked_slots():
    selected_date = request.args.get('date') #gets the value of date from url
    selected_studio = request.args.get('studio') #gets the value ofstudio from url
    if not selected_date or not selected_studio: #if either value is missing, return empty list so no error
        return jsonify([])
    booked = db.session.execute(select(StudioBooking).where(StudioBooking.studio_booking_date == selected_date, StudioBooking.fk_studio_space_id == selected_studio)).scalars()
    #booked (iterable array like thing) contains all bookings where booking date = currently selected date
    booked_slot_id = []
    for i in booked: #
        booked_slot_id.append(i.fk_slot_id)  #add all the booked slot ids to booked_slot_id
    return jsonify(booked_slot_id) #return JSON data to frontend

def missing_input(message):
    flash(message)
    return redirect(url_for('studio_booking.data_fetch')) 
    #if any part of form is not filled in, redirect user to /data fetch (this is a back up only html verification fails)

@studio_booking.route('/submit_studio_booking', methods=['POST']) #using POST method so submitted data is not publicly shown in URL
@login_required
def submit_studio_booking():
    #gets all the needed values from html
    studio_booking_date = request.form.get('booking-date') 
    student_studio_booking_reason = request.form.get('booking-reason')
    student_studio_booking_notes = request.form.get('booking-notes')
    timeslot = request.form.get('timeslot')
    studio_space = request.form.get('studio-space')
    fk_studio_setup_options_id = request.form.get('setup-select')

    #if any data is missing when trying to submit, return error message which is inserted into HTML
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

    #make new booking record
    
    new_record = StudioBooking(
            studio_booking_date = studio_booking_date,
            studio_booking_status = StudioBookingStatus.PENDING,
            student_studio_booking_reason = student_studio_booking_reason,
            student_studio_booking_notes = student_studio_booking_notes,
            fk_slot_id = timeslot,
            fk_studio_space_id = studio_space,
            fk_user_id=current_user.id
        )
    db.session.add(new_record)
    db.session.commit()

    setup = StudioBookingSetupSelection(
        fk_studio_setup_options_id = fk_studio_setup_options_id,
        fk_studio_booking_id = new_record.id
    )
    db.session.add(setup)
    db.session.commit()
    return redirect(url_for('studio_booking.success_booking')) #redirect user to success booking page

@studio_booking.route('/success_booking')
@login_required
def success_booking():
    return render_template("success_booking.html")




 