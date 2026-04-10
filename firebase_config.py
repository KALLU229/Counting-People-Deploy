import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate(dict(st.secrets["firebase"]))

if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

db = firestore.client()