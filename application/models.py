from .database import db 
import datetime as dt

class Master_User(db.Model):
	__tablename__ = 'master_user'
	id = db.Column(db.Integer, autoincrement = True, primary_key = True, nullable = False)
	username = db.Column(db.String, unique = True, nullable = False)
	user_type = db.Column(db.String, nullable = False, default = 'user')
	email = db.Column(db.String, unique = True, nullable = False)
	password = db.Column(db.String, nullable = False)
	
class Flights(db.Model):
    __tablename__ = 'flights'
    id = db.Column(db.Integer, autoincrement = True, primary_key = True, nullable = False)
    flight_number = db.Column(db.String, nullable = False)
    origin = db.Column(db.String, nullable = False)
    destination = db.Column(db.String, nullable = False)
    arrival_time = db.Column(db.String, nullable = False)
    departure_time = db.Column(db.String, nullable = False)
    date = db.Column(db.String, nullable = False)
    duration = db.Column(db.String, nullable = False)
    capacity = db.Column(db.Integer, nullable = False, default = 60)

class My_Bookings(db.Model):
    __tablename__ = 'my_bookings'
    id = db.Column(db.Integer, autoincrement = True, primary_key = True, nullable = False)
    u_id = db.Column(db.Integer, db.ForeignKey("master_user.id"), nullable = False)
    f_id = db.Column(db.Integer, db.ForeignKey("flights.id"), nullable = False)
    