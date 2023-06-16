import datetime as dt
from datetime import datetime
from flask import flash, render_template, request, redirect, url_for
from flask import current_app as app
from sqlalchemy import func
from .database import db 
from .models import Master_User, Flights, My_Bookings

@app.route("/", methods = ['GET'])
def home():
    return render_template("home.html")

@app.route("/login/admin", methods = ['GET', 'POST'])
def admin_login():
    if request.method == 'GET':
        return render_template("admin_login.html")
    elif request.method == 'POST':
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        if username == '' or email == '' or password == '':
            return redirect(url_for('admin_login'), errors = errors)
        # print(username, email, password)
        users = db.session.query(Master_User).filter(Master_User.email == email).all()
        for user in users:
            if user == None:
                return redirect(url_for('admin_login'))
            if user.password != password:
                return redirect(url_for('admin_login'))
            if user.user_type == 'admin':
                return redirect('/admin_dashboard')
    return redirect(url_for('admin_login'))

@app.route("/signup/user", methods = ['GET', 'POST'])
def user_signup():
    if request.method == 'GET':
        return render_template("user_signup.html")
    elif request.method == 'POST':
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]
        if username == '' or email == '' or password == '' or confirm_password == '':
            flash("Please fill all the fields")
            return redirect(url_for('user_signup'))
        user = db.session.query(Master_User).filter(Master_User.email == email).all()
        if len(user)!=0:
            flash("User already exists")
            return redirect(url_for('user_login'))
        if password == confirm_password:
            new_user = Master_User(username = username, email = email, password = password)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('user_login'))
        return redirect(url_for('user_signup'))

@app.route("/login/user", methods = ['GET', 'POST'])
def user_login():
    if request.method == 'GET':
        return render_template("user_login.html")
    elif request.method == 'POST':
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        if username == '' or email == '' or password == '':
            alert = "Please fill all the fields"
            return redirect(url_for('user_login'))
        user = db.session.query(Master_User).filter(Master_User.email == email).all()
        if len(user)==0:
            return redirect(url_for('user_login'))
        if user[0].password != password:
            return redirect(url_for('user_login'))
        if user[0].user_type == 'admin':
            alert = "You are not authorized to access this page"
            return redirect(url_for('user_login'))
        else:
            return redirect('/user_dashboard/{}'.format(user[0].id))
    
@app.route("/user_dashboard/<int:user_id>", methods = ['GET'])
def user_dashboard(user_id):
    flights = db.session.query(Flights).all()
    return render_template("user_dashboard.html", flights = flights, user_id = user_id)

@app.route("/admin_dashboard", methods = ['GET'])
def admin_dashboard():
    flights = db.session.query(Flights).all()
    return render_template("admin_dashboard.html", flights = flights)

@app.route("/add_flight", methods = ['GET', 'POST'])
def add_flight():
    if request.method == 'GET':
        return render_template("add_flight.html")
    elif request.method == 'POST':
        flight_number = request.form["flight_number"]
        origin = request.form["origin"]
        destination = request.form["destination"]
        date = request.form["date"]
        arrival_time = request.form["arrival_time"]
        departure_time = request.form["departure_time"]
        duration = request.form["duration"]
        
        if flight_number == '' or origin == '' or destination == '' or date == '' or arrival_time == '' or departure_time == '' or duration == '':
            alert = "Please fill all the fields"
            return redirect(url_for('add_flight'))
        
        new_flight = Flights(flight_number = flight_number, origin = origin, destination = destination, date = date, arrival_time = arrival_time, departure_time = departure_time, duration = duration)
        
        db.session.add(new_flight)
        db.session.commit()
        return redirect(url_for('admin_dashboard'))
    
@app.route("/remove_flight/<int:flight_id>", methods = ['GET'])
def remove_flight(flight_id):
    flight = db.session.query(Flights).filter(Flights.id == flight_id).first()
    db.session.delete(flight)
    bookings = db.session.query(My_Bookings).filter(My_Bookings.f_id == flight_id).all()
    for booking in bookings:
        db.session.delete(booking)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route("/book_flight/<int:flight_id>/<int:user_id>", methods = ['GET'])
def book_flight(flight_id, user_id):
    flight = db.session.query(Flights).filter(Flights.id == flight_id).first()
    user = db.session.query(Master_User).filter(Master_User.id == user_id).first()
    new_booking = My_Bookings(f_id = flight.id, u_id = user.id)
    flight.capacity -= 1
    db.session.add(new_booking)
    db.session.commit()
    flights = db.session.query(Flights).all()
    return redirect(url_for('user_dashboard', flights = flights, user_id = user.id))

@app.route("/my_bookings/<int:user_id>", methods = ['GET'])
def my_bookings(user_id):
    bookings = db.session.query(My_Bookings).filter(My_Bookings.u_id == user_id).all()
    flight_id = []
    for booking in bookings:
        flight_id.append(booking.f_id)
    flights = []
    for id in flight_id:
        flight = db.session.query(Flights).filter(Flights.id == id).first()
        flights.append(flight)
    return render_template("my_bookings.html", flights = flights, user_id = user_id)

@app.route("/cancel_booking/<int:flight_id>/<int:user_id>", methods = ['GET'])
def cancel_booking(flight_id, user_id):
    booking = db.session.query(My_Bookings).filter(My_Bookings.f_id == flight_id).filter(My_Bookings.u_id == user_id).first()
    db.session.delete(booking)
    db.session.commit()
    flight = db.session.query(Flights).filter(Flights.id == flight_id).first()
    flight.capacity += 1
    db.session.commit()
    return redirect(url_for('my_bookings', user_id = user_id))

@app.route("/view_bookings", methods = ['GET'])
def view_bookings():
    bookings = db.session.query(My_Bookings).all()
    flight_id = []
    for booking in bookings:
        flight_id.append(booking.f_id)
    flights = []
    for id in flight_id:
        flight = db.session.query(Flights).filter(Flights.id == id).first()
        flights.append(flight)
    return render_template("view_bookings.html", flights = flights)

@app.route('/search/<int:user_id>', methods = ['GET', 'POST'])
def search(user_id):
    if request.method == 'GET':
        return render_template("search_flight.html", user_id = user_id)
    elif request.method == 'POST':
        origin = request.form["origin"]
        destination = request.form["destination"]
        date = request.form["date"]
        start_time = request.form["start_time"]
        end_time = request.form["end_time"]
        flights = db.session.query(Flights).filter(Flights.origin == origin).filter(Flights.destination == destination).filter(Flights.date == date).filter(Flights.arrival_time.between(start_time, end_time)).all()
        user = db.session.query(Master_User).filter(Master_User.id == user_id).first()

        return render_template("search.html", flights = flights, user_id = user.id)

@app.route("/admin_logout", methods = ['GET'])
def admin_logout():
    return redirect(url_for('home'))

@app.route("/user_logout", methods = ['GET'])
def user_logout():
    return redirect(url_for('home'))