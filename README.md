================================================================================
🎓 SMART IT FACULTY — MUTAH UNIVERSITY PORTAL
================================================================================

A full-stack academic management web portal for the Faculty of Information 
Technology at Mutah University, providing dedicated dashboards for students 
and instructors with real-time database integration, an intelligent chatbot 
assistant, and an automated email notification system.

--------------------------------------------------------------------------------
🖥️  LIVE PREVIEW
--------------------------------------------------------------------------------

* Main App Server       : Served via Flask on http://localhost:5000
* Notification Service  : Runs independently on http://localhost:5001

--------------------------------------------------------------------------------
✨ FEATURES
--------------------------------------------------------------------------------

[👨‍🎓 Student Portal]
* Secure Login         : Authentication via student ID & password.
* Dashboard            : Live stats (GPA, completed hours, registered courses).
* Course Registration  : Search, register, and drop courses with validations.
* Honor Board          : View top-performing students across the faculty.
* Instructor Directory : Browse faculty members with a responsive carousel UI.
* AI Chatbot Assistant : Interactive chatbot helper for student inquiries.
* Notifications        : Private logs for section changes (time, room, etc.).

[👨‍🏫 Instructor Portal]
* Secure Login         : Authentication via employee ID & password.
* Dashboard            : Personal stats (courses taught, total students, 
                         pending expansion requests, section fill-rates).
* Student Management   : View enrolled students, record attendance & grades.
* Notification Sender  : Select section, update changes -> automatically 
                         updates DB and emails all enrolled students instantly.

[📬 Notification System]
* Supports 4 change types: Time · Room · Instructor · Day.
* Workflow: Updates 'sections' table -> fetches enrolled student emails -> 
            sends Gmail SMTP updates -> saves logs to 'private_notification'.

--------------------------------------------------------------------------------
🛠️  TECH STACK
--------------------------------------------------------------------------------

* Backend      : Python 3, Flask, Flask-CORS
* Database     : MySQL 8 (using mysql-connector-python)
* Frontend     : Vanilla HTML5, CSS3, JavaScript (ES2020)
* AI Component : Intelligent Chatbot Integration
* Email System : Gmail SMTP over SSL (smtplib)
* Typography   : Noto Kufi Arabic (Google Fonts)
* Architecture : Flask Blueprints (one modular blueprint per page/feature)

--------------------------------------------------------------------------------
📁 PROJECT STRUCTURE
--------------------------------------------------------------------------------

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
│               └── instructor_notification.py # notify endpoint + email
│
├── Web/Information_Technology/            # Frontend assets
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

--------------------------------------------------------------------------------
🗄️  DATABASE SCHEMA (MySQL)
--------------------------------------------------------------------------------

* students              - student profiles, GPA, completed hours
* instructors           - instructor profiles, specialization, rank
* courses               - course catalog with credit hours
* sections              - course sections (time, room, capacity, instructor)
* enrollments           - student <-> section registration mapping
* attendance            - per-student absence count per section
* grades                - participation, midterm, and final grades
* registration_requests - pending course expansion requests
* private_notification  - email notification log per student
* honor_board           - top student records
* student_records       - historical grade records

--------------------------------------------------------------------------------
⚙️  SETUP & RUN
--------------------------------------------------------------------------------

[Prerequisites]
  Python 3.10+ , MySQL 8.0+
  Command: pip install -r requirements.txt

[1. Configure Database]
  Open and edit API/settings.py:
  DB_HOST     = "localhost"
  DB_USER     = "your_user"
  DB_PASSWORD = "your_password"
  DB_NAME     = "information_technology"

[2. Run the Main Server]
  $ cd Project/Src
  $ python -m API.server

[3. Run the Notification Service] (Optional)
  $ cd Project/Src/Notifications
  $ python main.py

--------------------------------------------------------------------------------
🔐 DEFAULT ROLES & REDIRECTIONS
--------------------------------------------------------------------------------

* Student    (Login: Student ID)
  -> /Information_Technology/HTML/Students/student_dashboard.html

* Instructor (Login: Employee ID)
  -> /Information_Technology/HTML/Instructors/instructor_dashboard.html

--------------------------------------------------------------------------------
🎨 DESIGN SYSTEM
--------------------------------------------------------------------------------

* Direction  : RTL (Arabic-first layouts)
* Palette    : Warm gold theme (#b45309, #d97706, #fbbf24, #fdfbf5)
* Topbar     : Fixed dark-brown gradient with gold branding accents
* Sidebar    : Clean white background with active gold indicator states
* Animations : cardSlideIn, bannerFadeIn, iconPulse, topbarSlide
* Components : Stat cards, progress bars, data tables, carousels, modals

--------------------------------------------------------------------------------
📸 PAGES OVERVIEW
--------------------------------------------------------------------------------

* student_login / instructor_login : Secure authentication interfaces
* student_dashboard               : Personal stats, notifications, courses
* student_registration            : Course search, filtering, & enrollment
* student_honorboard              - Top student academic rankings
* student_instructor              - Faculty members directory carousel
* instructor_dashboard            - Instructor statistics & section rosters
* instructor_student              - Attendance tracking & grade sheets
* instructor_notification         - Target panel to trigger email dispatches

--------------------------------------------------------------------------------
👨‍💻 AUTHOR
--------------------------------------------------------------------------------

Sofyan Tarawneh
Faculty of Information Technology — Mutah University
📧 st333t682@gmail.com

--------------------------------------------------------------------------------
📄 LICENSE
--------------------------------------------------------------------------------

This project is developed exclusively for academic purposes at Mutah University.
================================================================================
