from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import Batch, Student, Subject
from extensions import db

batches_bp = Blueprint('batches', __name__)


@batches_bp.route('/batches')
@login_required
def batches_list():
    batches = Batch.query.order_by(Batch.year.desc(), Batch.name).all()

    batch_data = []
    for batch in batches:
        active_students = Student.query.filter_by(batch_id=batch.id, is_active=True).count()
        subjects = Subject.query.filter_by(batch_id=batch.id).order_by(Subject.name).all()
        batch_data.append({
            'batch': batch,
            'student_count': active_students,
            'subjects': subjects
        })

    return render_template('batches.html', batch_data=batch_data)


@batches_bp.route('/batches/add', methods=['POST'])
@login_required
def add_batch():
    if current_user.role != 'admin':
        flash('Only admins can create batches.', 'error')
        return redirect(url_for('batches.batches_list'))

    name = request.form.get('name', '').strip()
    department = request.form.get('department', '').strip()
    year = request.form.get('year', type=int)
    section = request.form.get('section', '').strip()

    if not all([name, department, year, section]):
        flash('Please fill in all required fields.', 'error')
        return redirect(url_for('batches.batches_list'))

    if Batch.query.filter_by(name=name).first():
        flash('A batch with this name already exists.', 'error')
        return redirect(url_for('batches.batches_list'))

    batch = Batch(name=name, department=department, year=year, section=section)
    db.session.add(batch)
    db.session.commit()

    flash(f'Batch "{name}" created successfully.', 'success')
    return redirect(url_for('batches.batches_list'))


@batches_bp.route('/batches/<int:batch_id>/edit', methods=['POST'])
@login_required
def edit_batch(batch_id):
    if current_user.role != 'admin':
        flash('Only admins can edit batches.', 'error')
        return redirect(url_for('batches.batches_list'))

    batch = Batch.query.get_or_404(batch_id)
    batch.name = request.form.get('name', batch.name).strip()
    batch.department = request.form.get('department', batch.department).strip()
    batch.year = request.form.get('year', batch.year, type=int)
    batch.section = request.form.get('section', batch.section).strip()

    db.session.commit()
    flash(f'Batch "{batch.name}" updated successfully.', 'success')
    return redirect(url_for('batches.batches_list'))


@batches_bp.route('/batches/<int:batch_id>/toggle', methods=['POST'])
@login_required
def toggle_batch(batch_id):
    if current_user.role != 'admin':
        flash('Only admins can activate/deactivate batches.', 'error')
        return redirect(url_for('batches.batches_list'))

    batch = Batch.query.get_or_404(batch_id)
    batch.is_active = not batch.is_active
    db.session.commit()

    status = 'activated' if batch.is_active else 'deactivated'
    flash(f'Batch "{batch.name}" has been {status}.', 'success')
    return redirect(url_for('batches.batches_list'))


@batches_bp.route('/batches/<int:batch_id>/subjects/add', methods=['POST'])
@login_required
def add_subject(batch_id):
    if current_user.role not in ('admin', 'teacher'):
        flash('You do not have permission to add subjects.', 'error')
        return redirect(url_for('batches.batches_list'))

    batch = Batch.query.get_or_404(batch_id)
    name = request.form.get('name', '').strip()
    code = request.form.get('code', '').strip().upper()

    if not name:
        flash('Subject name is required.', 'error')
    else:
        subject = Subject(name=name, code=code, batch_id=batch.id)
        db.session.add(subject)
        db.session.commit()
        flash(f'Subject "{name}" added to {batch.name}.', 'success')

    next_url = request.form.get('next_url')
    if next_url:
        return redirect(next_url)
    return redirect(url_for('batches.batches_list'))


@batches_bp.route('/api/batches/<int:batch_id>/subjects', methods=['GET'])
@login_required
def api_get_subjects(batch_id):
    subjects = Subject.query.filter_by(batch_id=batch_id).order_by(Subject.name).all()
    return jsonify({
        'subjects': [{
            'id': s.id,
            'name': s.name,
            'code': s.code or '',
            'display': f'{s.code} - {s.name}' if s.code else s.name
        } for s in subjects]
    })


@batches_bp.route('/api/batches/<int:batch_id>/subjects/add', methods=['POST'])
@login_required
def api_add_subject(batch_id):
    if current_user.role not in ('admin', 'teacher'):
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403

    batch = Batch.query.get_or_404(batch_id)
    data = request.get_json(silent=True) or request.form
    name = (data.get('name') or '').strip()
    code = (data.get('code') or '').strip().upper()

    if not name:
        return jsonify({'success': False, 'error': 'Subject name is required'}), 400

    subject = Subject(name=name, code=code, batch_id=batch.id)
    db.session.add(subject)
    db.session.commit()

    return jsonify({
        'success': True,
        'subject': {
            'id': subject.id,
            'name': subject.name,
            'code': subject.code or '',
            'display': f'{subject.code} - {subject.name}' if subject.code else subject.name
        }
    })


@batches_bp.route('/subjects/<int:subject_id>/delete', methods=['POST'])
@login_required
def delete_subject(subject_id):
    if current_user.role != 'admin':
        flash('Only admins can remove subjects.', 'error')
        return redirect(url_for('batches.batches_list'))

    subject = Subject.query.get_or_404(subject_id)
    batch_id = subject.batch_id
    db.session.delete(subject)
    db.session.commit()
    flash(f'Subject "{subject.name}" removed.', 'success')
    return redirect(url_for('batches.batches_list'))
