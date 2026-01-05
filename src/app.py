# """
# Main application file for the Streamlit-based Face Recognition Attendance System.

# This file handles the main application logic, including:
# - User authentication
# - UI layout and navigation
# - Real-time face recognition from webcam
# - Chatbot interaction
# - Admin and analytics dashboards
# """

# import streamlit as st

# # MUST BE FIRST - before any other imports that might use streamlit
# st.set_page_config(page_title="Face Recognition System", layout="wide")

# # Now import other modules
# from streamlit_webrtc import webrtc_streamer
# from face_recognition_service import FaceRecognitionTransformer
# from chatbot_service import AttendanceChatbot
# from auth import login_form
# from admin_dashboard import show_admin_dashboard
# from analytics_dashboard import show_analytics_dashboard
# from dotenv import load_dotenv
# import os
# import pandas as pd
# from config import LOG_FILE

# def main():
#     """
#     Main function to run the Streamlit application.
#     """
#     # --- Page Configuration ---
#     st.title("🧠 Face Recognition Attendance System")

#     # --- Load Environment Variables ---
#     load_dotenv()

#     # --- User Authentication ---
#     if "logged_in" not in st.session_state:
#         st.session_state.logged_in = False
#         st.session_state.role = None

#     if not st.session_state.logged_in:
#         login_form()
#         return

#     # --- Sidebar ---
#     with st.sidebar:
#         st.write(f"👤 Logged in as: {st.session_state.role}")
#         liveness_check = st.checkbox("Enable Liveness Check", value=False)
#         if st.button("🚪 Logout"):
#             st.session_state.logged_in = False
#             st.session_state.role = None
#             st.rerun()

#     # --- Initialize Chatbot ---
#     if "chatbot" not in st.session_state:
#         try:
#             st.session_state.chatbot = AttendanceChatbot()
#             st.session_state.chat_history = []
#         except Exception as e:
#             st.error(f"Chatbot initialization failed: {str(e)}")
#             st.session_state.chatbot = None

#     # --- Main Tabs ---
#     tabs_list = ["📷 Live Recognition", "💬 Chat Assistant"]
#     if st.session_state.role == "admin":
#         tabs_list += ["🛠️ Admin Dashboard", "📊 Advanced Analytics"]

#     tabs = st.tabs(tabs_list)

#    # --- Live Recognition Tab ---
#     with tabs[0]:
#         st.subheader("Live Webcam Recognition")

#         # Initialize camera state
#         if 'show_camera' not in st.session_state:
#             st.session_state.show_camera = False

#         # Control buttons
#         col1, col2 = st.columns([1, 5])
#         with col1:
#             if st.button("▶️ Start Camera"):
#                 st.session_state.show_camera = True
#             if st.button("⏹️ Stop Camera"):
#                 st.session_state.show_camera = False

#         # Render camera ONLY if explicitly requested
#         if st.session_state.show_camera:
#             st.warning("🔴 Camera Active - Face recognition in progress")
#             ctx = webrtc_streamer(
#                 key="face-recognition",
#                 video_processor_factory=lambda: FaceRecognitionTransformer(liveness_check=liveness_check),
#                 async_processing=True,
#                 rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
#                 media_stream_constraints={
#                     "video": {"width": 640, "height": 480, "frameRate": 15},
#                     "audio": False
#                 },
#                 desired_playing_state=True
#             )

#             # Add a stop button that actually stops the stream
#             if st.button("🛑 Force Stop", key="force_stop"):
#                 st.session_state.show_camera = False
#                 st.rerun()
#         else:
#             st.info("📷 Camera is off. Click 'Start Camera' to begin face recognition.")


#     # --- Chat Assistant Tab ---
#     with tabs[1]:
#         st.subheader("Attendance System Chat Assistant")
#         if st.session_state.chatbot is None:
#             st.warning("Chatbot is currently unavailable")
#         else:
#             for message in st.session_state.chat_history:
#                 with st.chat_message(message["role"]):
#                     st.markdown(message["content"])
            
#             if prompt := st.chat_input("Ask me about attendance..."):
#                 st.session_state.chat_history.append({"role": "user", "content": prompt})
                
#                 attendance_data = None
#                 if st.session_state.role == "admin" and os.path.exists(LOG_FILE):
#                     df = pd.read_csv(LOG_FILE)
#                     attendance_data = df.to_string()
                
