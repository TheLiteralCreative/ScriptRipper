import google.generativeai as genai
import os
import shutil
import pathlib
import json
from dotenv import load_dotenv
import streamlit as st
from datetime import datetime

# --- LIBRARIES ---
from langchain_text_splitters import RecursiveCharacterTextSplitter
import gspread
from google.oauth2.service_account import Credentials

# --- 1. CONFIGURATION ---

load_dotenv() 
try:
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
except KeyError:
    st.error("FATAL: GOOGLE_API_KEY environment variable not set. The application cannot start.")
    st.stop()

# --- PATH CONFIGURATION ---
BASE_DIR = pathlib.Path("./").resolve()
OUTPUTS_DIR = BASE_DIR / "Outputs"
PROMPTS_DIR = BASE_DIR / "prompts"
OUTPUTS_DIR.mkdir(exist_ok=True)
PROMPTS_DIR.mkdir(exist_ok=True)


# --- GOOGLE SHEETS CONFIGURATION ---
ACTIVITY_LOG_SHEET_NAME = "ScriptRipper_Activity_Log"


# --- DATA LOADING & SETUP FUNCTIONS ---

@st.cache_data
def load_master_prompt():
    try:
        with open(PROMPTS_DIR / "master_prompt.md", 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        st.error(f"FATAL: master_prompt.md not found in '{PROMPTS_DIR}'.")
        return None

@st.cache_data
def load_prompt_profiles():
    profiles = {}
    json_files = list(PROMPTS_DIR.glob("*_prompts.json"))
    if not json_files:
        st.error(f"FATAL: No prompt profiles found in '{PROMPTS_DIR}'.")
        return {}
    for prompt_file in json_files:
        profile_name = prompt_file.stem.replace('_prompts', '')
        try:
            with open(prompt_file, 'r', encoding='utf-8') as f:
                profiles[profile_name] = json.load(f)
        except Exception as e:
            st.warning(f"Could not load {prompt_file.name}: {e}.")
    return profiles

def setup_gspread_client():
    """Authenticates with Google and connects to the Sheets API."""
    try:
        creds_path = PROMPTS_DIR / 'credentials.json'
        if not creds_path.exists():
            st.warning("`credentials.json` not found. Logging disabled.")
            return None
        # Using the authentication method that you proved works
        client = gspread.service_account(filename=str(creds_path))
        return client
    except Exception as e:
        st.warning(f"Could not connect to Google Sheets: {e}. Logging disabled.")
        return None

def log_activity_to_sheet(client, log_data):
    """Appends a new row of data to the activity log sheet."""
    if client is None:
        return
    try:
        sheet = client.open(ACTIVITY_LOG_SHEET_NAME).sheet1
        if not sheet.get_all_values():
             sheet.append_row(["Timestamp", "Source Filename", "Profile Used", "Tasks Run", "Total Tokens Used"])
        sheet.append_row(log_data)
        st.success("Activity successfully logged to Google Sheet.")
    except Exception as e:
        st.warning(f"Failed to log activity to Google Sheet: {e}")


# --- ANALYSIS LOGIC ---
def analyze_transcript(transcript_content: str, transcript_name: str, selected_tasks: list, master_prompt: str, gsheet_client):
    log_area = st.expander("Processing Log", expanded=True)
    progress_bar = st.progress(0, text="Starting Analysis...")
    
    with log_area:
        st.info(f"Processing transcript: {transcript_name}")
        try:
            model = genai.GenerativeModel('gemini-1.5-pro-latest')
            request_options = {"timeout": 1200}
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=40000, chunk_overlap=2000)
            chunks = text_splitter.split_text(transcript_content)
            st.write(f"Transcript split into {len(chunks)} chunk(s).")

            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            base_filename = pathlib.Path(transcript_name).stem
            run_output_dir = OUTPUTS_DIR / f"{base_filename}_{timestamp}"
            run_output_dir.mkdir(exist_ok=True)
            st.success(f"Created output folder: {run_output_dir.name}")

            total_tokens_used = 0
            total_tasks = len(selected_tasks)

            for i, task in enumerate(selected_tasks):
                task_name = task["task_name"]
                original_prompt = task["prompt"]
                st.write("---")
                st.subheader(f"Running Task {i+1}/{total_tasks}: '{task_name}'")
                progress_bar.progress((i) / total_tasks, text=f"Starting Task: {task_name}")

                intermediate_results = []
                st.write(f"Analyzing {len(chunks)} chunks...")
                for j, chunk in enumerate(chunks):
                    with st.spinner(f"Analyzing chunk {j+1}/{len(chunks)}..."):
                        chunk_prompt = f"You are analyzing one small chunk of a larger document. Perform the following instruction ONLY on the provided chunk.\n\nINSTRUCTION: \"{original_prompt}\"\n\n--- CHUNK OF TRANSCRIPT ---\n{chunk}"
                        response = model.generate_content(chunk_prompt, request_options=request_options)
                        intermediate_results.append(response.text)
                        if response.usage_metadata:
                            total_tokens_used += response.usage_metadata.total_token_count
                    st.write(f"✓ Chunk {j+1}/{len(chunks)} complete.")
                
                st.write("Synthesizing final report...")
                with st.spinner(f"Creating final report for '{task_name}'..."):
                    synthesis_prompt = f"{master_prompt}\n\nYou have analyzed a document chunk by chunk. Below are the raw results. Synthesize them into a single, cohesive, de-duplicated final report that fulfills the original request.\n\nORIGINAL REQUEST: \"{original_prompt}\"\n\n--- RAW INTERMEDIATE RESULTS ---\n{''.join(intermediate_results)}"
                    final_response = model.generate_content(synthesis_prompt, request_options=request_options)
                    if final_response.usage_metadata:
                        total_tokens_used += final_response.usage_metadata.total_token_count
                
                slug = task_name.lower().replace(' ', '-').replace('&', 'and').replace('/', '')
                output_filename = f"{base_filename}_output_{slug}.md"
                output_path = run_output_dir / output_filename
                
                st.write(f"Saving final report to '{output_path}'...")
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(final_response.text)
                st.success(f"Saved '{output_filename}'")
                
                progress_bar.progress((i + 1) / total_tasks, text=f"Task Complete: {task_name}")
            
            st.success("All tasks completed successfully.")
            task_names_str = ", ".join([t['task_name'] for t in selected_tasks])
            log_data = [timestamp, transcript_name, st.session_state.selected_profile, task_names_str, total_tokens_used]
            log_activity_to_sheet(gsheet_client, log_data)
            return True, total_tokens_used
        except Exception as e:
            st.error(f"An error occurred during analysis: {e}")
            return False, 0

