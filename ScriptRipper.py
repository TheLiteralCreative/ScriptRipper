import google.generativeai as genai
import os
import shutil
import pathlib
import json
from dotenv import load_dotenv

# --- 1. CONFIGURATION ---

load_dotenv()

try:
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
except KeyError:
    print("FATAL: GOOGLE_API_KEY not found. Please ensure you have a .env file.")
    exit()

# --- PATH CONFIGURATION ---
BASE_DIR = pathlib.Path(__file__).resolve().parent
SCRIPTS_DIR = BASE_DIR / "Scripts"
RIPPED_DIR = BASE_DIR / "Ripped"
OUTPUTS_DIR = BASE_DIR / "Outputs" # <-- NEW: Dedicated folder for MD files
PROMPTS_DIR = BASE_DIR / "prompts"

# --- Create necessary folders if they don't exist ---
SCRIPTS_DIR.mkdir(exist_ok=True)
RIPPED_DIR.mkdir(exist_ok=True)
OUTPUTS_DIR.mkdir(exist_ok=True)
PROMPTS_DIR.mkdir(exist_ok=True)


# --- DYNAMICALLY LOAD PROMPTS FROM FILES ---

def load_master_prompt():
    """Loads the master prompt text from its file."""
    try:
        with open(PROMPTS_DIR / "master_prompt.md", 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"FATAL: master_prompt.md not found in '{PROMPTS_DIR}'. Please create it.")
        exit()

def load_prompt_profiles():
    """Scans the prompts folder for JSON files and loads them into a dictionary."""
    profiles = {}
    json_files = list(PROMPTS_DIR.glob("*_prompts.json"))
    if not json_files:
        print(f"FATAL: No prompt profiles (*_prompts.json) found in '{PROMPTS_DIR}'.")
        exit()
        
    for prompt_file in json_files:
        profile_name = prompt_file.stem.replace('_prompts', '')
        try:
            with open(prompt_file, 'r', encoding='utf-8') as f:
                profiles[profile_name] = json.load(f)
            print(f"Successfully loaded profile: '{profile_name}'")
        except json.JSONDecodeError:
            print(f"Warning: Could not decode JSON from {prompt_file.name}. Check for syntax errors (like trailing commas). Skipping.")
        except Exception as e:
            print(f"Warning: Could not load {prompt_file.name}: {e}. Skipping.")
    return profiles

# --- 2. SCRIPT LOGIC ---

def analyze_transcript(transcript_path: pathlib.Path, selected_prompts: list, master_prompt: str):
    """Analyzes a single transcript file, generates reports, and returns True on success."""
    print("-" * 50)
    print(f"Processing transcript: {transcript_path.name}")
    
    try:
        with open(transcript_path, 'r', encoding='utf-8') as f:
            transcript_content = f.read()

        if not transcript_content.strip():
            print("Warning: Transcript file is empty. Skipping analysis.")
            return False

        initial_message = master_prompt + "\n\n## MEETING TRANSCRIPT ##\n\n" + transcript_content
        model = genai.GenerativeModel('gemini-1.5-pro-latest')
        chat = model.start_chat()

        print("Sending transcript to Gemini...")
        response = chat.send_message(initial_message)
        print(f"Model Acknowledged: {response.text.strip()}")

        base_filename = transcript_path.stem
        for i, task in enumerate(selected_prompts):
            task_name = task["task_name"]
            prompt = task["prompt"]
            print(f"\nRequesting Analysis Task {i+1}: '{task_name}'...")
            response = chat.send_message(prompt)
            
            slug = task_name.lower().replace(' ', '-').replace('&', 'and').replace('/', '')
            output_filename = f"{base_filename}_output_{i+1}_{slug}.md"
            output_path = OUTPUTS_DIR / output_filename # <-- FIXED: Save to Outputs folder
            
            print(f"Saving analysis to '{output_path}'...")
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(response.text)
        
        print("\nAnalysis successful.")
        return True

    except Exception as e:
        print(f"!!-- An error occurred while processing {transcript_path.name}: {e} --!!")
        return False

# --- 3. MAIN EXECUTION BLOCK ---

if __name__ == "__main__":
    print("Starting ScriptRipper...")
    
    MASTER_PROMPT = load_master_prompt()
    PROMPT_PROFILES = load_prompt_profiles()

    if not PROMPT_PROFILES:
        print("FATAL: No valid prompt profiles were loaded. Exiting.")
        exit()

    print(f"\nScanning for transcripts in: {SCRIPTS_DIR}")
    files_processed = 0

    for profile_name, prompt_set in PROMPT_PROFILES.items():
        input_folder = SCRIPTS_DIR / profile_name
        
        if not input_folder.is_dir():
            print(f"FYI: Input folder for profile '{profile_name}' not found at '{input_folder}'. Creating it now.")
            input_folder.mkdir(parents=True, exist_ok=True)

        print(f"\n--- Checking folder for '{profile_name}' profile ---")
        files_to_process = [f for f in input_folder.iterdir() if f.is_file()]

        if not files_to_process:
            print("No new transcripts found.")
            continue

        for transcript_file_path in files_to_process:
            success = analyze_transcript(transcript_file_path, prompt_set, MASTER_PROMPT)
            
            if success:
                # --- FIXED: Safe file moving logic ---
                destination_path = RIPPED_DIR / transcript_file_path.name
                
                # If a file with the same name already exists, add a number to it
                counter = 1
                while destination_path.exists():
                    destination_path = RIPPED_DIR / f"{transcript_file_path.stem}-{counter}{transcript_file_path.suffix}"
                    counter += 1

                print(f"Moving processed transcript to '{destination_path.name}'...")
                shutil.move(transcript_file_path, destination_path)
                files_processed += 1

    print("-" * 50)
    print(f"ScriptRipper run complete. Total files processed: {files_processed}.")
    