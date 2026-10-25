# AttendTrack — Student Attendance Management System

A modern, institutional-grade Student Attendance Management System built with Python, Flask, SQLAlchemy, and a light blue responsive UI. Designed for universities, colleges, and schools to streamline daily attendance recording, cohort tracking, subject allocations, and compliance reporting.

---

## ✨ Features

- **Interactive Attendance Calendar**:
  - Full-featured calendar widget to navigate by date, weekday, month, and year.
  - Previous/Next day and quick jumps to *Today* and *Yesterday*.
  - Visual status dots on calendar days indicating previously recorded sessions.
- **Batch & Subject Management**:
  - Organize students into academic cohorts (Department, Year, Section).
  - Assign and dynamically create multiple subjects per batch on the fly (e.g. *Data Structures, DBMS, Operating Systems*).
  - Record and audit attendance per subject or general attendance.
- **Daily Attendance Marking**:
  - Segmented status selectors (*Present*, *Absent*, *Late*) with instant toggling.
  - Quick mass-action buttons (*All Present*, *All Absent*, *All Late*).
  - Individual student remarks and audit logs.
- **Student Directory & Profiles**:
  - Search and filter students by name, roll number, batch, and enrollment status.
  - Conic percentage charts, monthly attendance trends, and 30-day session logs.
  - Status indicators for students below the 75% attendance threshold.
- **Analytics & Exporting**:
  - Batch and subject-level summaries with customizable date ranges.
  - One-click CSV report export for institutional record-keeping.
- **Role-Based Access Control**:
  - **Administrator**: Full access to manage batches, subjects, faculty members, and student rosters.
  - **Teacher**: Access to mark attendance, review cohorts, and inspect student histories.

---

## 🛠️ Technology Stack

- **Backend**: Python 3.10+ / Flask 3.x
- **Database**: SQLite with Flask-SQLAlchemy ORM
- **Authentication**: Flask-Login with salted password hashing (PBKDF2-SHA256)
- **Frontend**: Semantic HTML5, Vanilla JavaScript, and Custom CSS (Light Blue theme)
- **Icons**: Inline SVG iconography (Feather / Lucide style)

---

## 🚀 Quick Start Guide

### 1. Clone the Repository
```bash
git clone <repository_url>
cd attendence
```

### 2. Set Up a Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Application
```bash
python app.py
```
The application will automatically initialize and seed the SQLite database on its first run. Open your browser and navigate to:
**`http://127.0.0.1:5000`**

---

## 🔑 Default Accounts (Seeded Demo)

| Role | Username | Password |
|---|---|---|
| **Administrator** | `admin` | `admin123` |
| **Teacher** | `teacher1` | `teacher123` |
| **Teacher** | `teacher2` | `teacher123` |

---

## 📁 Project Structure

```
├── app.py                 # Application factory and database seeder
├── extensions.py          # Shared extensions (SQLAlchemy, LoginManager)
├── models.py              # Database models (User, Batch, Student, Subject, Attendance)
├── requirements.txt       # Python dependencies
├── routes/
│   ├── auth.py            # Authentication & session routes
│   ├── dashboard.py       # Metrics, trends, and breakdown analytics
│   ├── attendance.py      # Daily attendance & quick-mark endpoints
│   ├── students.py        # Student records & profile views
│   ├── batches.py         # Batch cohorts & subject management
│   ├── reports.py         # Summary analytics & CSV export
│   ├── teachers.py        # Faculty and staff directory
│   └── settings.py        # Account credentials & preferences
├── static/
│   └── css/
│       └── style.css      # Light blue theme styles and tokens
└── templates/
    ├── base.html          # Global layout with navigation sidebar
    ├── login.html         # Login page
    ├── dashboard.html     # Analytics dashboard
    ├── attendance.html    # Interactive attendance sheet with calendar
    ├── students.html      # Students list & enrollment modal
    ├── student_profile.html # Detailed student profile & trend
    ├── batches.html       # Cohorts and subjects directory
    ├── reports.html       # Reports and CSV export
    ├── teachers.html      # Faculty management
    └── settings.html      # Account preferences
```

---

## 📄 License
This project is licensed under the MIT License.