#                 with st.spinner("Thinking..."):
#                     response = st.session_state.chatbot.get_response(prompt, attendance_data)
#                 st.session_state.chat_history.append({"role": "assistant", "content": response})
#                 st.rerun()

#     # --- Admin and Analytics Tabs (for admin users) ---
#     if st.session_state.role == "admin":
#         with tabs[2]:
#             show_admin_dashboard()

#         with tabs[3]:
#             show_analytics_dashboard()

# if __name__ == "__main__":
#     main()




"""
Main application file for the Streamlit-based Face Recognition Attendance System.
"""

import streamlit as st

# MUST BE FIRST - before other streamlit imports
st.set_page_config(page_title="Face Recognition System", layout="wide")

from streamlit_webrtc import webrtc_streamer
from face_recognition_service import FaceRecognitionTransformer
from chatbot_service import AttendanceChatbot
from auth import login_form
from admin_dashboard import show_admin_dashboard
from analytics_dashboard import show_analytics_dashboard
from dotenv import load_dotenv
import os
import pandas as pd
from config import LOG_FILE


def main():
    """
    Main function to run the Streamlit application.
    """
    st.title("🧠 Face Recognition Attendance System")

    # --- Load Environment Variables ---
    load_dotenv()

    # --- User Authentication ---
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.role = None

    if not st.session_state.logged_in:
        login_form()
        return

    # --- Sidebar ---
    with st.sidebar:
        st.write(f"👤 Logged in as: {st.session_state.role}")
        # liveness_check = st.checkbox("Enable Liveness Check", value=False)
        if st.button("🚪 Logout"):
            st.session_state.logged_in = False
            st.session_state.role = None
            st.rerun()

    # --- Initialize Chatbot ---
    if "chatbot" not in st.session_state:
        try:
            st.session_state.chatbot = AttendanceChatbot()
            st.session_state.chat_history = []
        except Exception as e:
            st.error(f"Chatbot initialization failed: {str(e)}")
            st.session_state.chatbot = None

    # --- Main Tabs ---
    tabs_list = ["📷 Live Recognition", "💬 Chat Assistant"]
    if st.session_state.role == "admin":
        tabs_list += ["🛠️ Admin Dashboard", "📊 Advanced Analytics"]

    tabs = st.tabs(tabs_list)

    # --- Live Recognition Tab ---
    with tabs[0]:
        st.subheader("Live Webcam Recognition")
        
        # Initialize state FIRST
        if 'camera_active' not in st.session_state:
            st.session_state.camera_active = False
        
        # Buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("▶️ Start Camera", key="btn_start"):
                st.session_state.camera_active = True
                st.rerun()
        with col2:
            if st.button("⏹️ Stop Camera", key="btn_stop"):
                st.session_state.camera_active = False
                st.rerun()
        
        # Show camera ONLY when active
        if st.session_state.camera_active:
            st.warning("🔴 Camera is ACTIVE")
            webrtc_streamer(
                key="face-recognition",
                video_processor_factory=FaceRecognitionTransformer,  # Removed lambda and liveness_check
                async_processing=True,
                rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
                media_stream_constraints={
                    "video": {"width": 640, "height": 480, "frameRate": 15},
                    "audio": False
                }
            )
        else:
            st.info("📷 Camera is off. Click 'Start Camera' to begin face recognition.")

    # --- Chat Assistant Tab ---
    with tabs[1]:
        st.subheader("Attendance System Chat Assistant")
        if st.session_state.chatbot is None:
            st.warning("Chatbot is currently unavailable")
        else:
            for message in st.session_state.chat_history:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
            
            if prompt := st.chat_input("Ask me about attendance..."):
                st.session_state.chat_history.append({"role": "user", "content": prompt})
                
                attendance_data = None
                if st.session_state.role == "admin" and os.path.exists(LOG_FILE):
                    df = pd.read_csv(LOG_FILE)
                    attendance_data = df.to_string()
                
                with st.spinner("Thinking..."):
                    response = st.session_state.chatbot.get_response(prompt, attendance_data)
                st.session_state.chat_history.append({"role": "assistant", "content": response})
                st.rerun()

    # --- Admin and Analytics Tabs (for admin users) ---
    if st.session_state.role == "admin":
        with tabs[2]:
            show_admin_dashboard()

        with tabs[3]:
            show_analytics_dashboard()


if __name__ == "__main__":
    main()
