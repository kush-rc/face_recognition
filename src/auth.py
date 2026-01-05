# """
# Authentication module for the Streamlit application.

# This module provides functions for user login and displays the login form.
# """

# import streamlit as st
# from config import USERS

# def check_login(username, password):
#     """
#     Checks if the given username and password are valid.

#     Args:
#         username (str): The username to check.
#         password (str): The password to check.

#     Returns:
#         str: The user's role if the credentials are valid, otherwise None.
#     """
#     user = USERS.get(username)
#     if user and user["password"] == password:
#         return user["role"]
#     return None

# def login_form():
#     """
#     Displays the login form and handles the login process.
#     """
#     st.subheader("🔐 Login")
#     st.warning("This is a demo application. Please use the provided credentials.")
#     username = st.text_input("Username", placeholder="admin or user")
#     password = st.text_input("Password", type="password", placeholder="admin123 or user123")
#     if st.button("Login"):
#         role = check_login(username, password)
#         if role:
#             st.session_state.logged_in = True
#             st.session_state.role = role
#             st.rerun()
#         else:
#             st.error("Invalid credentials")
#     st.stop()


"""
Authentication module for the Streamlit application.
"""

import streamlit as st
import json
import bcrypt
import os

def load_users():
    """Load users from user.json file."""
    user_file = "user.json"
    if os.path.exists(user_file):
        with open(user_file, "r") as f:
            return json.load(f)
    return []

def check_login(username, password):
    """
    Checks if the given username and password are valid.
    
    Args:
        username (str): The username to check.
        password (str): The password to check.
        
    Returns:
        str: The user's role if the credentials are valid, otherwise None.
    """
    users = load_users()
    for user in users:
        if user["username"] == username:
            # Check bcrypt hashed password
            if bcrypt.checkpw(password.encode(), user["password"].encode()):
                return user["role"]
    return None

def login_form():
    """Displays the login form and handles the login process."""
    st.subheader("🔐 Login")
    st.info("Demo credentials - admin/admin123 or john/john123")
    
    username = st.text_input("Username", placeholder="admin or john")
    password = st.text_input("Password", type="password", placeholder="Enter password")
    
    if st.button("Login"):
        role = check_login(username, password)
        if role:
            st.session_state.logged_in = True
            st.session_state.role = role
            st.success(f"Welcome {username}!")
            st.rerun()
        else:
            st.error("Invalid credentials")
