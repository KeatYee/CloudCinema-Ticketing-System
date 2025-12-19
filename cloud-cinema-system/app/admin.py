from werkzeug.security import generate_password_hash
pw = generate_password_hash('your_admin_password_here')
print("INSERT INTO users (name, email, pass, role) VALUES ('Admin User', 'admin@example.com', '{}', 'admin');".format(pw))