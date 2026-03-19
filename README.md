# CRM HOSPITAL - MediConnect

A Flask-based Hospital Management and CRM system designed for MediConnect. This project manages patient appointments, doctor logins, and automated SMS notifications via Twilio.

## Features
- **Patient Portal**: Schedule appointments and receive SMS confirmations.
- **Doctor Portal**: Secure login to view and manage appointments.
- **SMS Integration**: Automated notifications for booking confirmations and custom doctor messages using Twilio.
- **SQLite Database**: Lightweight storage for appointments and user data.

## Getting Started Locally

1. **Create and Activate Virtual Environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables**:
   Create a `.env` file and add your credentials:
   ```text
   FLASK_SECRET_KEY=your_secret_key
   TWILIO_SID=your_twilio_sid
   TWILIO_AUTH_TOKEN=your_twilio_auth_token
   TWILIO_PHONE_NUMBER=your_twilio_phone_number
   ```

4. **Run the App**:
   ```bash
   python3 app.py
   # Or using Flask run (specifying port if needed):
   python3 -m flask run --port=5001
   ```

## Deployment on Render

This project is optimized for deployment on **Render**.

### 1. Requirements
Ensure `requirements.txt` and `Procfile` are present in the repository.

### 2. Render Setup
- **Service Type**: Web Service.
- **Runtime**: Python.
- **Build Command**: `pip install -r requirements.txt`.
- **Start Command**: `gunicorn app:app`.

### 3. Environment Variables
Add the following in the Render Dashboard:
- `FLASK_SECRET_KEY`
- `TWILIO_SID`
- `TWILIO_AUTH_TOKEN`
- `TWILIO_PHONE_NUMBER`

---

*Note: For production, using a persistent disk or a managed database (like Render PostgreSQL) is recommended for data persistence.*