import random
from database import get_db
from mailer import send_otp

otp_store = {}

def register_user(name, email):
    if not email.endswith("@paruluniversity.ac.in"):
        return False, "Use college email only"

    db = get_db()
    try:
        db.execute(
            "INSERT INTO users (name, email) VALUES (?, ?)",
            (name, email)
        )
        db.commit()
        db.close()
        return True, "Registered successfully"
    except:
        db.close()
        return False, "User already registered"


def verify_otp(email, otp):
    if otp_store.get(email) == otp:
        conn = get_db()
        conn.execute(
            "UPDATE users SET verified=1 WHERE email=?",
            (email,)
        )
        conn.commit()
        conn.close()
        return True
    return False