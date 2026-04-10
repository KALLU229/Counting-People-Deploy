from firebase_config import db

db.collection("users").document("admin@admin.com").set({
    "email": "admin@admin.com",
    "password": "admin",
    "role": "admin"
})