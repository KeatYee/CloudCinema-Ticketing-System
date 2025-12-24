-- USE THE EXISTING DATABASE
USE moviedb;

-- =========================
-- USERS
-- =========================
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    pass VARCHAR(255) NOT NULL,
    role ENUM('customer', 'admin') DEFAULT 'customer',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- =========================
-- MOVIES
-- =========================
CREATE TABLE movies (
    movie_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    duration INT NOT NULL,              -- minutes
    rating VARCHAR(10),
    description TEXT,
    image_url VARCHAR(255)              -- poster / thumbnail image
);

-- =========================
-- SCREENS (HALLS)
-- =========================
CREATE TABLE screens (
    screen_id INT AUTO_INCREMENT PRIMARY KEY,
    screen_name VARCHAR(50) NOT NULL,
    total_seats INT NOT NULL
);

-- =========================
-- SEATS
-- =========================
CREATE TABLE seats (
    seat_id INT AUTO_INCREMENT PRIMARY KEY,
    screen_id INT NOT NULL,
    seat_row CHAR(1) NOT NULL,
    seat_number INT NOT NULL,

    FOREIGN KEY (screen_id) REFERENCES screens(screen_id),
    UNIQUE (screen_id, seat_row, seat_number)
);

-- =========================
-- SHOWTIMES
-- =========================
CREATE TABLE showtimes (
    showtime_id INT AUTO_INCREMENT PRIMARY KEY,
    movie_id INT NOT NULL,
    screen_id INT NOT NULL,
    show_date DATE NOT NULL,
    show_time TIME NOT NULL,
    price DECIMAL(6,2) NOT NULL,

    FOREIGN KEY (movie_id) REFERENCES movies(movie_id),
    FOREIGN KEY (screen_id) REFERENCES screens(screen_id)
);

-- =========================
-- BOOKINGS
-- =========================
CREATE TABLE bookings (
    booking_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    showtime_id INT NOT NULL,
    booking_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    cancelled TINYINT(1) DEFAULT 0,

    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (showtime_id) REFERENCES showtimes(showtime_id)
);

-- =========================
-- BOOKING SEATS
-- =========================
CREATE TABLE booking_seats (
    booking_seat_id INT AUTO_INCREMENT PRIMARY KEY,
    booking_id INT NOT NULL,
    seat_id INT NOT NULL,

    FOREIGN KEY (booking_id) REFERENCES bookings(booking_id),
    FOREIGN KEY (seat_id) REFERENCES seats(seat_id),
    UNIQUE (seat_id, booking_id)
);

INSERT INTO users (name, email, pass) VALUES ('John Doe', 'john@example.com', 'password');
-- To create an admin user with a hashed password, run the following Python snippet
-- from the project root (this will print an SQL statement to run in MySQL):
--
-- ```python
-- from werkzeug.security import generate_password_hash
-- pw = generate_password_hash('admin')
-- print(f"INSERT INTO users (name, email, pass, role) VALUES ('Admin User', 'admin@example.com', '{pw}', 'admin');")
-- ```
--
-- Copy the printed INSERT and run it in your MySQL client.

INSERT INTO movies (title, duration, rating, description, image_url) VALUES 
('Dune: Part Two', 166, 'PG-13', 'Paul Atreides unites with Chani and the Fremen while on a warpath of revenge.', 'dune2.jpg'),
('Oppenheimer', 180, 'R', 'The story of American scientist J. Robert Oppenheimer and his role in the development of the atomic bomb.', 'oppenheimer.jpg');

INSERT INTO screens (screen_name, total_seats) VALUES ('Grand Hall 1', 100);

INSERT INTO showtimes (movie_id, screen_id, show_date, show_time, price) VALUES 
(1, 1, CURDATE(), '14:30:00', 12.00),
(1, 1, CURDATE(), '18:00:00', 15.00),
(2, 1, CURDATE(), '20:00:00', 15.00);

-- =========================
-- SEATS INITIALIZATION
-- =========================
-- Create seat rows A-J with 10 seats each for screen_id = 1 (total 100 seats)
INSERT INTO seats (screen_id, seat_row, seat_number) VALUES
('1', 'A', 1), ('1', 'A', 2), ('1', 'A', 3), ('1', 'A', 4), ('1', 'A', 5), ('1', 'A', 6), ('1', 'A', 7), ('1', 'A', 8), ('1', 'A', 9), ('1', 'A', 10),
('1', 'B', 1), ('1', 'B', 2), ('1', 'B', 3), ('1', 'B', 4), ('1', 'B', 5), ('1', 'B', 6), ('1', 'B', 7), ('1', 'B', 8), ('1', 'B', 9), ('1', 'B', 10),
('1', 'C', 1), ('1', 'C', 2), ('1', 'C', 3), ('1', 'C', 4), ('1', 'C', 5), ('1', 'C', 6), ('1', 'C', 7), ('1', 'C', 8), ('1', 'C', 9), ('1', 'C', 10),
('1', 'D', 1), ('1', 'D', 2), ('1', 'D', 3), ('1', 'D', 4), ('1', 'D', 5), ('1', 'D', 6), ('1', 'D', 7), ('1', 'D', 8), ('1', 'D', 9), ('1', 'D', 10),
('1', 'E', 1), ('1', 'E', 2), ('1', 'E', 3), ('1', 'E', 4), ('1', 'E', 5), ('1', 'E', 6), ('1', 'E', 7), ('1', 'E', 8), ('1', 'E', 9), ('1', 'E', 10),
('1', 'F', 1), ('1', 'F', 2), ('1', 'F', 3), ('1', 'F', 4), ('1', 'F', 5), ('1', 'F', 6), ('1', 'F', 7), ('1', 'F', 8), ('1', 'F', 9), ('1', 'F', 10),
('1', 'G', 1), ('1', 'G', 2), ('1', 'G', 3), ('1', 'G', 4), ('1', 'G', 5), ('1', 'G', 6), ('1', 'G', 7), ('1', 'G', 8), ('1', 'G', 9), ('1', 'G', 10),
('1', 'H', 1), ('1', 'H', 2), ('1', 'H', 3), ('1', 'H', 4), ('1', 'H', 5), ('1', 'H', 6), ('1', 'H', 7), ('1', 'H', 8), ('1', 'H', 9), ('1', 'H', 10),
('1', 'I', 1), ('1', 'I', 2), ('1', 'I', 3), ('1', 'I', 4), ('1', 'I', 5), ('1', 'I', 6), ('1', 'I', 7), ('1', 'I', 8), ('1', 'I', 9), ('1', 'I', 10),
('1', 'J', 1), ('1', 'J', 2), ('1', 'J', 3), ('1', 'J', 4), ('1', 'J', 5), ('1', 'J', 6), ('1', 'J', 7), ('1', 'J', 8), ('1', 'J', 9), ('1', 'J', 10);