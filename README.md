**Scalable Cloud-Based Cinema Ticketing System**
Course: CSC3074 CLOUD COMPUTING

**Project Overview**
- App Type: Web Application (Flask/Python)
- Database: Amazon RDS (MySQL)
- Storage: Amazon S3 (Object Storage)
- Infrastructure: AWS VPC, EC2, Application Load Balancer (ALB), Auto Scaling Group (ASG)


**Key Features:**
- Customer Portal: Register, browse movies, view details, and book tickets.
- Admin Dashboard: Manage movies, showtimes, and halls securely.
- Cloud Storage: Movie posters are stored in Amazon S3.
- Security: Passwords are hashed using Scrypt; Database is isolated in a Private Subnet.
  

**How to Run** (Cloud Production)
- Here are the details to access and evaluate the project:
Access URL: http://movie-app-alb-845460910.us-east-1.elb.amazonaws.com/
Git Repository: https://github.com/KeatYee/CloudCinema-Ticketing-System.git
For App admin login:
email: admin@example.com
password: admin123


**Project Structure**
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
