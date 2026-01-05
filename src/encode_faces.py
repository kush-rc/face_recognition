"""
Face encoding script for the Face Recognition Attendance System.

This script iterates through the dataset of face images, computes the
face encodings for each face, and saves the encodings to a pickle file.
"""

import face_recognition
import os
import pickle
from PIL import Image
from config import DATASET_DIR, ENCODINGS_FILE

def encode_faces():
    """
    Encodes all the faces in the dataset and saves them to a pickle file.
    """
    known_encodings = []
    known_names = []
    
    print("Starting face encoding process...")
    for person_name in os.listdir(DATASET_DIR):
        person_dir = os.path.join(DATASET_DIR, person_name)
        if not os.path.isdir(person_dir):
            continue
            
        for img_name in os.listdir(person_dir):
            img_path = os.path.join(person_dir, img_name)
            # Check if it's an image file
            if not img_name.lower().endswith(('.jpg', '.jpeg', '.png')):
                continue
                
            try:
                print(f"Processing {person_name}/{img_name}...")
                image = face_recognition.load_image_file(img_path)
                
                # The face_encodings function can find multiple faces, so we use a loop
                encodings = face_recognition.face_encodings(image)
                
                for encoding in encodings:
                    # Append the encoding and the person's name (folder name)
                    known_encodings.append(encoding)
                    known_names.append(person_name)
            except Exception as e:
                print(f"[WARNING] Could not process image {img_path}: {e}")
    
    print(f"\nFound and encoded {len(known_names)} faces.")
    
    # Save the encodings to a pickle file
    data = {"encodings": known_encodings, "names": known_names}
    with open(ENCODINGS_FILE, "wb") as f:
        pickle.dump(data, f)
    print(f"Encodings saved to {ENCODINGS_FILE}")

if __name__ == "__main__":
    encode_faces()
