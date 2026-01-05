"""
Configuration file for the Face Recognition Attendance System.

This file contains all the configuration variables for the application,
such as file paths, face recognition parameters, attendance rules, and more.
Centralizing the configuration makes the application more maintainable.
"""

import os

# --- General Configuration ---
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATASET_DIR = os.path.join(ROOT_DIR, "dataset")

# --- File Paths ---
ENCODINGS_FILE = os.path.join(ROOT_DIR, "encodings.pickle")
LOG_FILE = os.path.join(ROOT_DIR, "attendance_log.csv")
SHAPE_PREDICTOR_FILE = os.path.join(ROOT_DIR, "shape_predictor_68_face_landmarks.dat")

# --- Face Recognition Parameters ---
MIN_FACE_SIZE = 100  # Minimum face size to detect (in pixels)
PROCESS_EVERY_N_FRAMES = 5  # Process every Nth frame to save resources
DOWNSAMPLE_FACTOR = 0.5  # Downsample factor for faster processing
MIN_TIME_BETWEEN_RECORDS = 60  # Cooldown in seconds between records for the same person

# --- Liveness Detection Parameters ---
EYE_AR_THRESH = 0.2  # Threshold for eye aspect ratio to detect a blink

# --- Attendance Rules ---
REQUIRED_HOURS_FULL_DAY = 8.5  # 8 hours 30 minutes
REQUIRED_HOURS_HALF_DAY = 4.25  # 4 hours 15 minutes
WORKING_DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

# --- Chatbot Configuration ---
CHATBOT_MODEL = "llama3-8b-8192"

# --- Authentication (for demonstration purposes) ---
# In a real application, use a secure way to store user data
USERS = {
    "admin": {"password": "admin123", "role": "admin"},
    "user": {"password": "user123", "role": "user"}
}