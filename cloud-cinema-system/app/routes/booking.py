from flask import Blueprint, render_template, request, redirect, url_for, current_app, session, flash
from collections import OrderedDict

booking_bp = Blueprint('booking', __name__)

@booking_bp.route('/book/<int:showtime_id>', methods=['GET', 'POST'])
def select_seats(showtime_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    db = current_app.get_db_connection()

    if request.method == 'POST':
        selected = request.form.getlist('seat')
        if not selected:
            flash('Please select at least one seat.')
            return redirect(url_for('booking.select_seats', showtime_id=showtime_id))

        try:
            seat_ids = [int(s) for s in selected]
        except ValueError:
            flash('Invalid seat selection.')
            return redirect(url_for('booking.select_seats', showtime_id=showtime_id))

        try:
            with db.cursor() as cursor:
                # Check for already booked seats
                placeholders = ','.join(['%s'] * len(seat_ids))
                sql = f"""
                    SELECT bs.seat_id
                    FROM booking_seats bs
                    JOIN bookings b ON bs.booking_id = b.booking_id
                    WHERE b.showtime_id = %s AND bs.seat_id IN ({placeholders})
                """
                cursor.execute(sql, tuple([showtime_id] + seat_ids))
                conflicts = cursor.fetchall()
                if conflicts:
                    flash('One or more selected seats are no longer available. Please choose different seats.')
                    return redirect(url_for('booking.select_seats', showtime_id=showtime_id))

                # Insert booking
                user_id = session['user_id']
                cursor.execute(
                    "INSERT INTO bookings (user_id, showtime_id) VALUES (%s, %s)",
                    (user_id, showtime_id)
                )
                booking_id = cursor.lastrowid

                # Insert booked seats
                for sid in seat_ids:
                    cursor.execute(
                        "INSERT INTO booking_seats (booking_id, seat_id) VALUES (%s, %s)",
                        (booking_id, sid)
                    )

                db.commit()
            return render_template('booking_confirmation.html', booking_id=booking_id, seat_ids=seat_ids)
        except Exception as e:
            db.rollback()
            flash('An error occurred while creating the booking.')
            return redirect(url_for('booking.select_seats', showtime_id=showtime_id))
        finally:
            db.close()

    # GET request: show seat layout
    try:
        with db.cursor() as cursor:
            # Fetch showtime info
            cursor.execute(
                "SELECT s.*, m.title FROM showtimes s JOIN movies m ON s.movie_id = m.movie_id WHERE s.showtime_id = %s",
                (showtime_id,)
            )
            show = cursor.fetchone()
            if not show:
                flash('Showtime not found.')
                return redirect(url_for('main.index'))

            screen_id = show['screen_id']

            # Fetch seats ordered
            cursor.execute(
                "SELECT * FROM seats WHERE screen_id = %s ORDER BY seat_row, seat_number",
                (screen_id,)
            )
            raw_seats = cursor.fetchall()

            # Group seats by row
            seat_map = OrderedDict()
            for seat in raw_seats:
                seat_map.setdefault(seat['seat_row'], []).append(seat)

            # Fetch booked seats
            cursor.execute("""
                SELECT bs.seat_id FROM booking_seats bs
                JOIN bookings b ON bs.booking_id = b.booking_id
                WHERE b.showtime_id = %s
            """, (showtime_id,))
            booked = cursor.fetchall()
            booked_ids = {r['seat_id'] for r in booked}

    finally:
        db.close()

    return render_template('seat_selection.html', show=show, seat_map=seat_map, booked_ids=booked_ids)
