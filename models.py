from extensions import db
import enum
from sqlalchemy import ForeignKey
from sqlalchemy import Time

DefaultLoanDays = 3

#SQLAlchemy names are in PascalCase, references to MYSQL table names are in lowercase. Both are singular
class UserRole(str, enum.Enum):
    ADMIN = "admin"
    STUDENT = "student"
    TEACHER = "teacher"

class AssetStatus(str, enum.Enum):
    AVALIABLE = "avaliable"
    UNAVALIABLE = "unavaliable"
    UPCOMING = "upcoming"

class LoanStatus(str, enum.Enum):
    OVERDUE = "overdue"
    PENDING = "pending"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"
    FINISHED = "finished"


class PickUpTime(str, enum.Enum):
    BEFORE = "before" #before school
    BREAK = "break"
    LUNCH = "lunch"
    AFTER = "after"

class StudioBookingStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"
    FINISHED = "finished"

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    google_sub_id = db.Column(db.String(255), nullable = False)
    name = db.Column(db.String(255), nullable = False)
    role = db.Column(db.Enum(UserRole), nullable=False, default=UserRole.STUDENT)
    year_group = db.Column(db.Integer)
    email = db.Column(db.String(255), nullable = False)
    __table_args__ = (
        db.CheckConstraint('year_group <= 13 AND year_group >= 7'),
    )

    def __repr__(self):
        return f'<User {self.id} {self.name} ({self.role})>'
    
class EquipmentCategory(db.Model):
    __tablename__ = 'equipment_category'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable = False)
    
    def __repr__(self):
        return f'<EquipmentCategory {self.id} {self.name}>'

class StudioSpace(db.Model):
    __tablename__ = 'studio_space'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable = False)

    def __repr__(self):
        return f'<StudioSpace {self.id} {self.name}>'

class TimeSlot(db.Model):
    __tablename__ = 'time_slot'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable = False)
    time_start = db.Column(Time, nullable = False)
    time_end = db.Column(Time, nullable = False)

    def __repr__(self):
        return f'<TimeSlot {self.id} {self.name}>'

class EquipmentType(db.Model):
    __tablename__ = 'equipment_type'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable = False)
    quantity = db.Column(db.Integer, nullable = False)
    max_loan_days = db.Column(db.Integer, default = DefaultLoanDays, nullable = False)
    min_year_group = db.Column(db.Integer, nullable = False)
    loan_limit_quantity = db.Column(db.Integer, nullable = False)
    fk_equipment_category_id = db.Column(ForeignKey("equipment_category.id"), nullable=False)
    equipment_category = db.relationship('EquipmentCategory')

    def __repr__(self):
            return f'<EquipmentType {self.id} {self.name}>'

class Asset(db.Model):
    __tablename__ = 'asset'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable = False)
    barcode = db.Column(db.String(255), nullable = False)
    status = db.Column(db.Enum(AssetStatus), nullable=False)
    is_active = db.Column(db.Boolean, nullable = False )
    fk_equipment_type_id = db.Column(ForeignKey("equipment_type.id"), nullable=False)
    equipment_type = db.relationship('EquipmentType')

    def __repr__(self):
            return f'<Asset {self.id} {self.name}>'

class StudioSetupOptions(db.Model):
    __tablename__ = 'studio_setup_options'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable = False)
    fk_studio_space_id = db.Column(ForeignKey("studio_space.id"), nullable=False)
    studio_space = db.relationship('StudioSpace')

    def __repr__(self):
            return f'<StudioSetupOptions {self.id} {self.name}>'


class EquipmentLoan(db.Model):
    __tablename__ = 'equipment_loan'
    id = db.Column(db.Integer, primary_key=True)
    loan_start_date = db.Column(db.Date, nullable=False)
    loan_end_date = db.Column(db.Date, nullable=False)
    pickup_time = db.Column(db.Enum(PickUpTime),nullable = False)
    status = db.Column(db.Enum(LoanStatus), nullable=False)
    student_loan_reason = db.Column(db.Text, nullable = False)
    student_extra_notes = db.Column(db.Text, nullable = True)
    admin_reject_reason = db.Column(db.Text, nullable = True)
    fk_user_id = db.Column(ForeignKey("user.id"), nullable=False)
    user = db.relationship('User')

    def __repr__(self):
            return f'<EquipmentLoan {self.id} {self.fk_user_id}>'


class EquipmentLoanItem(db.Model):
    __tablename__ = 'equipment_loan_item'
    id = db.Column(db.Integer, primary_key=True)
    fk_equipment_type_id = db.Column(ForeignKey("equipment_type.id"), nullable=False)
    equipment_type = db.relationship('EquipmentType')

    fk_asset_id = db.Column(ForeignKey("asset.id"), nullable=True)
    asset = db.relationship('Asset')

    fk_loan_id = db.Column(ForeignKey("equipment_loan.id"), nullable=False)
    equipment_loan = db.relationship('EquipmentLoan')

    def __repr__(self):
            return f'<EquipmentLoanItem {self.id} {self.fk_loan_id}>'



class StudioBooking(db.Model):
    __tablename__ = 'studio_booking'
    id = db.Column(db.Integer, primary_key=True)
    studio_booking_date = db.Column(db.Date, nullable=False)
    studio_booking_status = db.Column(db.Enum(StudioBookingStatus), nullable = False)
    student_studio_booking_reason = db.Column(db.Text, nullable = False)
    student_studio_booking_notes = db.Column(db.Text, nullable = True)
    admin_reject_reason = db.Column(db.Text, nullable = True)
    fk_user_id = db.Column(ForeignKey("user.id"), nullable=False)
    user = db.relationship('User')

    fk_slot_id = db.Column(ForeignKey("time_slot.id"), nullable=False)
    slot = db.relationship('TimeSlot')

    fk_studio_space_id = db.Column(ForeignKey("studio_space.id"), nullable=False)
    studio_space = db.relationship('StudioSpace')

    def __repr__(self):
            return f'<StudioBooking {self.id} {self.fk_user_id}>'
    


class StudioBookingSetupSelection(db.Model):
    __tablename__ = 'studio_booking_setup_selection'
    id = db.Column(db.Integer, primary_key=True)

    fk_studio_setup_options_id = db.Column(ForeignKey("studio_setup_options.id"), nullable=False)
    studio_setup_options = db.relationship('StudioSetupOptions')

    fk_studio_booking_id = db.Column(ForeignKey("studio_booking.id"), nullable=False)
    studio_booking = db.relationship('StudioBooking')

    def __repr__(self):
        return f'<StudioBookingSetupSelection {self.id} {self.fk_studio_booking_id}>'

class StudentClass(db.Model):
    __tablename__ = 'student_class'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable = False)
    fk_teacher_id = db.Column(ForeignKey("user.id"), nullable=False)
    teacher = db.relationship('User')

class ClassEnrollment(db.Model):
    __tablename__ = 'class_enrollment'
    id = db.Column(db.Integer, primary_key=True)
    fk_class_id = db.Column(ForeignKey("student_class.id"), nullable=False)
    student_class = db.relationship('StudentClass')

    fk_student_id = db.Column(ForeignKey("user.id"), nullable=False)
    student = db.relationship('User')

    def __repr__(self):
        return f'<ClassEnrollment {self.id}>'



