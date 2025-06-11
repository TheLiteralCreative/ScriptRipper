import google.generativeai as genai
import os
from dotenv import load_dotenv

print("--- Starting API Connection Test ---")

# Load API Key from .env file
load_dotenv()
try:
    api_key = os.environ["GOOGLE_API_KEY"]
    if not api_key:
        raise KeyError
    genai.configure(api_key=api_key)
    print("API Key loaded and configured successfully.")
except KeyError:
    print("FATAL ERROR: Could not find GOOGLE_API_KEY in your .env file.")
    exit()

# Make the simplest possible API call
try:
    print("Initializing Gemini model...")
    model = genai.GenerativeModel('gemini-1.5-pro-latest')
    
    print("Sending simple prompt to the API...")
    # Set a short timeout because this should be instant
    request_options = {"timeout": 60} 
    response = model.generate_content("Why is the sky blue?", request_options=request_options)
    
    print("\n--- TEST SUCCESSFUL ---")
    print("Received response from API:")
    print(response.text)

except Exception as e:
    print("\n--- TEST FAILED ---")
    print(f"An error occurred during the API call: {e}")