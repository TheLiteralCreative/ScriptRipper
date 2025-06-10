import google.generativeai as genai
import os
import shutil  # For moving files
import pathlib # For modern path and directory handling
from dotenv import load_dotenv

# --- 1. CONFIGURATION ---

load_dotenv()

try:
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
except KeyError:
    print("FATAL: GOOGLE_API_KEY not found. Please ensure you have a .env file.")
    exit()

# --- FOLDER AND PATH CONFIGURATION ---
# Defines all the key directories the script will use.
BASE_DIR = pathlib.Path(__file__).resolve().parent
SCRIPTS_DIR = BASE_DIR / "Scripts"
RIPPED_DIR = BASE_DIR / "Ripped"

# --- PROMPT PROFILES CONFIGURATION ---
# This dictionary maps folder names to their corresponding prompt sets.
# It makes it easy to add new profiles in the future!
PROMPT_PROFILES = {
    "meetings": [
        {
            "task_name": "Meeting Summary & Action Items",
            "prompt": "Generate a comprehensive summary of the meeting, focusing on dialogue and agreements. Extract all action items into a Markdown table."
        }
        # ... Add other meeting-specific prompts here
    ],
    "presentations": [
        {
            "task_name": "Presentation Outline & Key Quotes",
            "prompt": "Create a hierarchical outline of the main talking points from the presentation. Extract the most impactful quotes."
        }
        # ... Add other presentation-specific prompts here
    ]
}

# --- MASTER PROMPT (unchanged) ---
MASTER_PROMPT = """
# Your full master prompt with formatting rules goes here...
**## INSTRUCTION SET: TRANSCRIPT ANALYSIS PROTOCOL ##**
...
"""

# --- 2. SCRIPT LOGIC ---

def analyze_transcript(transcript_path: pathlib.Path, selected_prompts: list):
    """
    Analyzes a single transcript file, generates reports, and returns True on success.
    The transcript_path is a full Path object now.
    """
    print("-" * 50)
    print(f"Processing transcript: {transcript_path.name}")
    
    try:
        with open(transcript_path, 'r', encoding='utf-8') as f:
            transcript_content = f.read()

        initial_message = MASTER_PROMPT + "\n\n## MEETING TRANSCRIPT ##\n\n" + transcript_content
        model = genai.GenerativeModel('gemini-1.5-pro-latest')
        chat = model.start_chat()

        print("Sending transcript to Gemini...")
        response = chat.send_message(initial_message)
        print(f"Model Acknowledged: {response.text.strip()}")

        base_filename = transcript_path.stem  # Gets filename without extension

        for i, task in enumerate(selected_prompts):
            task_name = task["task_name"]
            prompt = task["prompt"]
            print(f"\nRequesting Analysis Task {i+1}: '{task_name}'...")
            
            response = chat.send_message(prompt)
            
            slug = task_name.lower().replace(' ', '-').replace('&', 'and')
            output_filename = f"{base_filename}_output_{i+1}_{slug}.md"
            output_path = BASE_DIR / output_filename
            
            print(f"Saving analysis to '{output_path.name}'...")
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(response.text)
        
        print("\nAnalysis successful.")
        return True # Indicate success

    except Exception as e:
        print(f"!!-- An error occurred while processing {transcript_path.name}: {e} --!!")
        return False # Indicate failure

# --- 3. MAIN EXECUTION BLOCK ---

if __name__ == "__main__":
    print("Starting ScriptRipper...")
    print(f"Scanning for transcripts in: {SCRIPTS_DIR}")
    
    files_processed = 0

    # The main loop that drives the new workflow
    for profile_name, prompt_set in PROMPT_PROFILES.items():
        input_folder = SCRIPTS_DIR / profile_name
        
        if not input_folder.is_dir():
            print(f"Warning: Folder for profile '{profile_name}' not found at '{input_folder}'. Skipping.")
            continue

        print(f"\n--- Checking folder for '{profile_name}' profile ---")
        
        # Get a list of all files in the directory
        files_to_process = [f for f in input_folder.iterdir() if f.is_file()]

        if not files_to_process:
            print("No new transcripts found.")
            continue

        for transcript_file_path in files_to_process:
            # Process the file
            success = analyze_transcript(transcript_file_path, prompt_set)
            
            # If successful, move the original file to the 'Ripped' folder
            if success:
                destination_path = RIPPED_DIR / transcript_file_path.name
                print(f"Moving processed transcript to '{destination_path}'...")
                shutil.move(transcript_file_path, destination_path)
                files_processed += 1

    print("-" * 50)
    print(f"ScriptRipper run complete. Total files processed: {files_processed}.")