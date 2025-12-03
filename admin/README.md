# Login & Registration System

A complete web application built with Python Flask backend and modern HTML/CSS/JavaScript frontend.

## 🌟 Features

### Backend (Flask)
- ✅ User Registration with validation
- ✅ Secure Login with password hashing
- ✅ Session management
- ✅ SQLite database
- ✅ Protected routes (login required)
- ✅ Flash messages for user feedback

### Frontend
- ✅ Modern green & white theme
- ✅ Responsive mobile design
- ✅ Real-time form validation
- ✅ Dynamic password strength checker
- ✅ Smooth animations and hover effects
- ✅ Card-based layout
- ✅ Google Fonts (Poppins)

### Validation Rules

**Registration:**
- Full Name: Required, only letters and spaces
- Gender: Required dropdown (Male/Female/Other)
- Email: Valid format + uniqueness check
- Mobile: Exactly 10 digits
- Address: Minimum 10 characters
- Password: 
  - Minimum 8 characters
  - At least one uppercase letter
  - At least one lowercase letter
  - At least one number
  - At least one special character
- Confirm Password: Must match password

**Login:**
- Email and password required
- Credentials verified against database

## 📁 Project Structure

```
project/
│
├── app2.py                 # Main Flask application
├── database.db             # SQLite database (auto-created)
├── README.md               # This file
│
├── templates/              # HTML templates
│   ├── register.html       # Registration page
│   ├── login.html          # Login page
│   └── home.html           # Dashboard (after login)
│
└── static/                 # Static files
    ├── style.css           # Main stylesheet
    ├── register.js         # Registration validation
    └── login.js            # Login enhancements
```

## 🚀 Installation & Setup

### Prerequisites
- Python 3.7 or higher
- pip (Python package manager)

### Step 1: Install Dependencies

```bash
pip install flask werkzeug
```

### Step 2: Run the Application

```bash
python app2.py
```

### Step 3: Access the Application

Open your browser and navigate to:
```
http://127.0.0.1:5000
```

## 📱 Pages

1. **Login Page** (`/login`)
   - Email and password fields
   - "Forgot Password?" link
   - "Register Now" link

2. **Registration Page** (`/register`)
   - Complete registration form
   - Real-time validation
   - Password strength indicator
   - "Login Now" link

3. **Dashboard** (`/home`)
   - Welcome message
   - User information
   - Stats cards
   - Logout button
   - Protected route (login required)

## 🎨 Theme

- **Primary Color:** Green (#4caf50)
- **Background:** Gradient purple
- **Cards:** White with rounded corners
- **Font:** Poppins (Google Fonts)
- **Design:** Modern, clean, minimalist

## 🔒 Security Features

- Password hashing using Werkzeug
- Session-based authentication
- SQL injection prevention (parameterized queries)
- CSRF protection ready
- Login required decorator for protected routes

## 💾 Database Schema

**users table:**
```sql
- id (INTEGER PRIMARY KEY)
- full_name (TEXT)
- gender (TEXT)
- email (TEXT UNIQUE)
- mobile (TEXT)
- address (TEXT)
- password (TEXT - hashed)
- created_at (TIMESTAMP)
```

## 🧪 Testing

1. Register a new account at `/register`
2. Login with your credentials at `/login`
3. Access the dashboard at `/home`
4. Try accessing `/home` without login (should redirect)
5. Test validation errors (wrong email format, weak password, etc.)

## 📝 Notes

- Database is automatically created on first run
- All passwords are hashed before storage
- Session expires on browser close
- Flash messages provide user feedback
- Fully responsive for mobile devices

## 🎓 College Project

This is a submission-ready college project demonstrating:
- Full-stack web development
- Database integration
- User authentication
- Form validation
- Responsive design
- Security best practices

## 📄 License

Free to use for educational purposes.

## 👨‍💻 Author

College Project - 2024
