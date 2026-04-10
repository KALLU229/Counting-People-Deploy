import streamlit as st
import pandas as pd
from firebase_config import db
from db import (
    add_user,
    delete_user,
    get_detections,
    get_logs,
    get_alert_limit,
    set_alert_limit
)
from auth.jwt_utils import verify_token


def admin_panel():
    # ================= JWT AUTH CHECK =================
    token = st.session_state.get("jwt")
    user = verify_token(token)

    if not user or user.get("role") != "admin":
        st.error("Access Denied: Admins only")
        st.stop()

    # ================= DARK ADMIN THEME =================
    st.markdown("""
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}

        .stApp {
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%) !important;
        }

        .admin-title {
            text-align: center;
            font-weight: 800;
            font-size: 42px;
            color: #00bcd4;
            margin-bottom: 2rem;
        }

        h3 {
            color: #80deea !important;
            font-weight: 600 !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # ================= TITLE =================
    st.markdown(
        "<h1 class='admin-title'>Admin Control Panel</h1>",
        unsafe_allow_html=True
    )

    st.info(f"Logged in as Admin: **{user['email']}**")

    # ================= USER MANAGEMENT =================
    st.subheader("User Management")

    # Fetch users from Firebase
    docs = db.collection("users").stream()

    users = []
    for i, doc in enumerate(docs):
        d = doc.to_dict()
        users.append({
            "ID": i + 1,
            "Email": d.get("email"),
            "Role": d.get("role")
        })

    df_users = pd.DataFrame(users) if users else pd.DataFrame()

    st.dataframe(df_users, use_container_width=True)

    # ---- ADD USER ----
    st.markdown("#### Add New User")

    col1, col2, col3 = st.columns(3)

    with col1:
        email = st.text_input("Email", placeholder="user@example.com", key="admin_add_email")
    with col2:
        password = st.text_input("Password", type="password", key="admin_add_password")
    with col3:
        role = st.selectbox("Role", ["user", "admin"], key="admin_add_role")

    if st.button("Add User", use_container_width=True):
        if not email or not password:
            st.error("Please enter email and password")
        elif add_user(email, password, role):
            st.success("User added successfully")
            st.rerun()
        else:
            st.error("User already exists")

    # ---- DELETE USER ----
    st.markdown("#### 🗑 Delete User")

    if not df_users.empty:
        email_to_delete = st.selectbox(
            "Select User",
            df_users["Email"].tolist(),
            key="admin_delete_user_email"
        )

        if st.button("Delete User", use_container_width=True):
            delete_user(email_to_delete)
            st.success("User deleted successfully")
            st.rerun()
    else:
        st.info("No users available")

    # ================= SYSTEM SETTINGS =================
    st.markdown("---")
    st.subheader("System Settings")

    current_limit = get_alert_limit()
    new_limit = st.number_input(
        "Crowd Alert Threshold",
        min_value=1,
        max_value=10000,
        value=current_limit,
        step=1
    )

    if st.button("Save Threshold", use_container_width=True):
        set_alert_limit(int(new_limit))
        st.success(f"Alert threshold updated to {new_limit}")
        st.rerun()

    # ================= SYSTEM LOGS =================
    st.markdown("---")
    st.subheader("System Logs")

    logs = get_logs(200)

    if logs.empty:
        st.info("No logs available")
    else:
        st.dataframe(logs, use_container_width=True, height=400)

    # ================= EXPORT DATA =================
    st.markdown("---")
    st.subheader("Export Detection Data")

    df = get_detections()

    if df.empty:
        st.info("No detection data available")
    else:
        st.download_button(
            "Download Detections CSV",
            df.to_csv(index=False),
            "detections.csv",
            mime="text/csv",
            use_container_width=True
        )