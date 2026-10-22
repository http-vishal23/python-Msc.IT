"""
Simple Student Management App (Flask + SQLite CRUD)
===================================================
Unit 2: Web Application Development with Flask & Databases
Course: MSc (IT) — Hands-On Python

This is the simplest possible student details application using Flask and Flask-SQLAlchemy.
Every beginner can understand every line of this file!

CRUD Breakdown:
---------------
1. CREATE : Add a new student      ➔ db.session.add() + db.session.commit()
2. READ   : View all students      ➔ Student.query.all()
3. UPDATE : Toggle Active/Inactive ➔ student.is_active = not student.is_active + db.session.commit()
4. DELETE : Remove a student       ➔ db.session.delete() + db.session.commit()

How to Run:
-----------
1. Run this script:
   python app.py
2. Open your browser:
   http://127.0.0.1:5003
"""

import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'students.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# ---------------------------------------------------------------------------
# Database Model (Table)
# ---------------------------------------------------------------------------
class Student(db.Model):
    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key=True)         # Unique ID (1, 2, 3...)
    name = db.Column(db.String(100), nullable=False)     # Student Name
    roll_no = db.Column(db.String(50), nullable=False)   # Roll Number (e.g. IT-101)
    course = db.Column(db.String(100), nullable=False)   # Course (e.g. MSc IT)
    is_active = db.Column(db.Boolean, default=True)      # True = Active, False = Inactive

    def __repr__(self):
        return f"<Student #{self.id}: {self.name} ({self.roll_no})>"


def seed_sample_data():
    if Student.query.count() == 0:
        samples = [
            Student(name="Aarav Sharma", roll_no="IT-101", course="MSc IT", is_active=True),
            Student(name="Diya Patel", roll_no="IT-102", course="MSc IT", is_active=True),
            Student(name="Rohan Verma", roll_no="CS-201", course="MSc CS", is_active=False),
        ]
        db.session.add_all(samples)
        db.session.commit()


# ---------------------------------------------------------------------------
# Routes (CRUD Operations)
# ---------------------------------------------------------------------------

@app.route('/')
def index():
    # Query all students from SQLite, ordered by newest first
    students = Student.query.order_by(Student.id.desc()).all()
    total = len(students)
    active_count = sum(1 for s in students if s.is_active)
    return render_template('index.html', students=students, total=total, active_count=active_count)


@app.route('/add', methods=['POST'])
def add_student():
    name = request.form.get('name', '').strip()
    roll_no = request.form.get('roll_no', '').strip()
    course = request.form.get('course', '').strip()

    # Only add if user filled in the fields
    if name and roll_no and course:
        new_student = Student(name=name, roll_no=roll_no, course=course)
        db.session.add(new_student)     # Stage into session
        db.session.commit()             # Save to SQLite database!

    return redirect(url_for('index'))


# 3. UPDATE: Toggle student between Active and Inactive
@app.route('/toggle/<int:id>')
def toggle_student(id):
    # Find the student by ID
    student = db.session.get(Student, id)
    if student:
        student.is_active = not student.is_active   # Toggle True <-> False
        db.session.commit()                         # Save the change!

    return redirect(url_for('index'))


# 4. DELETE: Remove a student
@app.route('/delete/<int:id>')
def delete_student(id):
    # Find the student by ID
    student = db.session.get(Student, id)
    if student:
        db.session.delete(student)      # Mark for deletion
        db.session.commit()             # Save the change!

    return redirect(url_for('index'))


# ---------------------------------------------------------------------------
# App Entrypoint
# ---------------------------------------------------------------------------
if __name__ == '__main__':
    # Create tables and seed initial data if needed
    with app.app_context():
        db.create_all()
        seed_sample_data()

    print("=" * 60)
    print("  🎓 Simple Student App Running!")
    print("  📍 Open in Browser: http://127.0.0.1:5003")
    print("=" * 60)
    app.run(debug=True, port=5003)