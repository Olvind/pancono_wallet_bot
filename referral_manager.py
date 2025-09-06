import json
import random
import string

DATABASE_FILE = "database.json"

def load_db():
    with open(DATABASE_FILE, "r") as f:
        return json.load(f)

def save_db(db):
    with open(DATABASE_FILE, "w") as f:
        json.dump(db, f, indent=4)

def generate_referral_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

def add_user(user_id):
    db = load_db()
    if str(user_id) not in db["users"]:
        code = generate_referral_code()
        db["users"][str(user_id)] = {
            "balance": 0,
            "wallet": None,
            "passphrase": None,
            "referral_code": code,
            "referred_by": None
        }
        save_db(db)
    return db["users"][str(user_id)]

def add_referral(user_id, referral_code):
    db = load_db()
    for uid, udata in db["users"].items():
        if udata["referral_code"] == referral_code:
            db["users"][str(user_id)]["referred_by"] = referral_code
            db["users"][str(uid)].setdefault("referrals", []).append(str(user_id))
            save_db(db)
            return True
    return False
