from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import Student, Batch, Attendance, Subject
from datetime import date, datetime
from extensions import db

attendance_bp = Blueprint('attendance', __name__)


@attendance_bp.route('/attendance')
@login_required
def daily_attendance():
    selected_date = request.args.get('date', date.today().isoformat())
    batch_id = request.args.get('batch', type=int)
    subject_id = request.args.get('subject', type=int)

    try:
        att_date = date.fromisoformat(selected_date)
    except ValueError:
        att_date = date.today()

    batches = Batch.query.filter_by(is_active=True).order_by(Batch.name).all()

    students = []
    attendance_map = {}
    subjects = []
    recorded_dates = []

    if batch_id:
        subjects = Subject.query.filter_by(batch_id=batch_id).order_by(Subject.name).all()
        students = Student.query.filter_by(batch_id=batch_id, is_active=True)\
            .order_by(Student.roll_number).all()

        student_ids = [s.id for s in students]

        # Query existing attendance for selected date
        query = Attendance.query.filter(
            Attendance.student_id.in_(student_ids),
            Attendance.date == att_date
        )
        if subject_id:
            query = query.filter(Attendance.subject_id == subject_id)
        else:
            query = query.filter(Attendance.subject_id.is_(None))

        existing = query.all()
        attendance_map = {a.student_id: a for a in existing}

        # Query dates that have attendance recorded for this batch
        date_query = db.session.query(Attendance.date).filter(
            Attendance.student_id.in_(student_ids)
        )
        if subject_id:
            date_query = date_query.filter(Attendance.subject_id == subject_id)
        recorded_dates = [d[0].isoformat() for d in date_query.distinct().all()]

    return render_template('attendance.html',
                           students=students,
                           batches=batches,
                           subjects=subjects,
                           selected_date=att_date,
                           selected_batch=batch_id,
                           selected_subject=subject_id,
                           attendance_map=attendance_map,
                           recorded_dates=recorded_dates)


@attendance_bp.route('/attendance/mark', methods=['POST'])
@login_required
def mark_attendance():
    if current_user.role not in ('admin', 'teacher'):
        flash('You do not have permission to mark attendance.', 'error')
        return redirect(url_for('attendance.daily_attendance'))

    att_date_str = request.form.get('date', date.today().isoformat())
    batch_id = request.form.get('batch_id', type=int)
    subject_id = request.form.get('subject_id', type=int)
    if not subject_id or subject_id == 0:
        subject_id = None

    try:
        att_date = date.fromisoformat(att_date_str)
    except ValueError:
        att_date = date.today()

    students = Student.query.filter_by(batch_id=batch_id, is_active=True).all()

    marked_count = 0
    for student in students:
        status = request.form.get(f'status_{student.id}', 'absent')
        remarks = request.form.get(f'remarks_{student.id}', '').strip()

        q = Attendance.query.filter_by(
            student_id=student.id,
            date=att_date
        )
        if subject_id:
            q = q.filter_by(subject_id=subject_id)
        else:
            q = q.filter(Attendance.subject_id.is_(None))

        existing = q.first()

        if existing:
            existing.status = status
            existing.remarks = remarks
            existing.marked_by = current_user.id
            existing.subject_id = subject_id
        else:
            record = Attendance(
                student_id=student.id,
                date=att_date,
                status=status,
                remarks=remarks,
                marked_by=current_user.id,
                subject_id=subject_id
            )
            db.session.add(record)

        marked_count += 1

    db.session.commit()

    batch = Batch.query.get(batch_id)
    subj = Subject.query.get(subject_id) if subject_id else None
    subj_name = f" ({subj.name})" if subj else ""
    flash(f'Attendance recorded for {marked_count} students in {batch.name}{subj_name} on {att_date.strftime("%d %b %Y")}.', 'success')
    return redirect(url_for('attendance.daily_attendance', date=att_date_str, batch=batch_id, subject=subject_id or ''))


@attendance_bp.route('/attendance/quick-mark', methods=['POST'])
@login_required
def quick_mark():
    """Mark all students in a batch as present/absent at once."""
    if current_user.role not in ('admin', 'teacher'):
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json(silent=True) or request.form
    batch_id = data.get('batch_id')
    subject_id = data.get('subject_id')
    if subject_id:
        try:
            subject_id = int(subject_id)
        except (ValueError, TypeError):
            subject_id = None
    else:
        subject_id = None

    att_date_str = data.get('date', date.today().isoformat())
    status = data.get('status', 'present')

    try:
        att_date = date.fromisoformat(att_date_str)
    except ValueError:
        att_date = date.today()

    students = Student.query.filter_by(batch_id=batch_id, is_active=True).all()

    for student in students:
        q = Attendance.query.filter_by(
            student_id=student.id,
            date=att_date
        )
        if subject_id:
            q = q.filter_by(subject_id=subject_id)
        else:
            q = q.filter(Attendance.subject_id.is_(None))

        existing = q.first()

        if existing:
            existing.status = status
            existing.marked_by = current_user.id
            existing.subject_id = subject_id
        else:
            record = Attendance(
                student_id=student.id,
                date=att_date,
                status=status,
                marked_by=current_user.id,
                subject_id=subject_id
            )
            db.session.add(record)

    db.session.commit()
    return jsonify({'success': True, 'count': len(students)})