# --- STREAMLIT GUI ---
st.set_page_config(layout="centered")
st.title("📄 ScriptRipper AI")
st.markdown("An advanced tool for deep analysis of meeting and presentation transcripts.")

master_prompt = load_master_prompt()
prompt_profiles = load_prompt_profiles()
gsheet_client = setup_gspread_client()

if master_prompt and prompt_profiles:
    uploaded_file = st.file_uploader("Upload a transcript file (.txt)", type=['txt'])
    if uploaded_file is not None:
        profile_options = list(prompt_profiles.keys())
        selected_profile_name = st.selectbox("Select an Analysis Profile:", options=profile_options, key="selected_profile")
        
        if selected_profile_name:
            st.markdown("---")
            tasks_for_profile = prompt_profiles[selected_profile_name]
            task_names_for_profile = [task['task_name'] for task in tasks_for_profile]
            selected_task_names = st.multiselect("Select Tasks to Run:", options=task_names_for_profile, default=task_names_for_profile)
            st.markdown("---")

            if st.button("🚀 Run Analysis", use_container_width=True):
                if not selected_task_names:
                    st.warning("Please select at least one task to run.")
                else:
                    tasks_to_run = [task for task in tasks_for_profile if task['task_name'] in selected_task_names]
                    transcript_content = uploaded_file.getvalue().decode("utf-8")
                    transcript_name = uploaded_file.name
                    success, total_tokens = analyze_transcript(transcript_content, transcript_name, tasks_to_run, master_prompt, gsheet_client)
                    if success:
                        st.balloons()
                        st.metric(label="Total Tokens Used for this Run", value=f"{total_tokens:,}")
