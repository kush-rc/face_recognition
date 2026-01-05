"""
Utility functions for the Face Recognition Attendance System.

This module provides helper functions for managing the dataset of face images,
including saving and deleting images, and listing the people in the dataset.
"""

import os
import shutil
from PIL import Image
from datetime import datetime
from config import DATASET_DIR

def save_image(uploaded_file, person_name):
    """
    Saves an uploaded image file with a unique, descriptive name.

    Args:
        uploaded_file: The uploaded file object.
        person_name (str): The name of the person.

    Returns:
        str: The path to the saved image file, or None if an error occurred.
    """
    # Sanitize person's name to create a valid directory name
    person_folder_name = person_name.strip().replace(" ", "_")
    person_dir = os.path.join(DATASET_DIR, person_folder_name)
    os.makedirs(person_dir, exist_ok=True)

    # Combine the person's name with a timestamp for a unique, descriptive filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    safe_person_name = person_name.strip().replace(" ", "_")
    file_path = os.path.join(person_dir, f"{safe_person_name}_{timestamp}.jpg")

    # Open and save the image
    try:
        image = Image.open(uploaded_file)
        if image.mode != 'RGB':
            image = image.convert('RGB')
        image.save(file_path, "JPEG")
        return file_path
    except Exception as e:
        print(f"Could not save image: {e}")
        return None

def delete_person(person_name):
    """
    Deletes the entire directory for a given person.

    Args:
        person_name (str): The name of the person to delete.

    Returns:
        bool: True if the directory was deleted successfully, otherwise False.
    """
    person_folder_name = person_name.strip().replace(" ", "_")
    person_dir = os.path.join(DATASET_DIR, person_folder_name)
    if os.path.exists(person_dir):
        try:
            shutil.rmtree(person_dir)
            return True
        except Exception as e:
            print(f"Error deleting directory {person_dir}: {e}")
            return False
    return False

def list_people():
    """
    Lists all people (directories) in the dataset folder.

    Returns:
        list: A sorted list of people in the dataset.
    """
    if not os.path.exists(DATASET_DIR):
        return []
    return sorted([name for name in os.listdir(DATASET_DIR) if os.path.isdir(os.path.join(DATASET_DIR, name))])
