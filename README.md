# 🎓 Smart IT Faculty — Mutah University Portal

A full-stack academic management web portal for the Faculty of Information Technology at Mutah University, featuring dedicated dashboards for students and instructors, real-time database integration, an intelligent chatbot assistant, and an automated email notification system.

---

## 🖥️ Live Preview

| Service | URL |
|---|---|
| Main App Server | `http://localhost:5000` |
| Notification Service | `http://localhost:5001` |

---

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

---

## ⚙️ Setup & Run

### Prerequisites
- Python 3.10+
- MySQL 8.0+

```bash
pip install -r requirements.txt
```

### 1. Configure Database

Open `API/settings.py` and update:

```python
DB_HOST     = "localhost"
DB_USER     = "your_user"
DB_PASSWORD = "your_password"
DB_NAME     = "information_technology"
```

### 2. Run the Main Server

```bash
cd Project/Src
python -m API.server
```

### 3. Run the Notification Service *(Optional)*

```bash
cd Project/Src/Notifications
python main.py
```

---

## 🔐 Default Roles & Redirections

| Role | Login Method | Redirect |
|---|---|---|
| Student | Student ID | `/Information_Technology/HTML/Students/student_dashboard.html` |
| Instructor | Employee ID | `/Information_Technology/HTML/Instructors/instructor_dashboard.html` |

---

## 🎨 Design System

- **Direction** — RTL (Arabic-first layouts)
- **Palette** — Warm gold theme (`#b45309`, `#d97706`, `#fbbf24`, `#fdfbf5`)
- **Topbar** — Fixed dark-brown gradient with gold branding accents
- **Sidebar** — Clean white background with active gold indicator states
- **Animations** — `cardSlideIn`, `bannerFadeIn`, `iconPulse`, `topbarSlide`
- **Components** — Stat cards, progress bars, data tables, carousels, modals

---

## 📸 Pages Overview

| Page | Description |
|---|---|
| `student_login` / `instructor_login` | Secure authentication interfaces |
| `student_dashboard` | Personal stats, notifications, courses |
| `student_registration` | Course search, filtering & enrollment |
| `student_honorboard` | Top student academic rankings |
| `student_instructor` | Faculty members directory carousel |
| `instructor_dashboard` | Instructor statistics & section rosters |
| `instructor_student` | Attendance tracking & grade sheets |
| `instructor_notification` | Target panel to trigger email dispatches |

---

## 👨‍💻 Author

**Sofyan Tarawneh**  
Faculty of Information Technology — Mutah University  
📧 st333t682@gmail.com

---

## 📄 License

This project is developed exclusively for academic purposes at Mutah University.
ؤ
copyright@sofyantarawneh
