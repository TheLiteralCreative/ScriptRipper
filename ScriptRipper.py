import google.generativeai as genai
import os
import argparse
import re
from dotenv import load_dotenv # <-- ADDED THIS LINE

# --- 1. CONFIGURATION ---

load_dotenv() # <-- ADDED THIS LINE to load variables from .env

# The rest of the script is the same! It will now find the key loaded by dotenv.
try:
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
except KeyError:
    print("FATAL: GOOGLE_API_KEY not found.")
    print("Please ensure you have a .env file with GOOGLE_API_KEY='YOUR_KEY' in it.")
    exit()


# This is your Master Prompt. You can edit this to refine the bot's behavior.
MASTER_PROMPT = """
**## INSTRUCTION SET: TRANSCRIPT ANALYSIS PROTOCOL ##**

**1. My Role and Goal:**
You are a Professional Meeting Analyst. Your sole purpose is to act as a data extraction engine for the meeting transcript I provide. Your highest and only priority is 100% accuracy and completeness based on the provided text.

**2. Core Directives (Non-negotiable):**
* NEVER Summarize: Do not shorten, paraphrase, or summarize.
* NEVER Invent Information: If the information requested is not present, you must explicitly state: "This information was not found in the transcript."
* PRIORITIZE VERBATIM EXTRACTION: Use the exact wording from the transcript whenever possible.
* REFERENCE THE ENTIRE DOCUMENT: For every single request, re-analyze the entire transcript.

**3. The Process:**
I will provide this full set of instructions and the transcript. Acknowledge this by responding ONLY with: "Protocol acknowledged. The full transcript has been loaded. I am ready." Then, await my specific data extraction tasks.
"""

# This is your list of analysis tasks.
# You can add, remove, or edit these tasks as needed.
ANALYSIS_PROMPTS = [
    {
        "task_name": "Action Items",
        "prompt": "Identify all action items. Format the output as a Markdown table with three columns: 'Action Item', 'Assigned To', and 'Mentioned Timestamp (if available)'."
    },
    {
        "task_name": "Key Decisions",
        "prompt": "List all key decisions made during the meeting. Precede each decision with the name of the person who stated the final decision. Use a numbered list."
    },
    {
        "task_name": "Project Titan Mentions",
        "prompt": "Extract all mentions of 'Project Titan'. Provide them as direct quotes in a bulleted list, with the speaker's name before each quote."
    }
]


# --- 2. SCRIPT LOGIC ---

def create_filename_slug(text):
    """Creates a URL-friendly slug from a string."""
    text = text.lower()
    text = re.sub(r'[\s_]+', '-', text)  # Replace spaces and underscores with hyphens
    text = re.sub(r'[^\w\s-]', '', text) # Remove all non-word chars except hyphens
    return text

def analyze_transcript(transcript_filepath):
    """
    Analyzes a given transcript file using the Gemini API, saving each analysis
    to a separate output file.
    """
    print(f"Loading transcript from: {transcript_filepath}")
    try:
        with open(transcript_filepath, 'r', encoding='utf-8') as f:
            transcript_content = f.read()
    except FileNotFoundError:
        print(f"FATAL: Transcript file not found at '{transcript_filepath}'")
        return

    # Prepare the initial message for the model
    initial_message = MASTER_PROMPT + "\n\n## MEETING TRANSCRIPT ##\n\n" + transcript_content

    # Initialize the model and start a chat session
    print("Initializing Gemini 1.5 Pro model...")
    model = genai.GenerativeModel('gemini-1.5-pro-latest')
    chat = model.start_chat()

    # Send the initial instructions and transcript
    print("Sending instructions and transcript to the model...")
    response = chat.send_message(initial_message)
    print(f"Model Acknowledged: {response.text}\n" + "="*30)

    # Prepare for output files
    base_filename = os.path.splitext(os.path.basename(transcript_filepath))[0]

    # Loop through the analysis prompts sequentially
    for i, task in enumerate(ANALYSIS_PROMPTS):
        task_name = task["task_name"]
        prompt = task["prompt"]
        print(f"\nRequesting Analysis Task {i+1}: '{task_name}'...")
        
        response = chat.send_message(prompt)
        
        # Save the output to a file
        slug = create_filename_slug(task_name)
        output_filename = f"{base_filename}_output_{i+1}_{slug}.md"
        
        print(f"Saving analysis to '{output_filename}'...")
        with open(output_filename, 'w', encoding='utf-8') as f:
            f.write(response.text)
        
    print("\n" + "="*30)
    print("Analysis complete. All output files have been saved.")


# --- 3. COMMAND-LINE INTERFACE ---

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze a meeting transcript using the Gemini API.")
    parser.add_argument("filepath", help="The full path to the transcript file.")
    
    args = parser.parse_args()
    
    analyze_transcript(args.filepath)