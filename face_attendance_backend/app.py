from flask import Flask, request, jsonify
from config import Config
from models import db, User, Attendance
from utils import get_face_encoding_from_file, identify_user
from datetime import datetime

app = Flask(__name__)
app.config.from_object(Config)

# Initialize DB
db.init_app(app)

# Create tables before running (Run once)
with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return "Face Attendance Backend is Running!"

# --- 1. REGISTER USER ---
@app.route('/register', methods=['POST'])
def register():
    """
    Expects form-data:
    - name: text
    - email: text
    - image: file
    """
    if 'image' not in request.files:
        return jsonify({"error": "No image uploaded"}), 400
    
    name = request.form.get('name')
    email = request.form.get('email')
    file = request.files['image']

    # 1. Process Image
    encoding = get_face_encoding_from_file(file)
    if encoding is None:
        return jsonify({"error": "No face detected in the image. Please try again."}), 400

    # 2. Save to DB
    try:
        new_user = User(name=name, email=email, face_encoding=encoding)
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": f"User {name} registered successfully!", "id": new_user.id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- 2. MARK ATTENDANCE ---
@app.route('/mark_attendance', methods=['POST'])
def mark_attendance():
    """
    Expects form-data:
    - image: file (Live capture)
    """
    if 'image' not in request.files:
        return jsonify({"error": "No image uploaded"}), 400
    
    file = request.files['image']

    # 1. Get Live Encoding
    live_encoding = get_face_encoding_from_file(file)
    if live_encoding is None:
        return jsonify({"error": "No face detected"}), 400

    # 2. Fetch all users from DB to compare
    users = User.query.all()
    known_users_data = [(u.id, u.face_encoding) for u in users]

    # 3. Identify User
    user_id = identify_user(live_encoding, known_users_data)

    if user_id:
        # 4. Check if already attended TODAY
        today = datetime.utcnow().date()
        existing_record = Attendance.query.filter_by(user_id=user_id, date=today).first()

        if existing_record:
            return jsonify({
                "status": "success",
                "message": "Attendance already marked for today.",
                "user_id": user_id
            }), 200
        
        # 5. Mark Attendance
        new_attendance = Attendance(user_id=user_id)
        db.session.add(new_attendance)
        db.session.commit()
        
        # Fetch user name for response
        user = User.query.get(user_id)
        return jsonify({
            "status": "success",
            "message": f"Welcome {user.name}, attendance marked!",
            "user_id": user_id
        }), 200
    else:
        return jsonify({"status": "failed", "message": "User not recognized"}), 404

# --- 3. GET LOGS (Optional) ---
@app.route('/logs', methods=['GET'])
def get_logs():
    logs = Attendance.query.order_by(Attendance.timestamp.desc()).all()
    output = []
    for log in logs:
        output.append({
            "user": log.user.name,
            "time": log.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        })
    return jsonify(output)

if __name__ == '__main__':
    app.run(debug=True, port=5000)