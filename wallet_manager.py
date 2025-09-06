import json
import os
import random

DATABASE_FILE = "database.json"

def load_db():
    if not os.path.exists(DATABASE_FILE):
        return {"users": {}, "keys": {}}
    with open(DATABASE_FILE, "r") as f:
        return json.load(f)

def save_db(db):
    with open(DATABASE_FILE, "w") as f:
        json.dump(db, f, indent=2)

def create_wallet_for_user(user_id):
    db = load_db()
    if str(user_id) not in db["users"]:
        db["users"][str(user_id)] = {
            "wallet": f"PANCA{random.randint(100000,999999)}",
            "passphrase": f"word{random.randint(1000,9999)}",
            "balance": 0,
            "imported_keys": []
        }
        save_db(db)
    return db["users"][str(user_id)]["wallet"], db["users"][str(user_id)]["passphrase"]

def import_private_key(user_id, private_key):
    db = load_db()
    if private_key not in db["keys"]:
        db["keys"][private_key] = 0
    if str(user_id) not in db["users"]:
        create_wallet_for_user(user_id)
        db = load_db()
    if private_key not in db["users"][str(user_id)]["imported_keys"]:
        db["users"][str(user_id)]["imported_keys"].append(private_key)
    save_db(db)
    return db["keys"][private_key]

def get_balance(user_id):
    db = load_db()
    if str(user_id) not in db["users"]:
        return {"main": 0, "imported": {}}
    user = db["users"][str(user_id)]
    balances = {"main": user["balance"], "imported": {}}
    for k in user.get("imported_keys", []):
        balances["imported"][k] = db["keys"].get(k, 0)
    return balances

def send_panca(user_id, recipient_wallet, amount):
    db = load_db()
    if str(user_id) not in db["users"]:
        return False, "❌ You don’t have a wallet. Create one first."

    sender = db["users"][str(user_id)]
    if sender["balance"] < amount:
        return False, "❌ Insufficient balance."

    # find recipient by wallet
    recipient_id = None
    for uid, u in db["users"].items():
        if u["wallet"] == recipient_wallet:
            recipient_id = uid
            break
    if not recipient_id:
        return False, "❌ Recipient wallet not found."

    # transfer
    sender["balance"] -= amount
    db["users"][recipient_id]["balance"] += amount
    save_db(db)
    return True, f"✅ Sent {amount} PANCA to {recipient_wallet}!"
