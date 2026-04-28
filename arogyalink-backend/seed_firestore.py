# Run once to populate demo data: python seed_firestore.py
import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("firebase-service-account.json")
firebase_admin.initialize_app(cred, {
    'projectId': 'arogyalink-prod',
})
fs = firestore.client()

# Demo facilities — Karnataka (near Bangalore / Kolar district)
facilities = [
    {
        "name": "Kolar PHC", "type": "PHC",
        "lat": 13.1329, "lng": 78.1273,
        "address": "Kolar, Karnataka 563101",
        "phone": "+919XXXXXXXXX",
        "has_ambulance": True, "is_active": True,
    },
    {
        "name": "Chintamani CHC", "type": "CHC",
        "lat": 13.4005, "lng": 78.0532,
        "address": "Chintamani, Karnataka 563125",
        "phone": "+919XXXXXXXXX",
        "has_ambulance": True, "is_active": True,
    },
    {
        "name": "Bangarpet PHC", "type": "PHC",
        "lat": 12.9836, "lng": 78.1737,
        "address": "Bangarpet, Karnataka 563114",
        "phone": "+919XXXXXXXXX",
        "has_ambulance": False, "is_active": True,
    },
]

for f in facilities:
    fs.collection("facilities").add(f)
print("Facilities seeded")

# Demo ASHA workers
asha_workers = [
    {
        "name": "Smt. Lakshmi K.", "phone": "+919XXXXXXXXX",
        "lat": 13.1280, "lng": 78.1300,
        "village": "Mulbagal", "is_active": True, "fcm_token": None,
    },
    {
        "name": "Smt. Meena R.", "phone": "+919XXXXXXXXX",
        "lat": 13.1350, "lng": 78.1200,
        "village": "Srinivaspur", "is_active": True, "fcm_token": None,
    },
]

for w in asha_workers:
    fs.collection("asha_workers").add(w)
print("ASHA workers seeded")
