from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import User
from extensions import db

settings_bp = Blueprint('settings', __name__)


@settings_bp.route('/settings')
@login_required
def settings():
    return render_template('settings.html')


@settings_bp.route('/settings/profile', methods=['POST'])
@login_required
def update_profile():
    full_name = request.form.get('full_name', '').strip()
    email = request.form.get('email', '').strip()

    if full_name:
        current_user.full_name = full_name
    if email:
        existing = User.query.filter(User.email == email, User.id != current_user.id).first()
        if existing:
            flash('This email is already in use by another account.', 'error')
            return redirect(url_for('settings.settings'))
        current_user.email = email

    db.session.commit()
    flash('Profile updated successfully.', 'success')
    return redirect(url_for('settings.settings'))


@settings_bp.route('/settings/password', methods=['POST'])
@login_required
def change_password():
    current_password = request.form.get('current_password', '')
    new_password = request.form.get('new_password', '')
    confirm_password = request.form.get('confirm_password', '')

    if not check_password_hash(current_user.password_hash, current_password):
        flash('Current password is incorrect.', 'error')
        return redirect(url_for('settings.settings'))

    if len(new_password) < 6:
        flash('New password must be at least 6 characters.', 'error')
        return redirect(url_for('settings.settings'))

    if new_password != confirm_password:
        flash('New passwords do not match.', 'error')
        return redirect(url_for('settings.settings'))

    current_user.password_hash = generate_password_hash(new_password)
    db.session.commit()
    flash('Password changed successfully.', 'success')
    return redirect(url_for('settings.settings'))
