from flask import Blueprint, render_template, request, Response
from flask_login import login_required
from models import Student, Batch, Attendance, Subject
from datetime import date, timedelta
from extensions import db
import csv
import io

reports_bp = Blueprint('reports', __name__)


@reports_bp.route('/reports')
@login_required
def reports():
    batches = Batch.query.filter_by(is_active=True).order_by(Batch.name).all()

    batch_id = request.args.get('batch', type=int)
    subject_id = request.args.get('subject', type=int)
    start_date = request.args.get('start', '')
    end_date = request.args.get('end', '')
    report_type = request.args.get('type', 'summary')

    today = date.today()

    if not start_date:
        start_date = (today - timedelta(days=30)).isoformat()
    if not end_date:
        end_date = today.isoformat()

    try:
        start = date.fromisoformat(start_date)
        end = date.fromisoformat(end_date)
    except ValueError:
        start = today - timedelta(days=30)
        end = today

    report_data = []
    subjects = []

    if batch_id:
        subjects = Subject.query.filter_by(batch_id=batch_id).order_by(Subject.name).all()
        students = Student.query.filter_by(batch_id=batch_id, is_active=True)\
            .order_by(Student.roll_number).all()

        for student in students:
            q = Attendance.query.filter(
                Attendance.student_id == student.id,
                Attendance.date >= start,
                Attendance.date <= end
            )
            if subject_id:
                q = q.filter(Attendance.subject_id == subject_id)

            records = q.all()

            total = len(records)
            present = sum(1 for r in records if r.status == 'present')
            absent = sum(1 for r in records if r.status == 'absent')
            late = sum(1 for r in records if r.status == 'late')
            percentage = round((present / total * 100), 1) if total > 0 else 0

            report_data.append({
                'student': student,
                'total': total,
                'present': present,
                'absent': absent,
                'late': late,
                'percentage': percentage
            })

    return render_template('reports.html',
                           batches=batches,
                           subjects=subjects,
                           report_data=report_data,
                           selected_batch=batch_id,
                           selected_subject=subject_id,
                           start_date=start_date,
                           end_date=end_date,
                           report_type=report_type)


@reports_bp.route('/reports/export')
@login_required
def export_report():
    batch_id = request.args.get('batch', type=int)
    subject_id = request.args.get('subject', type=int)
    start_date = request.args.get('start', '')
    end_date = request.args.get('end', '')

    today = date.today()
    if not start_date:
        start_date = (today - timedelta(days=30)).isoformat()
    if not end_date:
        end_date = today.isoformat()

    try:
        start = date.fromisoformat(start_date)
        end = date.fromisoformat(end_date)
    except ValueError:
        start = today - timedelta(days=30)
        end = today

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Roll Number', 'Name', 'Batch', 'Subject', 'Total Days', 'Present', 'Absent', 'Late', 'Percentage'])

    query = Student.query.filter_by(is_active=True)
    if batch_id:
        query = query.filter_by(batch_id=batch_id)

    students = query.order_by(Student.roll_number).all()

    subj = Subject.query.get(subject_id) if subject_id else None
    subj_label = subj.name if subj else 'All Subjects'

    for student in students:
        q = Attendance.query.filter(
            Attendance.student_id == student.id,
            Attendance.date >= start,
            Attendance.date <= end
        )
        if subject_id:
            q = q.filter(Attendance.subject_id == subject_id)

        records = q.all()

        total = len(records)
        present = sum(1 for r in records if r.status == 'present')
        absent = sum(1 for r in records if r.status == 'absent')
        late = sum(1 for r in records if r.status == 'late')
        percentage = round((present / total * 100), 1) if total > 0 else 0

        writer.writerow([
            student.roll_number,
            student.full_name,
            student.batch.name if student.batch else '',
            subj_label,
            total,
            present,
            absent,
            late,
            f'{percentage}%'
        ])

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment;filename=attendance_report_{start}_{end}.csv'}
    )
