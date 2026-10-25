from flask import Blueprint, render_template
from flask_login import login_required, current_user
from models import Student, Batch, Attendance, User
from datetime import date, timedelta
from sqlalchemy import func
from extensions import db

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    today = date.today()
    total_students = Student.query.filter_by(is_active=True).count()
    total_batches = Batch.query.filter_by(is_active=True).count()
    total_teachers = User.query.filter_by(role='teacher', is_active_user=True).count()

    # Today's attendance stats
    today_records = Attendance.query.filter_by(date=today).all()
    today_present = sum(1 for a in today_records if a.status == 'present')
    today_absent = sum(1 for a in today_records if a.status == 'absent')
    today_late = sum(1 for a in today_records if a.status == 'late')
    today_total = len(today_records)
    today_rate = round((today_present / today_total * 100), 1) if today_total > 0 else 0

    # Weekly attendance trend (last 7 days)
    weekly_data = []
    for i in range(6, -1, -1):
        d = today - timedelta(days=i)
        day_records = Attendance.query.filter_by(date=d).all()
        day_total = len(day_records)
        day_present = sum(1 for a in day_records if a.status in ('present', 'late'))
        rate = round((day_present / day_total * 100), 1) if day_total > 0 else 0
        weekly_data.append({
            'date': d.strftime('%a'),
            'full_date': d.strftime('%d %b'),
            'rate': rate,
            'present': day_present,
            'total': day_total
        })

    # Per-batch attendance for today
    batch_stats = []
    batches = Batch.query.filter_by(is_active=True).all()
    for batch in batches:
        student_ids = [s.id for s in batch.students if s.is_active]
        if student_ids:
            batch_today = Attendance.query.filter(
                Attendance.student_id.in_(student_ids),
                Attendance.date == today
            ).all()
            present = sum(1 for a in batch_today if a.status in ('present', 'late'))
            total = len(student_ids)
            rate = round((present / total * 100), 1) if total > 0 else 0
            batch_stats.append({
                'name': batch.name,
                'department': batch.department,
                'present': present,
                'total': total,
                'rate': rate
            })

    # Students with low attendance (below 75%)
    low_attendance_students = []
    all_students = Student.query.filter_by(is_active=True).all()
    for student in all_students:
        pct = student.attendance_percentage
        if pct < 75 and len(student.attendances) > 0:
            low_attendance_students.append({
                'name': student.full_name,
                'roll': student.roll_number,
                'batch': student.batch.name,
                'percentage': pct
            })
    low_attendance_students.sort(key=lambda x: x['percentage'])

    # Recent attendance activity
    recent_records = Attendance.query.order_by(Attendance.created_at.desc()).limit(10).all()
    recent_activity = []
    for rec in recent_records:
        recent_activity.append({
            'student_name': rec.student.full_name,
            'roll': rec.student.roll_number,
            'status': rec.status,
            'date': rec.date.strftime('%d %b %Y'),
            'batch': rec.student.batch.name
        })

    return render_template('dashboard.html',
                           total_students=total_students,
                           total_batches=total_batches,
                           total_teachers=total_teachers,
                           today_present=today_present,
                           today_absent=today_absent,
                           today_late=today_late,
                           today_rate=today_rate,
                           today_total=today_total,
                           weekly_data=weekly_data,
                           batch_stats=batch_stats,
                           low_attendance_students=low_attendance_students[:8],
                           recent_activity=recent_activity)
