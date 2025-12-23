from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, session

admin_bp = Blueprint('admin', __name__)


def _require_admin():
	# Simple guard: ensure logged in and role is 'admin'
	if 'user_id' not in session:
		return False, redirect(url_for('auth.login'))

	db = current_app.get_db_connection()
	try:
		with db.cursor() as cursor:
			cursor.execute("SELECT role FROM users WHERE user_id = %s", (session['user_id'],))
			user = cursor.fetchone()
			if not user or user.get('role') != 'admin':
				flash('Admin access required.')
				return False, redirect(url_for('main.index'))
	finally:
		db.close()
	return True, None


@admin_bp.route('/admin')
def admin_index():
	ok, resp = _require_admin()
	if not ok:
		return resp

	db = current_app.get_db_connection()
	try:
		with db.cursor() as cursor:
			cursor.execute("SELECT * FROM movies ORDER BY movie_id DESC")
			movies = cursor.fetchall()

			# only non-expired showtimes (show_date >= today)
			cursor.execute("SELECT s.*, m.title, sc.screen_name FROM showtimes s JOIN movies m ON s.movie_id = m.movie_id JOIN screens sc ON s.screen_id = sc.screen_id WHERE s.show_date >= CURDATE() ORDER BY s.show_date, s.show_time")
			showtimes = cursor.fetchall()
	finally:
		db.close()

	return render_template('admin_index.html', movies=movies, showtimes=showtimes)


@admin_bp.route('/admin/screens/add', methods=['GET', 'POST'])
def admin_add_screen():
	ok, resp = _require_admin()
	if not ok:
		return resp

	if request.method == 'POST':
		screen_name = request.form.get('screen_name')
		total_seats = request.form.get('total_seats')
		seats_per_row = request.form.get('seats_per_row')

		try:
			total_seats = int(total_seats)
			seats_per_row = int(seats_per_row)
		except Exception:
			flash('Total seats and seats per row must be numbers.')
			return redirect(url_for('admin.admin_add_screen'))

		if total_seats <= 0 or seats_per_row <= 0:
			flash('Numbers must be positive.')
			return redirect(url_for('admin.admin_add_screen'))

		db = current_app.get_db_connection()
		try:
			with db.cursor() as cursor:
				cursor.execute('INSERT INTO screens (screen_name, total_seats) VALUES (%s, %s)', (screen_name, total_seats))
				screen_id = cursor.lastrowid

				# helper: convert 0->A, 25->Z, 26->AA, etc.
				def row_label(n):
					label = ''
					n += 1
					while n > 0:
						n, rem = divmod(n-1, 26)
						label = chr(65 + rem) + label
					return label

				# compute number of rows needed
				num_rows = (total_seats + seats_per_row - 1) // seats_per_row
				seats_to_insert = []
				remaining = total_seats
				for r in range(num_rows):
					row = row_label(r)
					count_in_row = seats_per_row if remaining >= seats_per_row else remaining
					for num in range(1, count_in_row + 1):
						seats_to_insert.append((screen_id, row, num))
					remaining -= count_in_row

				if seats_to_insert:
					cursor.executemany('INSERT INTO seats (screen_id, seat_row, seat_number) VALUES (%s, %s, %s)', seats_to_insert)

				db.commit()

			flash('Screen (hall) added and seats initialized.')
			return redirect(url_for('admin.admin_index'))
		finally:
			db.close()

	return render_template('admin_add_screen.html')


@admin_bp.route('/admin/movies/<int:movie_id>/edit', methods=['GET', 'POST'])
def admin_edit_movie(movie_id):
	ok, resp = _require_admin()
	if not ok:
		return resp

	db = current_app.get_db_connection()
	try:
		with db.cursor() as cursor:
			if request.method == 'POST':
				title = request.form.get('title')
				duration = request.form.get('duration')
				rating = request.form.get('rating')
				description = request.form.get('description')
				image_url = request.form.get('image_url')
				cursor.execute("UPDATE movies SET title=%s, duration=%s, rating=%s, description=%s, image_url=%s WHERE movie_id=%s",
							   (title, duration, rating, description, image_url, movie_id))
				db.commit()
				flash('Movie updated.')
				return redirect(url_for('admin.admin_index'))

			cursor.execute('SELECT * FROM movies WHERE movie_id = %s', (movie_id,))
			movie = cursor.fetchone()
	finally:
		db.close()
	return render_template('admin_edit_movie.html', movie=movie)


