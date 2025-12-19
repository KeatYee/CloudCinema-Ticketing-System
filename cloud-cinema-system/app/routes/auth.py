from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Hash the password for security
        hashed_pw = generate_password_hash(password)
        
        db = current_app.get_db_connection()
        try:
            with db.cursor() as cursor:
                # Check if email is already taken
                cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
                if cursor.fetchone():
                    flash("Email already registered!")
                    return redirect(url_for('auth.register'))
                
                # Insert new user
                cursor.execute("INSERT INTO users (name, email, pass) VALUES (%s, %s, %s)", 
                               (name, email, hashed_pw))
                db.commit()
            return redirect(url_for('auth.login'))
        finally:
            db.close()
    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        db = current_app.get_db_connection()
        try:
            with db.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
                user = cursor.fetchone()
                
                # Check if user exists and password matches the hash
                if user and check_password_hash(user['pass'], password):
                    session['user_id'] = user['user_id']
                    session['name'] = user['name']
                    # store role for quick template checks (admin/customer)
                    session['role'] = user.get('role', 'customer')
                    return redirect(url_for('main.index'))
                else:
                    flash("Invalid credentials!")
        finally:
            db.close()
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.index'))


@auth_bp.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    user_id = session['user_id']
    db = current_app.get_db_connection()
    bookings = []
    try:
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM bookings WHERE user_id = %s ORDER BY booking_time DESC", (user_id,))
            rows = cursor.fetchall()
            for b in rows:
                # fetch showtime/movie/screen
                cursor.execute("SELECT s.*, m.title, sc.screen_name FROM showtimes s JOIN movies m ON s.movie_id = m.movie_id JOIN screens sc ON s.screen_id = sc.screen_id WHERE s.showtime_id = %s", (b['showtime_id'],))
                show = cursor.fetchone()

                # fetch seats
                cursor.execute("SELECT se.seat_row, se.seat_number FROM booking_seats bs JOIN seats se ON bs.seat_id = se.seat_id WHERE bs.booking_id = %s", (b['booking_id'],))
                seat_rows = cursor.fetchall()

                bookings.append({
                    'booking': b,
                    'show': show,
                    'seats': seat_rows
                })
    finally:
        db.close()

    return render_template('profile.html', bookings=bookings)