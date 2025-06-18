import google.generativeai as genai
import os
import shutil
import pathlib
import json
from dotenv import load_dotenv
import streamlit as st
from datetime import datetime
import zipfile
import io
import re

# --- NEW LIBRARIES ---
from langchain_text_splitters import RecursiveCharacterTextSplitter
import gspread
from google.oauth2.service_account import Credentials
from markdown_it import MarkdownIt
from weasyprint import HTML

# --- 1. CONFIGURATION ---

load_dotenv()

# Configure GenAI API
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


# --- HELPER FUNCTIONS FOR FILE CONVERSION ---
def convert_md_to_txt(md_content):
    """A simple function to strip Markdown formatting for a clean text file."""
    text = re.sub(r'#{1,6} ', '', md_content)
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    text = re.sub(r'`(.*?)`', r'\1', text)
    text = re.sub(r'^- ', '', text, flags=re.MULTILINE)
    # Basic table conversion
    text = re.sub(r'\|', ' | ', text)
    return text

def convert_md_to_pdf(md_content, output_path):
    """Converts Markdown content to a PDF file."""
    try:
        md = MarkdownIt()
        html_content = md.render(md_content)
        styled_html = f"""
        <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    body {{ font-family: DejaVu Sans, sans-serif; line-height: 1.6; }}
                    h1, h2, h3 {{ color: #333; }}
                    code, pre {{ background-color: #f4f4f4; padding: 2px 4px; border-radius: 4px; font-family: "Courier New", monospace; }}
                    pre {{ padding: 10px; white-space: pre-wrap; }}
                    table {{ border-collapse: collapse; width: 100%; margin-top: 1em; }}
                    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                    th {{ background-color: #f2f2f2; }}
                </style>
            </head>
            <body>
                {html_content}
            </body>
        </html>
        """
        HTML(string=styled_html).write_pdf(output_path)
        return True
    except Exception as e:
        st.warning(f"Could not generate PDF. Error: {e}")
        return False


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
    try:
        creds_path = PROMPTS_DIR / 'credentials.json'
        if not creds_path.exists():
            st.warning("`credentials.json` not found. Activity logging will be disabled.")
            return None
        client = gspread.service_account(filename=str(creds_path))
        return client
    except Exception as e:
        st.warning(f"Could not connect to Google Sheets: {e}. Logging disabled.")
        return None

def log_activity_to_sheet(client, log_data):
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
    generated_files = []

    with log_area:
        st.info(f"Processing transcript: {transcript_name}")
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            base_filename = pathlib.Path(transcript_name).stem
            run_output_dir = OUTPUTS_DIR / f"{base_filename}_{timestamp}"

            md_dir = run_output_dir / "markdown"
            txt_dir = run_output_dir / "text"
            pdf_dir = run_output_dir / "pdf"
            md_dir.mkdir(parents=True, exist_ok=True)
            txt_dir.mkdir(parents=True, exist_ok=True)
            pdf_dir.mkdir(parents=True, exist_ok=True)
            st.success(f"Created output folder: {run_output_dir.name}")

            model = genai.GenerativeModel('gemini-1.5-pro-latest')
            request_options = {"timeout": 1200}
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=40000, chunk_overlap=2000)
            chunks = text_splitter.split_text(transcript_content)
            st.write(f"Transcript split into {len(chunks)} chunk(s).")

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

                markdown_content = final_response.text
                slug = task_name.lower().replace(' ', '-').replace('&', 'and').replace('/', '')
                output_base_name = f"{base_filename}_output_{slug}"

                # Save Markdown
                md_path = md_dir / f"{output_base_name}.md"
                with open(md_path, 'w', encoding='utf-8') as f: f.write(markdown_content)
                generated_files.append(md_path)
                st.success(f"✓ Saved {md_path.name}")

                # Save Text
                txt_content = convert_md_to_txt(markdown_content)
                txt_path = txt_dir / f"{output_base_name}.txt"
                with open(txt_path, 'w', encoding='utf-8') as f: f.write(txt_content)
                generated_files.append(txt_path)
                st.success(f"✓ Saved {txt_path.name}")

                # Save PDF
                pdf_path = pdf_dir / f"{output_base_name}.pdf"
                if convert_md_to_pdf(markdown_content, pdf_path):
                    generated_files.append(pdf_path)
                    st.success(f"✓ Saved {pdf_path.name}")

                progress_bar.progress((i + 1) / total_tasks, text=f"Task Complete: {task_name}")

            st.success("All tasks completed successfully.")
            task_names_str = ", ".join([t['task_name'] for t in selected_tasks])
            log_data = [timestamp, transcript_name, st.session_state.selected_profile, task_names_str, total_tokens_used]
            log_activity_to_sheet(gsheet_client, log_data)
            return True, total_tokens_used, generated_files, run_output_dir

        except Exception as e:
            st.error(f"An error occurred during analysis: {e}")
            return False, 0, [], None

