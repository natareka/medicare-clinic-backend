# 🏥 MediCare Clinic — Full-Stack Appointment Booking System

A professional e-commerce style private clinic website with Django REST API backend, MySQL database, SMS (Twilio) and email (Gmail SMTP) notifications.

---

## 📸 Features

| Feature | Details |
|---|---|
| **Frontend** | HTML5, CSS3, Bootstrap 5, JavaScript |
| **Backend** | Python 3.9+, Django 4.2, Django REST Framework |
| **Database** | MySQL 8.0+ |
| **Email** | Gmail SMTP — confirmation, cancellation, reminders |
| **SMS** | Twilio — booking confirmation + 24hr reminders |
| **Admin** | Full Django Admin panel |
| **Mobile** | Fully responsive — all screen sizes |
| **Platform** | Windows 10/11, macOS 12+, Ubuntu 20.04+ |

---

## 📁 Project Structure

```
clinic_project/
├── frontend/
│   ├── index.html          ← Main homepage
│   ├── doctors.html        ← Doctors listing & search
│   ├── appointments.html   ← Manage bookings
│   ├── css/
│   │   └── style.css       ← Main stylesheet
│   └── js/
│       └── main.js         ← All JS logic + API calls
│
├── backend/
│   ├── manage.py
│   ├── requirements.txt
│   ├── .env.example        ← Copy to .env and fill in
│   ├── clinic_backend/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── celery.py       ← Background tasks
│   └── clinic/
│       ├── models.py       ← DB models
│       ├── views.py        ← API endpoints
│       ├── serializers.py
│       ├── urls.py
│       ├── admin.py
│       ├── notifications.py ← Email & SMS
│       ├── tasks.py        ← Celery background jobs
│       └── management/
│           └── commands/
│               └── seed_data.py ← Demo data loader
│
├── setup.py                ← Cross-platform setup wizard
├── start_windows.bat       ← Windows launcher
├── start_mac_linux.sh      ← macOS/Linux launcher
└── README.md
```

---

## ⚡ Quick Start

### Prerequisites

| Requirement | Download |
|---|---|
| Python 3.9+ | https://python.org/downloads |
| MySQL 8.0+ | https://dev.mysql.com/downloads |
| pip | Included with Python |

---

### Step 1 — Run Automated Setup

```bash
# Navigate to the project root
cd clinic_project

# Run the cross-platform setup wizard
python setup.py
```

This will:
- ✅ Create a Python virtual environment
- ✅ Install all dependencies
- ✅ Create the `.env` config file
- ✅ Create the MySQL database
- ✅ Apply all Django migrations
- ✅ Seed demo data (departments, doctors, etc.)
- ✅ Create admin user (admin / admin123)

---

### Step 2 — Configure Environment

Edit `backend/.env`:

```env
# Database
DB_NAME=medicare_clinic
DB_USER=root
DB_PASSWORD=YOUR_MYSQL_PASSWORD

# Email (Gmail)
EMAIL_HOST_USER=your@gmail.com
EMAIL_HOST_PASSWORD=your_app_password    # 16-char Google App Password

# SMS (Twilio)
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxx
TWILIO_PHONE_NUMBER=+1234567890
```

**Getting Gmail App Password:**
1. Enable 2-Step Verification on your Google account
2. Go to: https://myaccount.google.com/apppasswords
3. Create app password for "Mail"
4. Use the 16-character password in .env

**Getting Twilio Credentials:**
1. Sign up at https://twilio.com (free trial available)
2. Copy Account SID and Auth Token from dashboard
3. Get a phone number from Twilio console

---

### Step 3 — Start the Server

**Windows:**
```cmd
start_windows.bat
```

**macOS / Linux:**
```bash
./start_mac_linux.sh
```

**Or manually:**
```bash
# Activate virtual environment
# Windows:
backend\venv\Scripts\activate
# macOS/Linux:
source backend/venv/bin/activate

# Start server
cd backend
python manage.py runserver 0.0.0.0:8000
```

