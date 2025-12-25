**Scalable Cloud-Based Cinema Ticketing System**

Course: CSC3074 CLOUD COMPUTING

1. Installation Guide (How to Run Locally)
Follow these steps to set up the project on your local machine for development.

Prerequisites
Ensure you have the following installed:
- Python 3.12 or higher
- Git

**Step 1: Clone the Repository**
Open your terminal or command prompt and run:
git clone https://github.com/KeatYee/CloudCinema-Ticketing-System.git
cd CloudCinema-Ticketing-System/cloud-cinema-system


**Step 2: Set Up Virtual Environment**
Windows:
python -m venv venv
.\venv\Scripts\activate

Mac/Linux:
python3 -m venv venv
source venv/bin/activate


**Step 3: Install Dependencies**
Download the required Python libraries listed in requirements.txt.
pip install -r requirements.txt


**Step 4: Configure Environment Variables**
Create a file named .env inside the cloud-cinema-system/ folder. Paste the following configuration and replace the values with your actual AWS credentials.

SECRET_KEY=production_key_12345
# Database Connection
DB_HOST=movie-ticket-db.cu6z5duqk9n7.us-east-1.rds.amazonaws.com
DB_USER=admin
DB_PASSWORD=CloudComputingAssignment2025
DB_NAME=moviedb
# Storage
S3_BUCKET=csc3074-cloud-computing-assignment-22067110


**Step 5: Run the Application**
Start the Flask development server.

python app.py

Open your web browser and navigate to: http://127.0.0.1:5000



**2. Deployment Guide (AWS EC2)**
This application is designed to run on an Ubuntu EC2 instance using Gunicorn as the production WSGI server.

Connecting to the Server:
- Use your SSH key to access the remote server:ssh -i labsuser.pem ubuntu@<EC2_PUBLIC_IP>

Updating the Application:
To deploy the latest code changes from GitHub to the live server.
- Navigate to the project directory:cd CloudCinema-Ticketing-System/cloud-cinema-system
- Pull the latest changes:git pull
- Restart the background service:sudo systemctl restart cinema

Troubleshooting:
- Check Status:sudo systemctl status cinema
- Check Logs:sudo journalctl -u cinema.service -n 50 --no-pager



**3. Project Overview**
This application serves as a scalable cinema ticketing platform. It demonstrates cloud-native architecture principles by integrating compute, database, and storage services.

**Key Features:**
- Customer Portal: Register, browse movies, view details, and book tickets.
- Admin Dashboard: Manage movies, showtimes, and halls securely.
- Cloud Storage: Movie posters are stored in Amazon S3.
- Security: Passwords are hashed using Scrypt; Database is isolated in a Private Subnet.



**4. Database Setup**
The project uses a MySQL database hosted on AWS RDS. The schema and initial data are provided in the database.sql file.

To reset or initialize the database:
- Connect to the RDS instance via a MySQL client:mysql -h <DB_HOST> -u admin -p moviedb < database.sql
- Run the commands found in database.sql to create tables and seed initial data.



**5. Project Structure**
cloud-cinema-system/
├── app/
│   ├── routes/         # Python logic for different modules (auth, admin, etc.)
│   ├── templates/      # HTML pages
│   │   └── ...         # Public user & admin templates
│   └── static/         # CSS, JavaScript, and asset files
├── .env                # Environment configuration (Excluded from version control)
├── app.py              # Application entry point
├── requirements.txt    # List of Python dependencies
└── README.md           # Project documentation