import random
import string
import json
from referral_manager import load_db, save_db

def generate_wallet():
    # Mock wallet generation
    wallet_address = ''.join(random.choices(string.ascii_letters + string.digits, k=34))
    passphrase = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
    return wallet_address, passphrase

def create_wallet_for_user(user_id):
    db = load_db()
    if str(user_id) not in db["users"]:
        return None
    wallet, passphrase = generate_wallet()
    db["users"][str(user_id)]["wallet"] = wallet
    db["users"][str(user_id)]["passphrase"] = passphrase
    save_db(db)
    return wallet, passphrase