@admin_bp.route('/admin/movies/<int:movie_id>/delete', methods=['POST'])
def admin_delete_movie(movie_id):
	ok, resp = _require_admin()
	if not ok:
		return resp
	db = current_app.get_db_connection()
	try:
		with db.cursor() as cursor:
			# delete showtimes for this movie first
			cursor.execute('DELETE FROM showtimes WHERE movie_id = %s', (movie_id,))
			cursor.execute('DELETE FROM movies WHERE movie_id = %s', (movie_id,))
			db.commit()
			flash('Movie and its showtimes deleted.')
	finally:
		db.close()
	return redirect(url_for('admin.admin_index'))


@admin_bp.route('/admin/showtimes/<int:showtime_id>/edit', methods=['GET', 'POST'])
def admin_edit_showtime(showtime_id):
	ok, resp = _require_admin()
	if not ok:
		return resp

	db = current_app.get_db_connection()
	try:
		with db.cursor() as cursor:
			if request.method == 'POST':
				movie_id = request.form.get('movie_id')
				screen_id = request.form.get('screen_id')
				show_date = request.form.get('show_date')
				show_time = request.form.get('show_time')
				price = request.form.get('price')
				cursor.execute('UPDATE showtimes SET movie_id=%s, screen_id=%s, show_date=%s, show_time=%s, price=%s WHERE showtime_id=%s',
							   (movie_id, screen_id, show_date, show_time, price, showtime_id))
				db.commit()
				flash('Showtime updated.')
				return redirect(url_for('admin.admin_index'))

			cursor.execute('SELECT * FROM showtimes WHERE showtime_id = %s', (showtime_id,))
			showtime = cursor.fetchone()
			cursor.execute('SELECT movie_id, title FROM movies ORDER BY title')
			movies = cursor.fetchall()
			cursor.execute('SELECT screen_id, screen_name FROM screens ORDER BY screen_name')
			screens = cursor.fetchall()
	finally:
		db.close()
	return render_template('admin_edit_showtime.html', showtime=showtime, movies=movies, screens=screens)


@admin_bp.route('/admin/showtimes/<int:showtime_id>/delete', methods=['POST'])
def admin_delete_showtime(showtime_id):
	ok, resp = _require_admin()
	if not ok:
		return resp
	db = current_app.get_db_connection()
	try:
		with db.cursor() as cursor:
			# delete bookings and booking_seats for this showtime first
			cursor.execute('SELECT booking_id FROM bookings WHERE showtime_id = %s', (showtime_id,))
			bks = cursor.fetchall()
			for bk in bks:
				cursor.execute('DELETE FROM booking_seats WHERE booking_id = %s', (bk['booking_id'],))
			cursor.execute('DELETE FROM bookings WHERE showtime_id = %s', (showtime_id,))
			cursor.execute('DELETE FROM showtimes WHERE showtime_id = %s', (showtime_id,))
			db.commit()
			flash('Showtime and its bookings deleted.')
	finally:
		db.close()
	return redirect(url_for('admin.admin_index'))


