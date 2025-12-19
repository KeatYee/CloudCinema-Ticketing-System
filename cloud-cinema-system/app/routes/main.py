from flask import Blueprint, render_template, current_app, session

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    db = current_app.get_db_connection()
    try:
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM movies")
            movies = cursor.fetchall()
    finally:
        db.close()
    return render_template('index.html', movies=movies)

@main_bp.route('/movie/<int:movie_id>')
def movie_details(movie_id):
    db = current_app.get_db_connection()
    try:
        with db.cursor() as cursor:
            # 1. Fetch movie info
            cursor.execute("SELECT * FROM movies WHERE movie_id = %s", (movie_id,))
            movie = cursor.fetchone()

            # 2. Fetch showtimes for this movie
            cursor.execute("""
                SELECT s.*, sc.screen_name 
                FROM showtimes s 
                JOIN screens sc ON s.screen_id = sc.screen_id 
                WHERE s.movie_id = %s AND s.show_date >= CURDATE()
                ORDER BY s.show_date, s.show_time
            """, (movie_id,))
            showtimes = cursor.fetchall()
    finally:
        db.close()
    
    return render_template('movie_details.html', movie=movie, showtimes=showtimes)