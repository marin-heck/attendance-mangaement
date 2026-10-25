import os
import secrets
from flask import Flask
from extensions import db, login_manager


def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static')

    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'attendtrack-secret-key-2026-production')
    if os.environ.get('VERCEL'):
        db_path = '/tmp/attendance.db'
    else:
        db_path = os.path.join(basedir, 'attendance.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'warning'

    from models import User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.students import students_bp
    from routes.attendance import attendance_bp
    from routes.batches import batches_bp
    from routes.reports import reports_bp
    from routes.teachers import teachers_bp
    from routes.settings import settings_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(students_bp)
    app.register_blueprint(attendance_bp)
    app.register_blueprint(batches_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(teachers_bp)
    app.register_blueprint(settings_bp)

    with app.app_context():
        db.create_all()
        seed_data()

    return app


def seed_data():
    from models import User, Batch, Student
    from werkzeug.security import generate_password_hash
    from datetime import date

    if User.query.first() is None:
        admin = User(
            username='admin',
            email='admin@school.edu',
            password_hash=generate_password_hash('admin123'),
            role='admin',
            full_name='Dr. Rajesh Kumar'
        )
        teacher1 = User(
            username='teacher1',
            email='teacher1@school.edu',
            password_hash=generate_password_hash('teacher123'),
            role='teacher',
            full_name='Prof. Anita Sharma'
        )
        teacher2 = User(
            username='teacher2',
            email='teacher2@school.edu',
            password_hash=generate_password_hash('teacher123'),
            role='teacher',
            full_name='Prof. Vikram Singh'
        )
        db.session.add_all([admin, teacher1, teacher2])
        db.session.commit()

        batches = [
            Batch(name='CSE-A 2024', department='Computer Science', year=2024, section='A'),
            Batch(name='CSE-B 2024', department='Computer Science', year=2024, section='B'),
            Batch(name='ECE-A 2024', department='Electronics', year=2024, section='A'),
            Batch(name='ME-A 2024', department='Mechanical', year=2024, section='A'),
        ]
        db.session.add_all(batches)
        db.session.commit()

        from models import Subject
        subjects = [
            Subject(name='Data Structures & Algorithms', code='CS301', batch_id=1),
            Subject(name='Database Management Systems', code='CS302', batch_id=1),
            Subject(name='Operating Systems', code='CS303', batch_id=1),
            Subject(name='Computer Networks', code='CS304', batch_id=1),
            Subject(name='Data Structures & Algorithms', code='CS301', batch_id=2),
            Subject(name='Database Management Systems', code='CS302', batch_id=2),
            Subject(name='Web Technologies', code='CS305', batch_id=2),
            Subject(name='Digital Signal Processing', code='EC301', batch_id=3),
            Subject(name='Microprocessors & Microcontrollers', code='EC302', batch_id=3),
            Subject(name='Thermodynamics', code='ME301', batch_id=4),
            Subject(name='Fluid Mechanics', code='ME302', batch_id=4),
        ]
        db.session.add_all(subjects)
        db.session.commit()

        students_data = [
            ('Aarav Patel', 'CS2024001', 'aarav@student.edu', 1),
            ('Diya Sharma', 'CS2024002', 'diya@student.edu', 1),
            ('Arjun Reddy', 'CS2024003', 'arjun@student.edu', 1),
            ('Priya Gupta', 'CS2024004', 'priya@student.edu', 1),
            ('Rohan Mehta', 'CS2024005', 'rohan@student.edu', 1),
            ('Ananya Iyer', 'CS2024006', 'ananya@student.edu', 1),
            ('Kabir Nair', 'CS2024007', 'kabir@student.edu', 1),
            ('Sneha Joshi', 'CS2024008', 'sneha@student.edu', 2),
            ('Vivaan Das', 'CS2024009', 'vivaan@student.edu', 2),
            ('Ishita Roy', 'CS2024010', 'ishita@student.edu', 2),
            ('Aditya Verma', 'CS2024011', 'aditya@student.edu', 2),
            ('Meera Kapoor', 'CS2024012', 'meera@student.edu', 2),
            ('Ravi Kumar', 'EC2024001', 'ravi@student.edu', 3),
            ('Pooja Sinha', 'EC2024002', 'pooja@student.edu', 3),
            ('Amit Tiwari', 'EC2024003', 'amit@student.edu', 3),
            ('Neha Agarwal', 'EC2024004', 'neha@student.edu', 3),
            ('Saurabh Mishra', 'ME2024001', 'saurabh@student.edu', 4),
            ('Kavita Rao', 'ME2024002', 'kavita@student.edu', 4),
            ('Deepak Chauhan', 'ME2024003', 'deepak@student.edu', 4),
            ('Ritika Pandey', 'ME2024004', 'ritika@student.edu', 4),
        ]

        for name, roll, email, batch_id in students_data:
            s = Student(
                full_name=name,
                roll_number=roll,
                email=email,
                batch_id=batch_id,
                phone='9' + ''.join([str(hash(name + str(i)) % 10) for i in range(9)]),
                date_of_birth=date(2003, (hash(name) % 12) + 1, (hash(name) % 28) + 1),
                address=f'{hash(name) % 500 + 1}, Sector {hash(name) % 50 + 1}, City'
            )
            db.session.add(s)

        db.session.commit()

    from models import Attendance
    from datetime import timedelta
    import random

    if Attendance.query.first() is None:
        today = date.today()
        students = Student.query.all()
        # Seed past 14 days excluding Sundays
        for day_offset in range(13, -1, -1):
            att_date = today - timedelta(days=day_offset)
            if att_date.weekday() == 6:  # Skip Sunday
                continue

            for idx, student in enumerate(students):
                # Make students with roll ending in 003 or 007 have lower attendance (<75%)
                if '003' in student.roll_number or '007' in student.roll_number:
                    status = 'absent' if (day_offset + idx) % 2 == 0 else ('late' if day_offset % 3 == 0 else 'present')
                elif (day_offset + idx) % 11 == 0:
                    status = 'absent'
                elif (day_offset + idx) % 7 == 0:
                    status = 'late'
                else:
                    status = 'present'

                remarks = 'Arrived 15 mins late' if status == 'late' else ('Medical leave' if status == 'absent' and day_offset % 4 == 0 else None)

                record = Attendance(
                    student_id=student.id,
                    date=att_date,
                    status=status,
                    marked_by=2,
                    remarks=remarks
                )
                db.session.add(record)

        db.session.commit()


app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
