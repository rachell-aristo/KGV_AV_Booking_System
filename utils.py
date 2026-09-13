from flask import Blueprint, redirect, url_for, session, render_template, jsonify, request, flash
from extensions import db
from models import EquipmentType, LoanStatus, EquipmentLoanItem, StudioBooking,StudioBookingStatus, EquipmentLoan
from flask_login import login_required, current_user
from sqlalchemy import select
from collections import Counter


def count_equip_booking_items():
        booking_counts = {}
        equip_bookings = db.session.execute(select(EquipmentLoan).where(EquipmentLoan.fk_user_id == current_user.id)).scalars().all() 
        equip_booking_ids = [b.id for b in equip_bookings]
        loan_items = db.session.execute(select(EquipmentLoanItem).where(EquipmentLoanItem.fk_loan_id.in_(equip_booking_ids))).scalars().all() 
        for booking in equip_booking_ids:
            item_names = []
            for item in loan_items:
                if item.fk_loan_id == booking:
                    item_names.append(item.fk_equipment_type_id)
            booking_counts[booking] = Counter(item_names)
        return booking_counts

###########################


def equip_type_lookup():
    equip_type_lookup = {} #dict of equipment_type ids and corresponding name of item
    for i in db.session.execute(select(EquipmentType)).scalars().all():
        equip_type_lookup[i.id] = i.name
    return(equip_type_lookup)
