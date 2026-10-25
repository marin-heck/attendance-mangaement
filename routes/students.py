from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import Student, Batch, Attendance
from datetime import date
from extensions import db

students_bp = Blueprint('students', __name__)


@students_bp.route('/students')
@login_required
def students_list():
    batch_id = request.args.get('batch', type=int)
    search = request.args.get('search', '').strip()
    status = request.args.get('status', 'active')

    query = Student.query

    if batch_id:
        query = query.filter_by(batch_id=batch_id)
    if search:
        query = query.filter(
            db.or_(
                Student.full_name.ilike(f'%{search}%'),
                Student.roll_number.ilike(f'%{search}%'),
                Student.email.ilike(f'%{search}%')
            )
        )
    if status == 'active':
        query = query.filter_by(is_active=True)
    elif status == 'inactive':
        query = query.filter_by(is_active=False)

    students = query.order_by(Student.roll_number).all()
    batches = Batch.query.filter_by(is_active=True).order_by(Batch.name).all()

    return render_template('students.html',
                           students=students,
                           batches=batches,
                           selected_batch=batch_id,
                           search=search,
                           status=status)


@students_bp.route('/students/add', methods=['POST'])
@login_required
def add_student():
    if current_user.role not in ('admin', 'teacher'):
        flash('You do not have permission to add students.', 'error')
        return redirect(url_for('students.students_list'))

    full_name = request.form.get('full_name', '').strip()
    roll_number = request.form.get('roll_number', '').strip()
    email = request.form.get('email', '').strip()
    phone = request.form.get('phone', '').strip()
    batch_id = request.form.get('batch_id', type=int)
    dob = request.form.get('date_of_birth', '').strip()
    address = request.form.get('address', '').strip()

    if not all([full_name, roll_number, email, batch_id]):
        flash('Please fill in all required fields.', 'error')
        return redirect(url_for('students.students_list'))

    if Student.query.filter_by(roll_number=roll_number).first():
        flash('A student with this roll number already exists.', 'error')
        return redirect(url_for('students.students_list'))

    if Student.query.filter_by(email=email).first():
        flash('A student with this email already exists.', 'error')
        return redirect(url_for('students.students_list'))

    student = Student(
        full_name=full_name,
        roll_number=roll_number,
        email=email,
        phone=phone,
        batch_id=batch_id,
        address=address
    )

    if dob:
        try:
            student.date_of_birth = date.fromisoformat(dob)
        except ValueError:
            pass

    db.session.add(student)
    db.session.commit()
    flash(f'Student {full_name} has been added successfully.', 'success')
    return redirect(url_for('students.students_list'))


@students_bp.route('/students/<int:student_id>')
@login_required
def student_profile(student_id):
    student = Student.query.get_or_404(student_id)
    attendances = Attendance.query.filter_by(student_id=student_id)\
        .order_by(Attendance.date.desc()).all()

    total = len(attendances)
    present = sum(1 for a in attendances if a.status == 'present')
    absent = sum(1 for a in attendances if a.status == 'absent')
    late = sum(1 for a in attendances if a.status == 'late')
    percentage = round((present / total * 100), 1) if total > 0 else 0

    # Monthly breakdown
    monthly = {}
    for a in attendances:
        key = a.date.strftime('%B %Y')
        if key not in monthly:
            monthly[key] = {'present': 0, 'absent': 0, 'late': 0, 'total': 0}
        monthly[key][a.status] = monthly[key].get(a.status, 0) + 1
        monthly[key]['total'] += 1

    batches = Batch.query.filter_by(is_active=True).order_by(Batch.name).all()

    return render_template('student_profile.html',
                           student=student,
                           attendances=attendances[:30],
                           total=total,
                           present=present,
                           absent=absent,
                           late=late,
                           percentage=percentage,
                           monthly=monthly,
                           batches=batches)


@students_bp.route('/students/<int:student_id>/edit', methods=['POST'])
@login_required
def edit_student(student_id):
    if current_user.role not in ('admin', 'teacher'):
        flash('You do not have permission to edit students.', 'error')
        return redirect(url_for('students.student_profile', student_id=student_id))

    student = Student.query.get_or_404(student_id)

    student.full_name = request.form.get('full_name', student.full_name).strip()
    student.email = request.form.get('email', student.email).strip()
    student.phone = request.form.get('phone', student.phone).strip()
    student.address = request.form.get('address', student.address).strip()
    student.batch_id = request.form.get('batch_id', student.batch_id, type=int)

    dob = request.form.get('date_of_birth', '').strip()
    if dob:
        try:
            student.date_of_birth = date.fromisoformat(dob)
        except ValueError:
            pass

    db.session.commit()
    flash(f'Student {student.full_name} updated successfully.', 'success')
    return redirect(url_for('students.student_profile', student_id=student_id))


@students_bp.route('/students/<int:student_id>/toggle', methods=['POST'])
@login_required
def toggle_student(student_id):
    if current_user.role != 'admin':
        flash('Only admins can activate/deactivate students.', 'error')
        return redirect(url_for('students.students_list'))

    student = Student.query.get_or_404(student_id)
    student.is_active = not student.is_active
    db.session.commit()

    status = 'activated' if student.is_active else 'deactivated'
    flash(f'Student {student.full_name} has been {status}.', 'success')
    return redirect(url_for('students.students_list'))
