# """
# Face recognition service for the Streamlit application.

# This module contains the `FaceRecognitionTransformer` class, which is responsible
# for processing video frames, detecting and recognizing faces, and marking attendance.
# It also includes the `mark_attendance` function to log attendance records.
# """

# import cv2
# import face_recognition
# import numpy as np
# import streamlit as st
# import time
# import os
# import pandas as pd
# from datetime import datetime
# from config import (
#     MIN_FACE_SIZE,
#     PROCESS_EVERY_N_FRAMES,
#     DOWNSAMPLE_FACTOR,
#     MIN_TIME_BETWEEN_RECORDS,
#     LOG_FILE,
#     ENCODINGS_FILE,
# )
# from streamlit_webrtc import VideoProcessorBase  # Changed from VideoTransformerBase
# import pickle
# from liveness import detect_blink
# import dlib
# import av  # Added this import


# @st.cache_resource
# def load_encodings():
#     """
#     Loads the known face encodings from the pickle file.
#     Uses Streamlit's cache to avoid reloading the data on every run.
#     """
#     if os.path.exists(ENCODINGS_FILE):
#         with open(ENCODINGS_FILE, "rb") as f:
#             return pickle.load(f)
#     return {"encodings": [], "names": []}


# data = load_encodings()


# def mark_attendance(name):
#     """
#     Marks the attendance for a given person.

#     Args:
#         name (str): The name of the person to mark attendance for.

#     Returns:
#         bool: True if attendance was marked successfully, otherwise False.
#     """
#     try:
#         os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
#         now = datetime.now()
#         date_str = now.strftime("%Y-%m-%d")
#         time_str = now.strftime("%H:%M:%S")

#         new_record = {
#             "Name": name,
#             "Date": date_str,
#             "Time": time_str,
#             "Status": "Punch In" # Default status
#         }

#         if os.path.exists(LOG_FILE) and os.path.getsize(LOG_FILE) > 0:
#             df = pd.read_csv(LOG_FILE)
            
#             todays_records = df[(df["Name"] == name) & (df["Date"] == date_str)]
            
#             if not todays_records.empty:
#                 last_status = todays_records["Status"].iloc[-1]
#                 new_record["Status"] = "Punch Out" if last_status == "Punch In" else "Punch In"
            
#             df = pd.concat([df, pd.DataFrame([new_record])], ignore_index=True)
#         else:
#             df = pd.DataFrame([new_record])

#         df.to_csv(LOG_FILE, index=False)
#         st.toast(f"✅ {name} {new_record['Status']} at {time_str}")
#         return True

#     except Exception as e:
#         st.error(f"Error in mark_attendance: {str(e)}")
#         return False


# class FaceRecognitionTransformer(VideoProcessorBase):  # Changed from VideoTransformerBase
#     """
#     A class that processes video frames to perform face recognition.
#     """
#     def __init__(self, liveness_check=False):
#         self.frame_count = 0
#         self.last_detection_time = {}
#         self.liveness_check = liveness_check
#         self.blink_detected = False
#         self.detector = dlib.get_frontal_face_detector()

#     def recv(self, frame):  # Changed from transform
#         """
#         Processes a video frame to perform face recognition.

#         Args:
#             frame: The video frame to process.

#         Returns:
#             The processed video frame with face rectangles and names.
#         """
#         img = frame.to_ndarray(format="bgr24")
#         current_time = time.time()

#         if self.frame_count % PROCESS_EVERY_N_FRAMES == 0:
#             try:
#                 small_img = cv2.resize(img, (0, 0), fx=DOWNSAMPLE_FACTOR, fy=DOWNSAMPLE_FACTOR)
#                 rgb = cv2.cvtColor(small_img, cv2.COLOR_BGR2RGB)
#                 gray = cv2.cvtColor(small_img, cv2.COLOR_BGR2GRAY)
                
#                 face_locations = face_recognition.face_locations(rgb, model="hog")
                
#                 if face_locations:
#                     face_encodings = face_recognition.face_encodings(rgb, face_locations)
                    
#                     for (top, right, bottom, left), encoding in zip(face_locations, face_encodings):
#                         top = int(top / DOWNSAMPLE_FACTOR)
#                         right = int(right / DOWNSAMPLE_FACTOR)
#                         bottom = int(bottom / DOWNSAMPLE_FACTOR)
#                         left = int(left / DOWNSAMPLE_FACTOR)
                        
#                         if (right - left) < MIN_FACE_SIZE or (bottom - top) < MIN_FACE_SIZE:
#                             continue

#                         # Liveness Detection
#                         if self.liveness_check and not self.blink_detected:
#                             rect = dlib.rectangle(left, top, right, bottom)
#                             if detect_blink(gray, rect):
#                                 self.blink_detected = True
#                                 st.toast("Blink Detected! Liveness Confirmed.")
                        
#                         matches = face_recognition.compare_faces(data["encodings"], encoding)
#                         name = "Unknown"
#                         color = (0, 0, 255) 
                        
#                         if True in matches:
#                             matched_idxs = [i for i, match in enumerate(matches) if match]
#                             counts = {}
#                             for i in matched_idxs:
#                                 name_match = data["names"][i]
#                                 counts[name_match] = counts.get(name_match, 0) + 1
#                             name = max(counts, key=counts.get)
#                             color = (0, 255, 0) 
                            