# --- STREAMLIT GUI ---
st.set_page_config(layout="centered")
st.title("📄 ScriptRipper AI")
st.markdown("An advanced tool for deep analysis of meeting and presentation transcripts.")

# Initialize session state for the first run
if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False
    st.session_state.generated_files = []
    st.session_state.run_output_dir = None
    st.session_state.total_tokens = 0

# Load data and clients on startup
master_prompt = load_master_prompt()
prompt_profiles = load_prompt_profiles()
gsheet_client = setup_gspread_client()

if master_prompt and prompt_profiles:
    uploaded_file = st.file_uploader("Upload a transcript file (.txt)", type=['txt'], key="file_uploader")
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
                st.session_state.analysis_complete = False
                with st.spinner('Preparing analysis...'):
                    tasks_to_run = [task for task in tasks_for_profile if task['task_name'] in selected_task_names]
                    transcript_content = uploaded_file.getvalue().decode("utf-8")
                    transcript_name = uploaded_file.name

                    success, total_tokens, files, run_dir = analyze_transcript(
                        transcript_content, transcript_name, tasks_to_run, master_prompt, gsheet_client
                    )

                    if success:
                        st.session_state.analysis_complete = True
                        st.session_state.generated_files = files
                        st.session_state.run_output_dir = run_dir
                        st.session_state.total_tokens = total_tokens
                        st.rerun() # Rerun the script to display the download buttons

# Display Download Buttons After Analysis
if st.session_state.analysis_complete:
    st.divider()
    st.header("✅ Analysis Complete: Download Your Files")
    st.metric(label="Total Tokens Used for this Run", value=f"{st.session_state.total_tokens:,}")

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED, False) as zip_file:
        for file_path in st.session_state.generated_files:
            zip_file.write(file_path, arcname=file_path.relative_to(st.session_state.run_output_dir))

    st.download_button(
        label="📥 Download All (.zip)",
        data=zip_buffer.getvalue(),
        file_name=f"{st.session_state.run_output_dir.name}.zip",
        mime="application/zip",
        use_container_width=True
    )

    st.subheader("Or, download individual files:")

    md_files = sorted([f for f in st.session_state.generated_files if f.suffix == ".md"])
    txt_files = sorted([f for f in st.session_state.generated_files if f.suffix == ".txt"])
    pdf_files = sorted([f for f in st.session_state.generated_files if f.suffix == ".pdf"])

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("#### Markdown (.md)")
        for file in md_files:
            with open(file, "rb") as f:
                st.download_button(label=f"📄 {file.name}", data=f, file_name=file.name, key=f"md_{file.name}")
    with col2:
        st.markdown("#### Text (.txt)")
        for file in txt_files:
            with open(file, "rb") as f:
                st.download_button(label=f"📄 {file.name}", data=f, file_name=file.name, key=f"txt_{file.name}")
    with col3:
        st.markdown("#### PDF (.pdf)")
        for file in pdf_files:
            with open(file, "rb") as f:
                st.download_button(label=f"📄 {file.name}", data=f, file_name=file.name, key=f"pdf_{file.name}")
