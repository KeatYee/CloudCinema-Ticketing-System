from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        
        hashed_pw = generate_password_hash(password)
        
        db = current_app.get_db_connection()
        try:
            with db.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
                if cursor.fetchone():
                    flash("Email already registered!", "danger")
                    return redirect(url_for('auth.register'))
                
                cursor.execute("INSERT INTO users (name, email, pass) VALUES (%s, %s, %s)", 
                               (name, email, hashed_pw))
                db.commit()
            flash("Registration successful! Please login.", "success")
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
                
                # Check if user exists
                password_match = False
                if user:
                    try:
                        if check_password_hash(user['pass'], password):
                            password_match = True
                    except ValueError:
                        # Fallback for plain text passwords (if any exist)
                        if user['pass'] == password:
                            password_match = True

                if password_match:
                    session['user_id'] = user['user_id']
                    session['name'] = user['name']
                    role = user.get('role', 'customer')
                    session['role'] = role
                    
                    flash(f"Welcome back, {user['name']}!", "success")
                    
                    # Redirect based on Role
                    if role == 'admin':
                        return redirect(url_for('admin.admin_index'))
                    else:
                        return redirect(url_for('main.index'))
                else:
                    flash("Invalid credentials!", "danger")
        finally:
            db.close()
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('main.index'))

@auth_bp.route('/profile/edit', methods=['GET', 'POST'])
def edit_profile():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    user_id = session['user_id']
    db = current_app.get_db_connection()
    try:
        with db.cursor() as cursor:
            if request.method == 'POST':
                name = request.form.get('name')
                email = request.form.get('email')
                password = request.form.get('password')
                current_password = request.form.get('current_password')

                cursor.execute('SELECT user_id FROM users WHERE email = %s AND user_id != %s', (email, user_id))
                if cursor.fetchone():
                    flash('Email already in use.', 'danger')
                    return redirect(url_for('auth.edit_profile'))

                if password:
                    if not current_password:
                        flash('Enter current password to change it.', 'warning')
                        return redirect(url_for('auth.edit_profile'))
                    
                    cursor.execute('SELECT pass FROM users WHERE user_id = %s', (user_id,))
                    rowp = cursor.fetchone()
                    
                    curr_match = False
                    try:
                        if check_password_hash(rowp.get('pass', ''), current_password):
                            curr_match = True
                    except:
                        if rowp.get('pass') == current_password:
                            curr_match = True
                            
                    if not curr_match:
                        flash('Current password is incorrect.', 'danger')
                        return redirect(url_for('auth.edit_profile'))

                    hashed = generate_password_hash(password)
                    cursor.execute('UPDATE users SET name=%s, email=%s, pass=%s WHERE user_id=%s', (name, email, hashed, user_id))
                else:
                    cursor.execute('UPDATE users SET name=%s, email=%s WHERE user_id=%s', (name, email, user_id))

                db.commit()
                session['name'] = name
                flash('Profile updated.', 'success')
                return redirect(url_for('auth.profile'))

            cursor.execute('SELECT user_id, name, email, role, created_at FROM users WHERE user_id = %s', (user_id,))
            user = cursor.fetchone()
    finally:
        db.close()

    return render_template('profile_edit.html', user=user)

@auth_bp.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    user_id = session['user_id']
    db = current_app.get_db_connection()
    bookings = []
    user = None
    try:
        with db.cursor() as cursor:
            cursor.execute('SELECT user_id, name, email, role, created_at FROM users WHERE user_id = %s', (user_id,))
            user = cursor.fetchone()
            cursor.execute("SELECT * FROM bookings WHERE user_id = %s ORDER BY booking_time DESC", (user_id,))
            rows = cursor.fetchall()
            for b in rows:
                cursor.execute("SELECT s.*, m.title, m.image_url, sc.screen_name FROM showtimes s JOIN movies m ON s.movie_id = m.movie_id JOIN screens sc ON s.screen_id = sc.screen_id WHERE s.showtime_id = %s", (b['showtime_id'],))
                show = cursor.fetchone()
                
                cursor.execute("SELECT se.seat_row, se.seat_number FROM booking_seats bs JOIN seats se ON bs.seat_id = se.seat_id WHERE bs.booking_id = %s", (b['booking_id'],))
                seat_rows = cursor.fetchall()

                is_past = False
                cancelled_flag = bool(b.get('cancelled', 0)) if isinstance(b, dict) else False
                if show:
                    sd = show.get('show_date')
                    try:
                        if isinstance(sd, str):
                            sd = datetime.strptime(sd, '%Y-%m-%d').date()
                        if sd:
                            is_past = sd < datetime.now().date()
                    except Exception:
                        is_past = False

                bookings.append({
                    'booking': b,
                    'show': show,
                    'seats': seat_rows,
                    'is_past': is_past,
                    'cancelled': cancelled_flag
                })
    finally:
        db.close()

    upcoming = [b for b in bookings if not b['is_past'] and not b['cancelled']]
    past = [b for b in bookings if b['is_past'] or b['cancelled']]

    return render_template('profile.html', upcoming=upcoming, past=past, user=user)