from datetime import date, datetime
from flask_login import UserMixin
from extensions import db


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='teacher')
    full_name = db.Column(db.String(150), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active_user = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<User {self.username}>'


class Batch(db.Model):
    __tablename__ = 'batches'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    department = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    section = db.Column(db.String(10), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    students = db.relationship('Student', backref='batch', lazy=True)

    def __repr__(self):
        return f'<Batch {self.name}>'


class Student(db.Model):
    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(150), nullable=False)
    roll_number = db.Column(db.String(30), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(15))
    date_of_birth = db.Column(db.Date)
    address = db.Column(db.Text)
    batch_id = db.Column(db.Integer, db.ForeignKey('batches.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    attendances = db.relationship('Attendance', backref='student', lazy=True)

    @property
    def attendance_percentage(self):
        total = len(self.attendances)
        if total == 0:
            return 0
        present = sum(1 for a in self.attendances if a.status == 'present')
        return round((present / total) * 100, 1)

    def __repr__(self):
        return f'<Student {self.roll_number} - {self.full_name}>'


class Subject(db.Model):
    __tablename__ = 'subjects'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(20))
    batch_id = db.Column(db.Integer, db.ForeignKey('batches.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    batch = db.relationship('Batch', backref=db.backref('subjects', lazy=True, cascade='all, delete-orphan'))

    def __repr__(self):
        return f'<Subject {self.code} - {self.name}>'


class Attendance(db.Model):
    __tablename__ = 'attendance'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, default=date.today)
    status = db.Column(db.String(10), nullable=False, default='absent')
    marked_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=True)
    remarks = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    teacher = db.relationship('User', backref='marked_attendances')
    subject = db.relationship('Subject', backref='attendances')

    __table_args__ = (
        db.UniqueConstraint('student_id', 'date', 'subject_id', name='unique_student_date_subject'),
    )

    def __repr__(self):
        return f'<Attendance {self.student_id} - {self.date} - {self.status}>'
