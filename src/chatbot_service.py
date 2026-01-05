"""
Chatbot service for the Streamlit application.

This module contains the `AttendanceChatbot` class, which is responsible
for interacting with the Groq API to provide a chat interface.
"""

from groq import Groq
import os
from dotenv import load_dotenv
from datetime import datetime
from config import CHATBOT_MODEL

class AttendanceChatbot:
    """
    A class to represent the attendance chatbot.
    """
    def __init__(self):
        """
        Initializes the AttendanceChatbot.
        """
        # 1. Load environment variables from .env file
        load_dotenv()
        
        # 2. Get API key from environment variables
        api_key = os.getenv("GROQ_API_KEY")
        
        # 3. Validate the API key
        if not api_key:
            raise ValueError(
                "GROQ_API_KEY not found in .env file. "
                "Please create a .env file with your Groq API key.\n"
                "Example .env content:\n"
                "GROQ_API_KEY=your_api_key_here"
            )
        
        # 4. Initialize Groq client
        self.client = Groq(api_key=api_key)
        
        # 5. Set up chatbot context
        self.context = f"""
        You are an AI assistant for a Face Recognition Attendance System.
        You can help with attendance records, system usage, and troubleshooting.
        Current date: {datetime.now().strftime('%Y-%m-%d')}
        """

    def get_response(self, user_input, attendance_data=None):
        """
        Gets a response from the chatbot.

        Args:
            user_input (str): The user's input.
            attendance_data (str, optional): The attendance data to provide to the chatbot. Defaults to None.

        Returns:
            str: The chatbot's response.
        """
        try:
            # Prepare messages
            messages = [
                {"role": "system", "content": self.context},
                {"role": "user", "content": user_input}
            ]
            
            # Add attendance data if available (for admins)
            if attendance_data:
                messages.insert(1, {"role": "system", "content": f"Attendance data:\n{attendance_data}"})

            # Get response from Groq API
            response = self.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=messages,
                temperature=0.7,
                max_tokens=150
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Sorry, I encountered an error: {str(e)}"