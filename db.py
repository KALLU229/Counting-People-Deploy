import streamlit as st
from firebase_config import db
from datetime import datetime
import pandas as pd

# ================== USERS ==================
def add_user(email, password, role):
    try:
        db.collection("users").document(email).set({
            "email": email,
            "password": password,
            "role": role
        })
        return True
    except:
        return False

def validate_user(email, password):
    doc = db.collection("users").document(email).get()

    if doc.exists:
        data = doc.to_dict()
        if data["password"] == password:
            return {"email": email, "role": data["role"]}

    return None

def delete_user(email):
    db.collection("users").document(email).delete()

# ================== LOGGING ==================
def log(level, message):
    db.collection("logs").add({
        "level": level,
        "message": message,
        "timestamp": datetime.now()
    })
    
def get_logs(limit=100):
    docs = db.collection("logs") \
             .order_by("timestamp", direction="DESCENDING") \
             .limit(limit) \
             .stream()

    data = []
    for doc in docs:
        d = doc.to_dict()
        data.append({
            "Level": d["level"],
            "Message": d["message"],
            "Timestamp": d["timestamp"]
        })

    return pd.DataFrame(data)

# ================== DETECTIONS ==================
def save_detection(track_id, x, y):
    db.collection("detections").add({
        "track_id": track_id,
        "x": x,
        "y": y,
        "timestamp": datetime.now()
    })

def get_detections():
    docs = db.collection("detections") \
             .order_by("timestamp", direction="DESCENDING") \
             .limit(200) \
             .stream()

    data = []
    for doc in docs:
        d = doc.to_dict()
        data.append({
            "track_id": d["track_id"],
            "x": d["x"],
            "y": d["y"],
            "timestamp": d["timestamp"]
        })

    return pd.DataFrame(data)

# ================== COUNTER ==================
def update_live_count(entered, exited, inside):
    db.collection("people_counter").add({
        "entered": entered,
        "exited": exited,
        "inside": inside,
        "timestamp": datetime.now()
    })


def get_counter_history():
    docs = db.collection("people_counter") \
             .order_by("timestamp", direction="DESCENDING") \
             .limit(100) \
             .stream()

    data = []
    for doc in docs:
        d = doc.to_dict()
        data.append({
            "entered": d["entered"],
            "exited": d["exited"],
            "inside": d["inside"],
            "timestamp": d["timestamp"]
        })

    return pd.DataFrame(data)

# ================== SETTINGS ==================
def set_alert_limit(limit):
    db.collection("settings").document("alert").set({
        "limit": limit
    })

def get_alert_limit():
    doc = db.collection("settings").document("alert").get()
    if doc.exists:
        return doc.to_dict().get("limit", 10)
    return 10