@admin_bp.route('/admin/bookings')
def admin_bookings():
	ok, resp = _require_admin()
	if not ok:
		return resp
	db = current_app.get_db_connection()
	try:
		with db.cursor() as cursor:
			# list current (non-expired and not cancelled) bookings
			cursor.execute("""
				SELECT b.booking_id, b.booking_time, u.name AS user_name,
					   s.show_date, s.show_time, m.title,
					   GROUP_CONCAT(CONCAT(se.seat_row, se.seat_number) ORDER BY se.seat_row, se.seat_number SEPARATOR ', ') AS seats
				FROM bookings b
				JOIN users u ON b.user_id = u.user_id
				JOIN showtimes s ON b.showtime_id = s.showtime_id
				JOIN movies m ON s.movie_id = m.movie_id
				LEFT JOIN booking_seats bs ON bs.booking_id = b.booking_id
				LEFT JOIN seats se ON bs.seat_id = se.seat_id
				WHERE s.show_date >= CURDATE() AND b.cancelled = 0
				GROUP BY b.booking_id
				ORDER BY s.show_date, s.show_time
			""")
			bookings = cursor.fetchall()
	finally:
		db.close()
	return render_template('admin_bookings.html', bookings=bookings)


@admin_bp.route('/admin/bookings/cancel', methods=['POST'])
def admin_cancel_booking():
	ok, resp = _require_admin()
	if not ok:
		return resp
	booking_id = request.form.get('booking_id')
	if not booking_id:
		flash('Invalid booking id.')
		return redirect(url_for('admin.admin_bookings'))
	try:
		bid = int(booking_id)
	except ValueError:
		flash('Invalid booking id.')
		return redirect(url_for('admin.admin_bookings'))

	db = current_app.get_db_connection()
	try:
		with db.cursor() as cursor:
			cursor.execute('DELETE FROM booking_seats WHERE booking_id = %s', (bid,))
			try:
				cursor.execute('UPDATE bookings SET cancelled = 1 WHERE booking_id = %s', (bid,))
			except Exception:
				cursor.execute('DELETE FROM bookings WHERE booking_id = %s', (bid,))
			db.commit()
			flash('Booking cancelled.')
	finally:
		db.close()
	return redirect(url_for('admin.admin_bookings'))


@admin_bp.route('/admin/movies/add', methods=['GET', 'POST'])
def admin_add_movie():
	ok, resp = _require_admin()
	if not ok:
		return resp

	if request.method == 'POST':
		title = request.form.get('title')
		duration = request.form.get('duration')
		rating = request.form.get('rating')
		description = request.form.get('description')
		image_url = request.form.get('image_url')

		db = current_app.get_db_connection()
		try:
			with db.cursor() as cursor:
				cursor.execute("INSERT INTO movies (title, duration, rating, description, image_url) VALUES (%s, %s, %s, %s, %s)",
							   (title, duration, rating, description, image_url))
				db.commit()
			flash('Movie added.')
			return redirect(url_for('admin.admin_index'))
		finally:
			db.close()

	return render_template('admin_add_movie.html')


@admin_bp.route('/admin/showtimes/add', methods=['GET', 'POST'])
def admin_add_showtime():
	ok, resp = _require_admin()
	if not ok:
		return resp

	db = current_app.get_db_connection()
	try:
		with db.cursor() as cursor:
			cursor.execute("SELECT movie_id, title FROM movies ORDER BY title")
			movies = cursor.fetchall()
			cursor.execute("SELECT screen_id, screen_name FROM screens ORDER BY screen_name")
			screens = cursor.fetchall()
	finally:
		db.close()

	if request.method == 'POST':
		movie_id = request.form.get('movie_id')
		screen_id = request.form.get('screen_id')
		show_date = request.form.get('show_date')
		show_time = request.form.get('show_time')
		price = request.form.get('price')

		db = current_app.get_db_connection()
		try:
			with db.cursor() as cursor:
				cursor.execute("INSERT INTO showtimes (movie_id, screen_id, show_date, show_time, price) VALUES (%s, %s, %s, %s, %s)",
							   (movie_id, screen_id, show_date, show_time, price))
				db.commit()
			flash('Showtime added.')
			return redirect(url_for('admin.admin_index'))
		finally:
			db.close()

	return render_template('admin_add_showtime.html', movies=movies, screens=screens)