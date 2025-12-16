import sqlite3
import os
import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify, session, render_template
from werkzeug.security import generate_password_hash, check_password_hash
from twilio.rest import Client
load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)
DB_NAME = "hospital.db"

# ================= CONFIGURATION =================
TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

# ================= DATABASE =================

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Appointments Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_name TEXT,
            phone_number TEXT,
            email TEXT,
            symptoms TEXT,
            appointment_time TEXT,
            status TEXT DEFAULT 'Scheduled'
        )
    ''')
    
    # Doctors Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS doctors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            doctor_id TEXT UNIQUE,
            password_hash TEXT,
            name TEXT,
            specialty TEXT
        )
    ''')
    conn.commit()
    conn.close()

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def send_sms(to, body):
    """
    Sends an SMS using Twilio.
    Prints to console for verification if credentials are mock/invalid.
    """
    print(f"\n[SMS LOG] To: {to} | Message: {body}\n")
    
    # Check if credentials are placeholders
    if "YOUR_SID" in TWILIO_SID or not TWILIO_SID:
        return True 

    try:
        client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)
        client.messages.create(
            body=body,
            from_=TWILIO_PHONE_NUMBER,
            to=to
        )
        return True
    except Exception as e:
        print(f"[Twilio Error]: {e}")
        return False

# ================= ROUTES =================

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/patient')
def patient():
    return render_template('patient.html')

@app.route('/doctor')
def doctor():
    return render_template('doctor.html')

# ================= API =================

@app.route('/api/appointments', methods=['POST'])
def create_appointment():
    data = request.json
    conn = get_db()
    conn.execute(
        'INSERT INTO appointments (patient_name, phone_number, email, symptoms, appointment_time) VALUES (?, ?, ?, ?, ?)',
        (data['name'], data['phone'], data.get('email', ''), data['symptoms'], data['time'])
    )
    conn.commit()
    conn.close()
    
    # 1. Automatic Booking Confirmation SMS to Patient
    formatted_time = data['time'].replace('T', ' at ')
    msg = f"Hello {data['name']}, your appointment with MediConnect is confirmed for {formatted_time}. We look forward to seeing you."
    send_sms(data['phone'], msg)
    
    return jsonify(success=True)

@app.route('/api/appointments', methods=['GET'])
def get_appointments():
    if 'doctor_id' not in session:
        return jsonify(error="Unauthorized"), 401
    conn = get_db()
    rows = conn.execute('SELECT * FROM appointments ORDER BY appointment_time ASC').fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route('/api/doctor/signup', methods=['POST'])
def doctor_signup():
    data = request.json
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO doctors (doctor_id, password_hash, name, specialty) VALUES (?, ?, ?, ?)',
            (data['doctor_id'], generate_password_hash(data['password']), data['name'], data['specialty'])
        )
        conn.commit()
        # Capture the auto-incremented ID (Serial Number)
        new_serial_number = cursor.lastrowid 
        conn.close()
        
        return jsonify(success=True, serial_number=new_serial_number)
    except Exception as e:
        return jsonify(success=False, error="User ID already exists"), 400

@app.route('/api/doctor/login', methods=['POST'])
def doctor_login():
    data = request.json
    conn = get_db()
    d = conn.execute(
        'SELECT * FROM doctors WHERE doctor_id=?',
        (data['doctor_id'],)
    ).fetchone()
    conn.close()

    if d and check_password_hash(d['password_hash'], data['password']):
        session['doctor_id'] = d['doctor_id']
        session['doctor_name'] = d['name']
        return jsonify(success=True, name=d['name'])

    return jsonify(success=False), 401

@app.route('/api/doctor/logout', methods=['POST'])
def doctor_logout():
    session.clear()
    return jsonify(success=True)

@app.route('/api/check_session')
def check_session():
    return jsonify(logged_in='doctor_id' in session, name=session.get('doctor_name'))

@app.route('/api/send_notification', methods=['POST'])
def send_notification():
    """
    Endpoint for doctors to send custom SMS messages to patients.
    """
    if 'doctor_id' not in session:
        return jsonify(error="Unauthorized"), 401

    data = request.json
    appt_id = data.get('id')
    custom_message = data.get('message')

    conn = get_db()
    row = conn.execute('SELECT phone_number, patient_name FROM appointments WHERE id=?', (appt_id,)).fetchone()
    conn.close()

    if row:
        # Send the custom message
        full_msg = f"Dr. {session['doctor_name']} says: {custom_message}"
        send_sms(row['phone_number'], full_msg)
        return jsonify(success=True)
    else:
        return jsonify(success=False, error="Patient not found"), 404

if __name__ == '__main__':
    if not os.path.exists(DB_NAME):
        init_db()
    app.run(debug=True, port=5000)