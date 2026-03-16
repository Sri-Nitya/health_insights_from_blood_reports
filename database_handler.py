import hashlib
import json
import os
import base64
import bcrypt
from cryptography.fernet import Fernet
import typing
import sqlite3
from datetime import datetime


BASE_DIR = os.path.dirname(__file__)
DATA_FILE = os.path.join(BASE_DIR, "users.json")
CURRENT_SESSION_FILE = os.path.join(BASE_DIR, "current_session.json")
FERNET_KEY_FILE = os.path.join(BASE_DIR, "fernet.key")
REPORT_ENCRYPTION_KEY = os.environ.get("REPORT_KEY")
DB_FILE = os.path.join(BASE_DIR, "data.db")


def _get_conn():
    return sqlite3.connect(DB_FILE)


def init_db():
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            email TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            username TEXT
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT,
            text TEXT,
            file_bytes TEXT,
            file_type TEXT,
            file_name TEXT,
            created_at TEXT,
            FOREIGN KEY(email) REFERENCES users(email)
        )
        """
    )
    conn.commit()
    conn.close()


def _migrate_json_to_db():
    if not os.path.exists(DATA_FILE):
        return
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return

    conn = _get_conn()
    cur = conn.cursor()
    for email, info in data.items():
        password = info.get("password")
        username = info.get("username")
        try:
            cur.execute("INSERT OR IGNORE INTO users(email, password, username) VALUES (?, ?, ?)", (email, password, username))
        except Exception:
            pass
        for rpt in info.get("reports", []):
            try:
                cur.execute(
                    "INSERT INTO reports(email, text, file_bytes, file_type, file_name, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                    (
                        email,
                        rpt.get("text"),
                        rpt.get("file_bytes"),
                        rpt.get("file_type"),
                        rpt.get("file_name"),
                        datetime.utcnow().isoformat(),
                    ),
                )
            except Exception:
                pass
    conn.commit()
    conn.close()


init_db()
_migrate_json_to_db()

def register_user(email, password, username=None):
    conn = _get_conn()
    cur = conn.cursor()
    try:
        # store bcrypt hashed password
        hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        cur.execute("INSERT INTO users(email, password, username) VALUES (?, ?, ?)", (email, hashed, username))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    except Exception:
        return False
    finally:
        conn.close()

def authenticate_user(email, password):
    conn = _get_conn()
    cur = conn.cursor()
    try:
        cur.execute("SELECT password FROM users WHERE email = ?", (email,))
        row = cur.fetchone()
        if not row:
            return False
        stored = row[0]
        if stored and stored.startswith("$2"):
            return bcrypt.checkpw(password.encode("utf-8"), stored.encode("utf-8"))
        return False
    except Exception:
        return False
    finally:
        conn.close()


def _get_fernet():
    key = REPORT_ENCRYPTION_KEY
    if key:
        try:
            return Fernet(key.encode("utf-8"))
        except Exception:
            pass

    if os.path.exists(FERNET_KEY_FILE):
        try:
            with open(FERNET_KEY_FILE, "rb") as f:
                k = f.read().strip()
                return Fernet(k)
        except Exception:
            pass

    try:
        k = Fernet.generate_key()
        with open(FERNET_KEY_FILE, "wb") as f:
            f.write(k)
        return Fernet(k)
    except Exception:
        return None


def encrypt_bytes(raw: bytes) -> bytes:
    f = _get_fernet()
    if not f:
        return raw
    try:
        return f.encrypt(raw)
    except Exception:
        return raw


def decrypt_bytes(enc: bytes) -> bytes:
    f = _get_fernet()
    if not f:
        return enc
    try:
        return f.decrypt(enc)
    except Exception:
        return enc

def save_report(email, text, file_bytes, file_type, file_name):
    conn = _get_conn()
    cur = conn.cursor()
    try:
        report_hash = hashlib.sha256(file_bytes).hexdigest()

        cur.execute(
            "SELECT 1 FROM reports WHERE email = ? AND hash = ?",
            (email, report_hash)
        )
        existing = cur.fetchone()

        if existing:
            print("Duplicate report detected. Skipping save.")
            return
        enc = encrypt_bytes(file_bytes)
        encrypted_text = encrypt_bytes(text.encode("utf-8"))
        encoded_text = base64.b64encode(encrypted_text).decode("utf-8")
        encoded_bytes = base64.b64encode(enc).decode("utf-8")
        cur.execute(
            "INSERT INTO reports(email, text, file_bytes, file_type, file_name, created_at, hash) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (email, encoded_text, encoded_bytes, file_type, file_name, datetime.utcnow().isoformat(), report_hash),
        )
        conn.commit()
    except Exception as e:
        print("Error saving report:", e)
    finally:
        conn.close()

def load_reports_for_user(email):
    conn = _get_conn()
    cur = conn.cursor()
    try:
        cur.execute(
            "SELECT text, file_bytes, file_type, file_name, created_at FROM reports WHERE email = ? ORDER BY id",
            (email,),
        )
        rows = cur.fetchall()
        reports = []
        for r in rows:
            try:
                decoded_bytes = base64.b64decode(r[1])
                file_bytes = decrypt_bytes(decoded_bytes)
            except Exception:
                print("File decode failed, using raw")
                file_bytes = None

            try:
                decoded_text = base64.b64decode(r[0])
                text = decrypt_bytes(decoded_text).decode("utf-8")
            except Exception:
                print("Text decode failed, using raw text")
                text = r[0]

            reports.append({
                "text": text,
                "file_bytes": file_bytes,
                "file_type": r[2],
                "file_name": r[3],
                "created_at": r[4],
            })
        return reports
    except Exception:
        return []
    finally:
        conn.close()


def save_current_session(email):
    try:
        with open(CURRENT_SESSION_FILE, "w") as f:
            json.dump({"username": email}, f)
    except Exception as e:
        print(f"Error saving session: {e}")


def load_current_session():
    if not os.path.exists(CURRENT_SESSION_FILE):
        return None
    try:
        with open(CURRENT_SESSION_FILE, "r") as f:
            data = json.load(f)
            return data.get("username")
    except Exception:
        return None


def clear_current_session():
    try:
        if os.path.exists(CURRENT_SESSION_FILE):
            os.remove(CURRENT_SESSION_FILE)
    except Exception:
        pass

def get_username(email):
    conn = _get_conn()
    cur = conn.cursor()
    try:
        cur.execute("SELECT username FROM users WHERE email = ?", (email,))
        row = cur.fetchone()
        if row:
            return row[0]
        return None
    except Exception:
        return None
    finally:
        conn.close()
        
def delete_report(email, created_at):
    conn = _get_conn()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM reports WHERE email = ? AND created_at = ?", (email, created_at))
        conn.commit()
    except Exception:
        pass
    finally:
        conn.close()