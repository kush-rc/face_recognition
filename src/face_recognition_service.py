# """
# Face recognition service for the Streamlit application.
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
# from streamlit_webrtc import VideoProcessorBase
# import pickle
# import av

# @st.cache_resource
# def load_encodings():
#     """Loads the known face encodings from the pickle file."""
#     if os.path.exists(ENCODINGS_FILE):
#         with open(ENCODINGS_FILE, "rb") as f:
#             return pickle.load(f)
#     st.error(f"Encoding file not found at {ENCODINGS_FILE}. Please run 'encode_faces.py'.")
#     return {"encodings": [], "names": []}

# data = load_encodings()

# def mark_attendance(name):
#     """Marks the attendance for a given person."""
#     try:
#         os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
#         now = datetime.now()
#         date_str = now.strftime("%Y-%m-%d")
#         time_str = now.strftime("%H:%M:%S")

#         new_record = {
#             "Name": name,
#             "Date": date_str,
#             "Time": time_str,
#             "Status": "Punch In"
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

# class FaceRecognitionTransformer(VideoProcessorBase):
#     """A class that processes video frames to perform face recognition."""
    
#     def __init__(self):
#         self.frame_count = 0
#         self.last_detection_time = {}

#     def recv(self, frame: av.VideoFrame) -> av.VideoFrame:
#         """Processes a video frame to perform face recognition."""
#         img = frame.to_ndarray(format="bgr24")
#         current_time = time.time()

#         if self.frame_count % PROCESS_EVERY_N_FRAMES == 0:
#             try:
#                 # Resize frame for faster processing
#                 small_img = cv2.resize(img, (0, 0), fx=DOWNSAMPLE_FACTOR, fy=DOWNSAMPLE_FACTOR)
#                 rgb_small_frame = cv2.cvtColor(small_img, cv2.COLOR_BGR2RGB)
                
#                 # Find all the faces and face encodings in the current frame
#                 face_locations = face_recognition.face_locations(rgb_small_frame, model="hog")
#                 face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
                
#                 for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
#                     # Scale back up face locations
#                     top = int(top / DOWNSAMPLE_FACTOR)
#                     right = int(right / DOWNSAMPLE_FACTOR)
#                     bottom = int(bottom / DOWNSAMPLE_FACTOR)
#                     left = int(left / DOWNSAMPLE_FACTOR)
                    
#                     if (right - left) < MIN_FACE_SIZE or (bottom - top) < MIN_FACE_SIZE:
#                         continue

#                     # See if the face is a match for the known face(s)
#                     matches = face_recognition.compare_faces(data["encodings"], face_encoding)
#                     name = "Unknown"
#                     color = (0, 0, 255) # Red for unknown
                    
#                     if True in matches:
#                         face_distances = face_recognition.face_distance(data["encodings"], face_encoding)
#                         best_match_index = np.argmin(face_distances)
#                         if matches[best_match_index]:
#                             name = data["names"][best_match_index]
#                             color = (0, 255, 0) # Green for known
                            
#                             # Mark attendance if not recorded recently
#                             last_time = self.last_detection_time.get(name, 0)
#                             if current_time - last_time > MIN_TIME_BETWEEN_RECORDS:
#                                 if mark_attendance(name):
#                                     self.last_detection_time[name] = current_time
                    
#                     # Draw a box around the face
#                     cv2.rectangle(img, (left, top), (right, bottom), color, 2)
#                     # Draw a label with a name below the face
#                     cv2.rectangle(img, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
#                     font = cv2.FONT_HERSHEY_DUPLEX
#                     cv2.putText(img, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
            
#             except Exception as e:
#                 st.error(f"Face detection error: {str(e)}")

#         self.frame_count += 1
#         return av.VideoFrame.from_ndarray(img, format="bgr24")




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
    st.error(f"Encoding file not found at {ENCODINGS_FILE}. Please run 'encode_faces.py'.")
    return {"encodings": [], "names": []}

def reload_encodings():
    """
    Forces a reload of the face encodings.
    Call this after adding new users to the database.
    """
    st.cache_resource.clear()
    return load_encodings()

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
        # Load fresh encodings when the transformer is initialized
        self.data = load_encodings()

    def recv(self, frame: av.VideoFrame) -> av.VideoFrame:
        """Processes a video frame to perform face recognition."""
        img = frame.to_ndarray(format="bgr24")
        current_time = time.time()

        if self.frame_count % PROCESS_EVERY_N_FRAMES == 0:
            try:
                # Resize frame for faster processing
                small_img = cv2.resize(img, (0, 0), fx=DOWNSAMPLE_FACTOR, fy=DOWNSAMPLE_FACTOR)
                rgb_small_frame = cv2.cvtColor(small_img, cv2.COLOR_BGR2RGB)

                # Find all the faces and face encodings in the current frame
                face_locations = face_recognition.face_locations(rgb_small_frame, model="hog")
                face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

                for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                    # Scale back up face locations
                    top = int(top / DOWNSAMPLE_FACTOR)
                    right = int(right / DOWNSAMPLE_FACTOR)
                    bottom = int(bottom / DOWNSAMPLE_FACTOR)
                    left = int(left / DOWNSAMPLE_FACTOR)

                    if (right - left) < MIN_FACE_SIZE or (bottom - top) < MIN_FACE_SIZE:
                        continue

                    # See if the face is a match for the known face(s)
                    matches = face_recognition.compare_faces(self.data["encodings"], face_encoding)
                    name = "Unknown"
                    color = (0, 0, 255)  # Red for unknown

                    if True in matches:
                        face_distances = face_recognition.face_distance(self.data["encodings"], face_encoding)
                        best_match_index = np.argmin(face_distances)
                        
                        if matches[best_match_index]:
                            name = self.data["names"][best_match_index]
                            color = (0, 255, 0)  # Green for known

                            # Mark attendance if not recorded recently
                            last_time = self.last_detection_time.get(name, 0)
                            if current_time - last_time > MIN_TIME_BETWEEN_RECORDS:
                                if mark_attendance(name):
                                    self.last_detection_time[name] = current_time

                    # Draw a box around the face
                    cv2.rectangle(img, (left, top), (right, bottom), color, 2)
                    
                    # Draw a label with a name below the face
                    cv2.rectangle(img, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
                    font = cv2.FONT_HERSHEY_DUPLEX
                    cv2.putText(img, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

            except Exception as e:
                st.error(f"Face detection error: {str(e)}")

        self.frame_count += 1
        return av.VideoFrame.from_ndarray(img, format="bgr24")
