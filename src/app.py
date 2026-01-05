# """
# Main application file for the Streamlit-based Face Recognition Attendance System.
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
#         if 'camera_active' not in st.session_state:
#             st.session_state.camera_active = False

#         # Control buttons
#         col1, col2 = st.columns([1, 5])
#         with col1:
#             if st.button("▶️ Start Camera"):
#                 st.session_state.camera_active = True
#                 st.rerun()
#             if st.button("⏹️ Stop Camera"):
#                 st.session_state.camera_active = False
#                 st.rerun()

#         # Render camera ONLY if explicitly requested
#         if st.session_state.camera_active:
#             st.warning("🔴 Camera Active - Face recognition in progress")
#             webrtc_streamer(
#                 key="face-recognition",
#                 video_processor_factory=FaceRecognitionTransformer,
#                 async_processing=True,
#                 rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
#                 media_stream_constraints={
#                     "video": {"width": 640, "height": 480, "frameRate": 15},
#                     "audio": False
#                 },
#             )
#         else:
#             st.info("📷 Camera is off. Click 'Start Camera' to begin face recognition.")


#     # --- Chat Assistant Tab ---
#     with tabs[1]:
#         st.subheader("Attendance System Chat Assistant")
#         if st.session_state.chatbot is None:
#             st.warning("Chatbot is currently unavailable")
#         else:
#             # Display chat messages from history on app rerun
#             for message in st.session_state.get("chat_history", []):
#                 with st.chat_message(message["role"]):
#                     st.markdown(message["content"])
            
#             if prompt := st.chat_input("Ask me about attendance..."):
#                 # Add user message to chat history
#                 st.session_state.chat_history.append({"role": "user", "content": prompt})
                
#                 # Display user message in chat message container
#                 with st.chat_message("user"):
#                     st.markdown(prompt)

#                 # Prepare context for the chatbot
#                 attendance_data = None
#                 if st.session_state.role == "admin" and os.path.exists(LOG_FILE):
#                     try:
#                         df = pd.read_csv(LOG_FILE)
#                         attendance_data = df.to_string()
#                     except Exception as e:
#                         st.error(f"Error reading attendance log: {e}")

#                 # Get and display assistant response
#                 with st.chat_message("assistant"):
#                     with st.spinner("Thinking..."):
#                         response = st.session_state.chatbot.get_response(prompt, attendance_data)
#                         st.markdown(response)
                
#                 # Add assistant response to chat history
#                 st.session_state.chat_history.append({"role": "assistant", "content": response})


#     # --- Admin and Analytics Tabs (for admin users) ---
#     if st.session_state.role == "admin":
#         if len(tabs) > 2:
#             with tabs[2]:
#                 show_admin_dashboard()
#         if len(tabs) > 3:
#             with tabs[3]:
#                 show_analytics_dashboard()

# if __name__ == "__main__":
#     main()



"""
Main application file for the Streamlit-based Face Recognition Attendance System.
"""
import streamlit as st

# MUST BE FIRST - before any other imports that might use streamlit
st.set_page_config(page_title="Face Recognition System", layout="wide")

# Now import other modules
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
    # --- Page Configuration ---
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
        
        # Camera quality info
        st.info("📹 Camera configured for HD 720p @ 30fps")
        
        # Initialize camera state
        if 'camera_active' not in st.session_state:
            st.session_state.camera_active = False
        
        # Control buttons
        col1, col2 = st.columns([1, 5])
        with col1:
            if st.button("▶️ Start Camera"):
                st.session_state.camera_active = True
                st.rerun()
            if st.button("⏹️ Stop Camera"):
                st.session_state.camera_active = False
                st.rerun()
        
        # Render camera ONLY if explicitly requested
        if st.session_state.camera_active:
            st.warning("🔴 Camera Active - Face recognition in progress")
            webrtc_streamer(
                key="face-recognition",
                video_processor_factory=FaceRecognitionTransformer,
                async_processing=True,
                rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
                media_stream_constraints={
                    "video": {
                        "width": {"ideal": 1280, "min": 1280},
                        "height": {"ideal": 720, "min": 720},
                        "frameRate": {"ideal": 30, "min": 20}
                    },
                    "audio": False
                },
            )
        else:
            st.info("📷 Camera is off. Click 'Start Camera' to begin face recognition.")
    
    # --- Chat Assistant Tab ---
    with tabs[1]:
        st.markdown("### 💬 Attendance System Chat Assistant")
        st.markdown("---")
        
        if st.session_state.chatbot is None:
            st.error("🤖 Chatbot is currently unavailable. Please check your GROQ_API_KEY configuration.")
        else:
            # Create a container for chat messages
            chat_container = st.container()
            
            # Display all chat messages from history
            with chat_container:
                # Show welcome message if no chat history
                if len(st.session_state.get("chat_history", [])) == 0:
                    with st.chat_message("assistant", avatar="🤖"):
                        st.markdown("""
                        👋 **Welcome to the Attendance Chat Assistant!**
                        
                        I can help you with:
                        - 📊 Attendance records and statistics
                        - 🔍 Information about specific employees
                        - ❓ System usage and troubleshooting
                        - 📅 Date-specific attendance queries
                        
                        Feel free to ask me anything!
                        """)
                
                # Display existing chat messages
                for message in st.session_state.get("chat_history", []):
                    avatar = "👤" if message["role"] == "user" else "🤖"
                    with st.chat_message(message["role"], avatar=avatar):
                        st.markdown(message["content"])
            
            # Chat input at the bottom
            prompt = st.chat_input("💭 Ask me about attendance, employees, or system help...")
            
            if prompt:
                # Add user message to chat history
                st.session_state.chat_history.append({"role": "user", "content": prompt})
                
                # Prepare context for the chatbot
                attendance_data = None
                if st.session_state.role == "admin" and os.path.exists(LOG_FILE):
                    try:
                        df = pd.read_csv(LOG_FILE)
                        attendance_data = df.to_string()
                    except Exception as e:
                        st.error(f"⚠️ Error reading attendance log: {e}")
                
                # Get assistant response
                response = st.session_state.chatbot.get_response(prompt, attendance_data)
                
                # Add assistant response to chat history
                st.session_state.chat_history.append({"role": "assistant", "content": response})
                
                # Rerun to display the new messages
                st.rerun()
            
            # Add clear chat button in sidebar
            with st.sidebar:
                st.markdown("---")
                st.markdown("### 💬 Chat Controls")
                if st.button("🗑️ Clear Chat History", use_container_width=True):
                    st.session_state.chat_history = []
                    st.rerun()
                
                # Show chat statistics
                if st.session_state.get("chat_history", []):
                    st.markdown("### 📊 Chat Stats")
                    user_msgs = len([m for m in st.session_state.chat_history if m["role"] == "user"])
                    bot_msgs = len([m for m in st.session_state.chat_history if m["role"] == "assistant"])
                    st.metric("Your Messages", user_msgs)
                    st.metric("Bot Responses", bot_msgs)
    
    # --- Admin and Analytics Tabs (for admin users) ---
    if st.session_state.role == "admin":
        if len(tabs) > 2:
            with tabs[2]:
                show_admin_dashboard()
        if len(tabs) > 3:
            with tabs[3]:
                show_analytics_dashboard()

if __name__ == "__main__":
    main()
