import streamlit as st
import cv2
import tempfile
from vision.process_frame import process_frame, reset_tracker
from db import get_alert_limit

reset_tracker()

def detection_page():
    # ================= DARK DETECTION THEME STYLING =================
    st.markdown("""
        <style>
        /* Hide default elements */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        
        /* Dark solid background */
        .stApp {
            background: linear-gradient(135deg, #0a0e1a 0%, #1a1f35 100%) !important;
        }
        
        /* Detection page title */
        .detection-title {
            text-align: center;
            font-weight: 800;
            font-size: 42px;
            color: #00bcd4;
            text-shadow: 0 0 25px rgba(0, 188, 212, 0.5);
            margin-bottom: 2rem;
            letter-spacing: 1px;
            padding: 1rem;
            border-bottom: 2px solid rgba(0, 188, 212, 0.3);
        }
        </style>
    """, unsafe_allow_html=True)

    # ================= TITLE =================
    st.markdown(
        """
        <h1 class="detection-title">
            Video Upload Detection
        </h1>
        """,
        unsafe_allow_html=True
    )

    # ================= FILE UPLOADER =================
    uploaded = st.file_uploader(
        " Upload Video File",
        type=["mp4", "avi", "mov", "mkv"]
    )

    if not uploaded:
        st.info("Please upload a video file to begin detection")
        return

    # ================= PROCESSING =================
    tfile = tempfile.NamedTemporaryFile(delete=False)
    tfile.write(uploaded.read())

    cap = cv2.VideoCapture(tfile.name)
    frame_window = st.empty()
    status_container = st.empty()

    reset_tracker()
    st.session_state.alert_triggered = False

    total_in = total_out = 0
    frame_count = 0  # 🔥 added for optimization

    ok, frame = cap.read()
    if not ok:
        st.error("Cannot read video file")
        return

    h, w = frame.shape[:2]
    line_y = h // 2

    metrics_cols = st.columns(3)

    # ================= MAIN LOOP =================
    while ok:
        ok, frame = cap.read()
        if not ok:
            break

        frame_count += 1

        #  Control Firebase writes
        save_flag = (frame_count % 3 == 0)

        frame, total_in, total_out, inside = process_frame(
            frame, h, w, line_y, total_in, total_out, save_flag
        )

        # ================= ALERT =================
        current_limit = get_alert_limit()

        if inside >= current_limit and not st.session_state.alert_triggered:
            status_container.error(f" ALERT: Crowd limit exceeded! ({inside}/{current_limit})")
            st.session_state.alert_triggered = True
        elif inside < current_limit:
            st.session_state.alert_triggered = False
            status_container.empty()

        # ================= METRICS =================
        with metrics_cols[0]:
            st.metric(" Entered", total_in)
        with metrics_cols[1]:
            st.metric(" Exited", total_out)
        with metrics_cols[2]:
            st.metric(" Inside", inside)

        # 🔥 Reduce UI refresh load
        if frame_count % 2 == 0:
            frame_window.image(
                cv2.cvtColor(frame, cv2.COLOR_BGR2RGB),
                width=min(w, 800)
            )

    cap.release()
    st.session_state.alert_triggered = False

    st.success("Video processing completed successfully!")

    summary_cols = st.columns(3)
    with summary_cols[0]:
        st.metric("Total Entered", total_in)
    with summary_cols[1]:
        st.metric("Total Exited", total_out)
    with summary_cols[2]:
        st.metric("Final Inside Count", inside)