---

### Step 4 — Open the Website

1. **Frontend:** Open `frontend/index.html` in your browser
   - Or use VS Code Live Server for better experience
   - Or use Python: `python -m http.server 5500 --directory frontend`

2. **Admin Panel:** http://127.0.0.1:8000/admin
   - Username: `admin`
   - Password: `admin123`

3. **API Base URL:** http://127.0.0.1:8000/api/

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/departments/` | List all departments |
| GET | `/api/doctors/` | List doctors (filter: `?department=1`) |
| GET | `/api/doctors/{id}/slots/?date=YYYY-MM-DD` | Available time slots |
| POST | `/api/appointments/book/` | Book appointment |
| GET | `/api/appointments/{uuid}/` | Get appointment details |
| POST | `/api/appointments/{uuid}/cancel/` | Cancel appointment |
| GET | `/api/appointments/patient/?email=x` | Patient's appointments |
| GET | `/api/testimonials/` | Approved testimonials |
| POST | `/api/contact/` | Submit contact form |
| GET | `/api/stats/` | Clinic statistics |

---

## 📧 Booking Appointment — Request Body

```json
POST /api/appointments/book/
{
  "first_name": "John",
  "last_name": "Doe",
  "email": "john@example.com",
  "phone": "+6591234567",
  "gender": "M",
  "date_of_birth": "1990-05-15",
  "blood_group": "O+",
  "city": "Singapore",
  "doctor_id": 1,
  "department_id": 1,
  "appointment_date": "2026-05-20",
  "appointment_time": "10:00",
  "appointment_type": "CONSULTATION",
  "symptoms": "Chest pain and shortness of breath"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Appointment booked successfully!",
  "data": {
    "appointment_id": "uuid-here",
    "reference": "APT-ABC12345",
    "patient_name": "John Doe",
    "doctor": "Dr. Sarah Chen",
    "date": "May 20, 2026",
    "time": "10:00 AM",
    "email_sent": true,
    "sms_sent": true
  }
}
```

---

## 🔔 Notification System

### Email (Gmail SMTP)
- ✅ Booking confirmation with full HTML template
- ✅ Cancellation notification
- ✅ Contact form acknowledgement

### SMS (Twilio)
- ✅ Booking confirmation SMS
- ✅ 24-hour appointment reminder (via Celery)

### Running Background Tasks (Celery)
```bash
# Install Redis (required for Celery)
# Windows: https://github.com/microsoftarchive/redis/releases
# macOS: brew install redis
# Linux: sudo apt install redis-server

# Start Redis
redis-server

# Start Celery worker with beat scheduler (in backend folder)
celery -A clinic_backend worker --beat -l info
```

---

## 🎨 Frontend Pages

| Page | File | Description |
|---|---|---|
| Homepage | `index.html` | Hero, departments, doctors, stats, testimonials, contact |
| Doctors | `doctors.html` | Full doctor listing with search & filter |
| Appointments | `appointments.html` | Lookup & manage bookings |

---

## 🔐 Admin Panel Features

- Department management
- Doctor profiles with schedules
- Appointment dashboard with date filtering
- Patient records
- Testimonial approval queue
- Contact message inbox

---

## 🛠️ Troubleshooting

**MySQL connection error:**
- Verify MySQL is running: `mysql -u root -p`
- Check credentials in `backend/.env`
- Windows: Start MySQL from Services or XAMPP

**Email not sending:**
- Enable 2FA on Gmail account
- Use App Password (not your regular password)
- Check spam folder for test emails

**SMS not sending:**
- Verify Twilio credentials in `.env`
- Check phone number format: `+CountryCodeNumber`
- Twilio trial accounts can only send to verified numbers

**Module not found errors:**
- Activate virtual environment first
- Re-run: `pip install -r requirements.txt`

---

## 📄 License

MIT License — Free for personal and commercial use.

---

Built with ❤️ using Django, Bootstrap 5 & MySQL
