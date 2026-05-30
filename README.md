# 🎓 Smart IT Faculty — Mutah University Portal

A full-stack academic management web portal for the Faculty of Information Technology at Mutah University, featuring dedicated dashboards for students and instructors, real-time database integration, an intelligent chatbot assistant, and an automated email notification system.


## ✨ Features

### 👨‍🎓 Student Portal
- **Secure Login** — Authentication via student ID & password
- **Dashboard** — Live stats: GPA, completed hours, registered courses
- **Course Registration** — Search, register, and drop courses with validations
- **Honor Board** — View top-performing students across the faculty
- **Instructor Directory** — Browse faculty members with a responsive carousel UI
- **AI Chatbot Assistant** — Interactive chatbot for student inquiries
- **Notifications** — Private logs for section changes (time, room, etc.)

### 👨‍🏫 Instructor Portal
- **Secure Login** — Authentication via employee ID & password
- **Dashboard** — Personal stats: courses taught, total students, pending expansion requests, section fill-rates
- **Student Management** — View enrolled students, record attendance & grades
- **Notification Sender** — Select section, update changes → automatically updates DB and emails all enrolled students instantly

### 📬 Notification System
Supports **4 change types**: `Time` · `Room` · `Instructor` · `Day`

**Workflow:** Updates `sections` table → fetches enrolled student emails → sends Gmail SMTP updates → saves logs to `private_notification`

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3, Flask, Flask-CORS |
| Database | MySQL 8 (`mysql-connector-python`) |
| Frontend | Vanilla HTML5, CSS3, JavaScript (ES2020) |
| AI Component | Intelligent Chatbot Integration |
| Email System | Gmail SMTP over SSL (`smtplib`) |
| Typography | Noto Kufi Arabic (Google Fonts) |
| Architecture | Flask Blueprints (modular, one per feature) |

---

## 📁 Project Structure

```
Project/Src/
│
├── API/                                    # Flask backend
│   ├── server.py                           # App factory & blueprint registration
│   ├── settings.py                         # DB configurations & paths
│   ├── faculties.py
│   └── Information_Technology/
│       └── Web/
│           ├── Students/
│           │   ├── student_login.py
│           │   ├── student_dashboard.py    # stats, courses, notifications
│           │   ├── student_registration.py
│           │   ├── student_honorboard.py
│           │   ├── student_instructor.py
│           │   └── student_sidebar.py
│           └── Instructors/
│               ├── instructor_login.py
│               ├── instructor_pages.py     # dashboard stats + sections
│               ├── instructor_student.py   # attendance & grades endpoints
│               ├── instructor_sidebar.py
│               ├── instructor_topbar.py
│               └── instructor_notification.py  # notify endpoint + email
│
├── Web/Information_Technology/             # Frontend assets
│   ├── HTML/
│   │   ├── Students/
│   │   └── Instructors/
│   ├── CSS/
│   │   ├── Students/
│   │   └── Instructors/
│   └── JS/
│       ├── Students/
│       └── Instructors/
│
└── Notifications/                          # Standalone notification service
    ├── main.py                             # Flask app (port 5001)
    ├── notifier.py
    ├── database.py
    ├── message.py
    ├── sender.py
    ├── settings.py
    └── templates/index.html
```

---

## 🗄️ Database Schema (MySQL)

| Table | Description |
|---|---|
| `students` | Student profiles, GPA, completed hours |
| `instructors` | Instructor profiles, specialization, rank |
| `courses` | Course catalog with credit hours |
| `sections` | Course sections (time, room, capacity, instructor) |
| `enrollments` | Student ↔ section registration mapping |
| `attendance` | Per-student absence count per section |
| `grades` | Participation, midterm, and final grades |
| `registration_requests` | Pending course expansion requests |
| `private_notification` | Email notification log per student |
| `honor_board` | Top student records |
| `student_records` | Historical grade records |



## 👨‍💻 Author

**Sofyan Tarawneh**  
Faculty of Information Technology — Mutah University  
📧 st333t682@gmail.com

---

## 📄 License

This project is developed exclusively for academic purposes at Mutah University.

copyright@sofyantarawneh
