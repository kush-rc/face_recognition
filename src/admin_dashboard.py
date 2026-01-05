"""
Admin dashboard for the Streamlit application.

This module provides the UI and logic for the admin dashboard,
including adding and deleting people from the dataset.
"""

import streamlit as st
import os
import sys
import subprocess
from utils import save_image, delete_person, list_people

def run_encoding_script():
    """
    Runs the encode_faces.py script as a subprocess and shows the status.
    """
    try:
        with st.spinner("New data saved. Re-training face model... This may take a moment."):
            # This command runs the script using the same Python that's running Streamlit
            result = subprocess.run(
                [sys.executable, "src/encode_faces.py"],
                capture_output=True,
                text=True,
                check=True  # This makes it raise an exception if the script fails
            )
            # Important: Clear the cache to force Streamlit to reload the new encodings file
            st.cache_resource.clear()
        st.success("Face model updated successfully!")

    except FileNotFoundError:
        st.error("Error: 'encode_faces.py' not found. Make sure it's in the src folder.")
    except subprocess.CalledProcessError as e:
        # This shows the actual error message from the script if it fails
        st.error(f"The encoding script failed with an error:")
        st.code(e.stderr)
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")

def show_admin_dashboard():
    """
    Displays the admin dashboard.
    """
    st.subheader("Manage Dataset")
    
    with st.expander("Add New Person to Database", expanded=True):
        person_name = st.text_input("Enter the person's name", key="new_person_name")

        method_tab1, method_tab2 = st.tabs(["Upload an Image", "Capture with Camera"])

        with method_tab1:
            uploaded_file = st.file_uploader("Choose an image file", type=["jpg", "jpeg", "png"])
            if st.button("Add from File"):
                if person_name and uploaded_file:
                    path = save_image(uploaded_file, person_name)
                    st.success(f"Image for '{person_name}' saved successfully!")
                    # Automatically re-train after adding
                    run_encoding_script()
                    st.rerun()
                else:
                    st.error("Please provide both a name and an image file.")

        with method_tab2:
            # Initialize session state for storing captured images
            if 'captured_images' not in st.session_state:
                st.session_state.captured_images = []

            # Display the camera input only if we haven't reached the max limit
            if len(st.session_state.captured_images) < 6:
                # A unique key forces the widget to reset properly
                camera_photo = st.camera_input(
                    f"Take picture ({len(st.session_state.captured_images)}/6)",
                    key=f"camera_input_{len(st.session_state.captured_images)}"
                )
                # When a new photo is taken, add it to our list and rerun
                if camera_photo:
                    st.session_state.captured_images.append(camera_photo)
                    st.rerun()
            else:
                st.success("Maximum of 6 images captured. You can now save them.")

            # Display the thumbnails of all captured images
            if st.session_state.captured_images:
                st.write("Captured Images:")
                cols = st.columns(6)
                for i, photo in enumerate(st.session_state.captured_images):
                    with cols[i]:
                        st.image(photo, width=100)

                # Add buttons for saving or clearing the captured images
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ Save All Images", use_container_width=True):
                        if person_name:
                            for photo in st.session_state.captured_images:
                                save_image(photo, person_name)
                            st.success(f"{len(st.session_state.captured_images)} images saved for {person_name}!")
                            # Clear the list after saving
                            st.session_state.captured_images = []
                            # Automatically re-train after adding
                            run_encoding_script()
                            st.rerun()
                        else:
                            st.error("Please enter the person's name before saving.")
                with col2:
                    if st.button("❌ Clear Captured Images", use_container_width=True):
                        st.session_state.captured_images = []
                        st.rerun()
    
    with st.expander("Delete Person"):
        people = list_people()
        if people:
            to_delete = st.selectbox("Select person to delete", people)
            if st.button("Delete This Person"):
                if delete_person(to_delete):
                    st.success(f"Successfully deleted all records and images for {to_delete}.")
                    # Automatically re-train after deleting
                    run_encoding_script()
                    st.rerun()
        else:
            st.info("No people found in the database to delete.")