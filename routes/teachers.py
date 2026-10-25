from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from models import User
from extensions import db

teachers_bp = Blueprint('teachers', __name__)


@teachers_bp.route('/teachers')
@login_required
def teachers_list():
    if current_user.role != 'admin':
        flash('Only admins can manage teachers.', 'error')
        return redirect(url_for('dashboard.dashboard'))

    teachers = User.query.filter(User.role.in_(['teacher', 'admin']))\
        .order_by(User.full_name).all()

    return render_template('teachers.html', teachers=teachers)


@teachers_bp.route('/teachers/add', methods=['POST'])
@login_required
def add_teacher():
    if current_user.role != 'admin':
        flash('Only admins can add teachers.', 'error')
        return redirect(url_for('teachers.teachers_list'))

    full_name = request.form.get('full_name', '').strip()
    username = request.form.get('username', '').strip()
    email = request.form.get('email', '').strip()
    password = request.form.get('password', '')
    role = request.form.get('role', 'teacher')

    if not all([full_name, username, email, password]):
        flash('Please fill in all required fields.', 'error')
        return redirect(url_for('teachers.teachers_list'))

    if User.query.filter_by(username=username).first():
        flash('This username is already taken.', 'error')
        return redirect(url_for('teachers.teachers_list'))

    if User.query.filter_by(email=email).first():
        flash('This email is already registered.', 'error')
        return redirect(url_for('teachers.teachers_list'))

    user = User(
        full_name=full_name,
        username=username,
        email=email,
        password_hash=generate_password_hash(password),
        role=role if role in ('admin', 'teacher') else 'teacher'
    )
    db.session.add(user)
    db.session.commit()

    flash(f'{full_name} has been added as a {role}.', 'success')
    return redirect(url_for('teachers.teachers_list'))


@teachers_bp.route('/teachers/<int:user_id>/toggle', methods=['POST'])
@login_required
def toggle_teacher(user_id):
    if current_user.role != 'admin':
        flash('Only admins can manage teachers.', 'error')
        return redirect(url_for('teachers.teachers_list'))

    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('You cannot deactivate your own account.', 'error')
        return redirect(url_for('teachers.teachers_list'))

    user.is_active_user = not user.is_active_user
    db.session.commit()

    status = 'activated' if user.is_active_user else 'deactivated'
    flash(f'{user.full_name} has been {status}.', 'success')
    return redirect(url_for('teachers.teachers_list'))
