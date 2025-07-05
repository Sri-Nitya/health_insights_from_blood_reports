import json
import os
import base64


DATA_FILE = "users.json"

def load_users():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(DATA_FILE, "w") as f:
        json.dump(users, f)

def register_user(email, password):
    users = load_users()
    if email in users:
        return False
    users[email] = {"password": password, "reports": []}
    save_users(users)
    return True

def authenticate_user(email, password):
    users = load_users()
    return email in users and users[email]["password"] == password

def save_report(email, text, file_bytes, file_type, file_name):
    users = load_users()
    if email in users:
        encoded_bytes = base64.b64encode(file_bytes).decode("utf-8")  # Encode bytes to base64 string
        users[email]["reports"].append({
            "text": text,
            "file_bytes": encoded_bytes,
            "file_type": file_type,
            "file_name": file_name
        })
        save_users(users)

def load_reports_for_user(email):
    users = load_users()
    if email in users:
        return users[email].get("reports", [])
    return []