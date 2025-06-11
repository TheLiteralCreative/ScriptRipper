import google.generativeai as genai
import os
import pathlib
import json
from dotenv import load_dotenv
import streamlit as st

# --- NEW LIBRARY FOR TEXT CHUNKING ---
from langchain_text_splitters import RecursiveCharacterTextSplitter

# --- 1. CONFIGURATION ---

# This function checks for Google Colab's secrets manager first, then a local .env file.
def load_api_key():
    try:
        from google.colab import userdata
        print("Loading API Key from Colab Secrets...")
        return userdata.get('GOOGLE_API_KEY')
    except (ImportError, KeyError):
        print("Could not find Colab secrets. Falling back to local .env file.")
        load_dotenv()
        return os.environ.get("GOOGLE_API_KEY")

# Configure GenAI API
api_key = load_api_key()
if not api_key:
    st.error("FATAL: GOOGLE_API_KEY not found. Please set it in Colab Secrets or a local .env file.")
    st.stop()
genai.configure(api_key=api_key)


# --- PATH CONFIGURATION ---
# In Colab, we work relative to the content directory
BASE_DIR = pathlib.Path("./").resolve()
OUTPUTS_DIR = BASE_DIR / "Outputs"
PROMPTS_DIR = BASE_DIR / "prompts"
OUTPUTS_DIR.mkdir(exist_ok=True)
PROMPTS_DIR.mkdir(exist_ok=True)


# --- DATA LOADING FUNCTIONS ---
@st.cache_data
def load_master_prompt():
    try:
        with open(PROMPTS_DIR / "master_prompt.md", 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        st.error(f"FATAL: master_prompt.md not found in '{PROMPTS_DIR}'. Please create it.")
        return None

@st.cache_data
def load_prompt_profiles():
    profiles = {}
    json_files = list(PROMPTS_DIR.glob("*_prompts.json"))
    if not json_files:
        st.error(f"FATAL: No prompt profiles (*_prompts.json) found in '{PROMPTS_DIR}'.")
        return {}
    for prompt_file in json_files:
        profile_name = prompt_file.stem.replace('_prompts', '')
        try:
            with open(prompt_file, 'r', encoding='utf-8') as f:
                profiles[profile_name] = json.load(f)
        except Exception as e:
            st.warning(f"Could not load {prompt_file.name}: {e}. Skipping.")
    return profiles

# --- ANALYSIS LOGIC ---
def analyze_transcript(transcript_content: str, transcript_name: str, selected_tasks: list, master_prompt: str):
    log_area = st.expander("Processing Log", expanded=True)
    progress_bar = st.progress(0)
    
    with log_area:
        st.info(f"Processing transcript: {transcript_name}")

        try:
            model = genai.GenerativeModel('gemini-1.5-pro-latest')
            request_options = {"timeout": 1200}
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=40000, chunk_overlap=2000)
            chunks = text_splitter.split_text(transcript_content)
            st.write(f"Transcript split into {len(chunks)} chunk(s).")

            base_filename = pathlib.Path(transcript_name).stem
            total_tasks = len(selected_tasks)

            for i, task in enumerate(selected_tasks):
                task_name = task["task_name"]
                original_prompt = task["prompt"]
                st.write("---")
                st.subheader(f"Running Task {i+1}/{total_tasks}: '{task_name}'")
                
                intermediate_results = []
                st.write(f"Analyzing {len(chunks)} chunks...")
                for j, chunk in enumerate(chunks):
                    chunk_prompt = f"You are analyzing one small chunk of a larger document. Perform the following instruction ONLY on the provided chunk.\n\nINSTRUCTION: \"{original_prompt}\"\n\n--- CHUNK OF TRANSCRIPT ---\n{chunk}"
                    with st.spinner(f"Analyzing chunk {j+1}/{len(chunks)}..."):
                        response = model.generate_content(chunk_prompt, request_options=request_options)
                        intermediate_results.append(response.text)
                    st.write(f"✓ Chunk {j+1}/{len(chunks)} complete.")

                st.write("Synthesizing final report...")
                synthesis_prompt = f"{master_prompt}\n\nYou have analyzed a document chunk by chunk. Below are the raw results. Synthesize them into a single, cohesive, de-duplicated final report that fulfills the original request.\n\nORIGINAL REQUEST: \"{original_prompt}\"\n\n--- RAW INTERMEDIATE RESULTS ---\n{''.join(intermediate_results)}"
                
                with st.spinner(f"Creating final report for '{task_name}'..."):
                    final_response = model.generate_content(synthesis_prompt, request_options=request_options)

                slug = task_name.lower().replace(' ', '-').replace('&', 'and').replace('/', '')
                output_filename = f"{base_filename}_output_{slug}.md"
                output_path = OUTPUTS_DIR / output_filename
                
                st.write(f"Saving final report to '{output_path}'...")
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(final_response.text)
                st.success(f"Saved '{output_filename}'")
                
                progress_bar.progress((i + 1) / total_tasks)
            
            st.success("All tasks completed successfully.")
            return True

        except Exception as e:
            st.error(f"An error occurred during analysis: {e}")
            return False

# --- STREAMLIT GUI ---
st.set_page_config(layout="centered")
st.title("📄 ScriptRipper AI")
st.markdown("An advanced tool for deep analysis of meeting and presentation transcripts.")

master_prompt = load_master_prompt()
prompt_profiles = load_prompt_profiles()

if master_prompt and prompt_profiles:
    uploaded_file = st.file_uploader("Upload a transcript file (.txt)", type=['txt'])
    if uploaded_file is not None:
        profile_options = list(prompt_profiles.keys())
        selected_profile_name = st.selectbox("Select an Analysis Profile:", options=profile_options)
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
                    analyze_transcript(transcript_content, transcript_name, tasks_to_run, master_prompt)
                    st.balloons()