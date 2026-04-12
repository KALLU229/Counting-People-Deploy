import streamlit as st
from views.login import login_page
from views.register import register_page
from views.dashboard import dashboard
# from views.detection import detection_page
# from views.live_camera import live_camera_page
from views.admin_panel import admin_panel
from auth.jwt_utils import verify_token

# ================== APP INIT ==================
st.set_page_config(
    page_title="Crowd Counting System",
    layout="wide"
)

# ================== AUTH UTIL ==================
def get_current_user():
    token = st.session_state.get("jwt")
    if not token:
        return None
    return verify_token(token)

# ================== SESSION ==================
user = get_current_user()

if not user:
    page = st.sidebar.radio("Auth", ["Login", "Register"])
    if page == "Login":
        login_page()
    else:
        register_page()
else:
    st.sidebar.success(f"Logged in as {user['email']}")

    if st.sidebar.button("Logout"):
        st.session_state.pop("jwt", None)
        st.rerun()

    pages = ["Dashboard", "Detection", "Live Camera"]

    if user["role"] == "admin":
        pages.append("Admin Panel")

    page = st.sidebar.radio("Menu", pages)

    if page == "Dashboard":
        dashboard()
    # elif page == "Detection":
    #     detection_page()
    # elif page == "Live Camera":
    #     live_camera_page()
    elif page == "Admin Panel":
        admin_panel()