#                             last_time = self.last_detection_time.get(name, 0)
#                             if current_time - last_time > MIN_TIME_BETWEEN_RECORDS:
#                                 if self.liveness_check and self.blink_detected:
#                                     if mark_attendance(name):
#                                         self.last_detection_time[name] = current_time
#                                         self.blink_detected = False # Reset for next user
#                                 elif not self.liveness_check:
#                                     if mark_attendance(name):
#                                         self.last_detection_time[name] = current_time
                        
#                         cv2.rectangle(img, (left, top), (right, bottom), color, 2)
#                         cv2.putText(img, name, (left, top - 10), 
#                                     cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2)
            
#             except Exception as e:
#                 print(f"Face detection error: {str(e)}")

#         self.frame_count += 1
#         return av.VideoFrame.from_ndarray(img, format="bgr24")  # Changed return statement




"""
Face recognition service for the Streamlit application.
"""

import cv2
import face_recognition
import numpy as np
import streamlit as st
import time
import os
import pandas as pd
from datetime import datetime
from config import (
    MIN_FACE_SIZE,
    PROCESS_EVERY_N_FRAMES,
    DOWNSAMPLE_FACTOR,
    MIN_TIME_BETWEEN_RECORDS,
    LOG_FILE,
    ENCODINGS_FILE,
)
from streamlit_webrtc import VideoProcessorBase
import pickle
import av

@st.cache_resource
def load_encodings():
    """Loads the known face encodings from the pickle file."""
    if os.path.exists(ENCODINGS_FILE):
        with open(ENCODINGS_FILE, "rb") as f:
            return pickle.load(f)
    return {"encodings": [], "names": []}

data = load_encodings()

def mark_attendance(name):
    """Marks the attendance for a given person."""
    try:
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H:%M:%S")

        new_record = {
            "Name": name,
            "Date": date_str,
            "Time": time_str,
            "Status": "Punch In"
        }

        if os.path.exists(LOG_FILE) and os.path.getsize(LOG_FILE) > 0:
            df = pd.read_csv(LOG_FILE)
            todays_records = df[(df["Name"] == name) & (df["Date"] == date_str)]
            
            if not todays_records.empty:
                last_status = todays_records["Status"].iloc[-1]
                new_record["Status"] = "Punch Out" if last_status == "Punch In" else "Punch In"
            
            df = pd.concat([df, pd.DataFrame([new_record])], ignore_index=True)
        else:
            df = pd.DataFrame([new_record])

        df.to_csv(LOG_FILE, index=False)
        st.toast(f"✅ {name} {new_record['Status']} at {time_str}")
        return True

    except Exception as e:
        st.error(f"Error in mark_attendance: {str(e)}")
        return False

class FaceRecognitionTransformer(VideoProcessorBase):
    """A class that processes video frames to perform face recognition."""
    
    def __init__(self):
        self.frame_count = 0
        self.last_detection_time = {}

    def recv(self, frame):
        """Processes a video frame to perform face recognition."""
        img = frame.to_ndarray(format="bgr24")
        current_time = time.time()

        if self.frame_count % PROCESS_EVERY_N_FRAMES == 0:
            try:
                small_img = cv2.resize(img, (0, 0), fx=DOWNSAMPLE_FACTOR, fy=DOWNSAMPLE_FACTOR)
                rgb = cv2.cvtColor(small_img, cv2.COLOR_BGR2RGB)
                
                face_locations = face_recognition.face_locations(rgb, model="hog")
                
                if face_locations:
                    face_encodings = face_recognition.face_encodings(rgb, face_locations)
                    
                    for (top, right, bottom, left), encoding in zip(face_locations, face_encodings):
                        top = int(top / DOWNSAMPLE_FACTOR)
                        right = int(right / DOWNSAMPLE_FACTOR)
                        bottom = int(bottom / DOWNSAMPLE_FACTOR)
                        left = int(left / DOWNSAMPLE_FACTOR)
                        
                        if (right - left) < MIN_FACE_SIZE or (bottom - top) < MIN_FACE_SIZE:
                            continue

                        matches = face_recognition.compare_faces(data["encodings"], encoding)
                        name = "Unknown"
                        color = (0, 0, 255)
                        
                        if True in matches:
                            matched_idxs = [i for i, match in enumerate(matches) if match]
                            counts = {}
                            for i in matched_idxs:
                                name_match = data["names"][i]
                                counts[name_match] = counts.get(name_match, 0) + 1
                            name = max(counts, key=counts.get)
                            color = (0, 255, 0)
                            
                            last_time = self.last_detection_time.get(name, 0)
                            if current_time - last_time > MIN_TIME_BETWEEN_RECORDS:
                                if mark_attendance(name):
                                    self.last_detection_time[name] = current_time
                        
                        cv2.rectangle(img, (left, top), (right, bottom), color, 2)
                        cv2.putText(img, name, (left, top - 10), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2)
            
            except Exception as e:
                print(f"Face detection error: {str(e)}")

        self.frame_count += 1
        return av.VideoFrame.from_ndarray(img, format="bgr24")
