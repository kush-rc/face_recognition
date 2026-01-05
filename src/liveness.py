"""
Liveness detection module for the Face Recognition Attendance System.

This module provides functions for blink detection to prevent spoofing attacks.
"""

import dlib
import cv2
from imutils import face_utils
import numpy as np
from config import SHAPE_PREDICTOR_FILE, EYE_AR_THRESH

# Initialize dlib's face detector (HOG-based) and then create
# the facial landmark predictor
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(SHAPE_PREDICTOR_FILE)

def eye_aspect_ratio(eye):
    """
    Computes the eye aspect ratio (EAR) for a given eye.

    Args:
        eye: A list of (x, y)-coordinates for the eye landmarks.

    Returns:
        The eye aspect ratio.
    """
    # compute the euclidean distances between the two sets of
    # vertical eye landmarks (x, y)-coordinates
    A = np.linalg.norm(eye[1] - eye[5])
    B = np.linalg.norm(eye[2] - eye[4])

    # compute the euclidean distance between the horizontal
    # eye landmark (x, y)-coordinates
    C = np.linalg.norm(eye[0] - eye[3])

    # compute the eye aspect ratio
    ear = (A + B) / (2.0 * C)

    # return the eye aspect ratio
    return ear

def detect_blink(gray, rect):
    """
    Detects a blink for a given face.

    Args:
        gray: The grayscale image.
        rect: The bounding box of the face.

    Returns:
        True if a blink is detected, otherwise False.
    """
    # determine the facial landmarks for the face region, then
    # convert the facial landmark (x, y)-coordinates to a NumPy
    # array
    shape = predictor(gray, rect)
    shape = face_utils.shape_to_np(shape)

    # extract the left and right eye coordinates, then use the
    # coordinates to compute the eye aspect ratio for both eyes
    (lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
    (rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]
    leftEye = shape[lStart:lEnd]
    rightEye = shape[rStart:rEnd]
    leftEAR = eye_aspect_ratio(leftEye)
    rightEAR = eye_aspect_ratio(rightEye)

    # average the eye aspect ratio together for both eyes
    ear = (leftEAR + rightEAR) / 2.0
    
    # check to see if the eye aspect ratio is below the blink
    # threshold, and if so, return True
    return ear < EYE_AR_THRESH