from flask import Flask, request, jsonify
from config import Config
from models import db, User, Attendance
from utils import get_face_encoding_from_file, identify_user
from datetime import datetime

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return "Face Attendance Backend is Running!"

@app.route('/register', methods=['POST'])
def register():
    if 'image' not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    name = request.form.get('name')
    email = request.form.get('email')
    file = request.files['image']

    encoding = get_face_encoding_from_file(file)
    if encoding is None:
        return jsonify({"error": "No face detected."}), 400

    try:
        new_user = User(name=name, email=email, face_encoding=encoding)
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": "User registered!", "id": new_user.id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/mark_attendance', methods=['POST'])
def mark_attendance():
    if 'image' not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    file = request.files['image']
    live_encoding = get_face_encoding_from_file(file)

    if live_encoding is None:
        return jsonify({"error": "No face detected"}), 400

    users = User.query.all()
    known_users_data = [(u.id, u.face_encoding) for u in users]
    user_id = identify_user(live_encoding, known_users_data)

    if user_id:
        today = datetime.utcnow().date()
        existing = Attendance.query.filter_by(user_id=user_id, date=today).first()
        if existing:
            return jsonify({"message": "Already marked today", "user_id": user_id}), 200

        new_att = Attendance(user_id=user_id)
        db.session.add(new_att)
        db.session.commit()
        return jsonify({"message": "Attendance marked!", "user_id": user_id}), 200
    else:
        return jsonify({"message": "User not recognized"}), 404

if __name__ == '__main__':
    app.run(debug=True, port=5000)