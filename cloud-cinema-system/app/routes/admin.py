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

			cursor.execute("SELECT s.*, m.title, sc.screen_name FROM showtimes s JOIN movies m ON s.movie_id = m.movie_id JOIN screens sc ON s.screen_id = sc.screen_id ORDER BY s.show_date, s.show_time")
			showtimes = cursor.fetchall()
	finally:
		db.close()

	return render_template('admin_index.html', movies=movies, showtimes=showtimes)


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