import google.generativeai as genai
import os
import shutil
import pathlib
import json
from dotenv import load_dotenv

# --- GUI Library ---
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# --- 1. CONFIGURATION ---

load_dotenv()

try:
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
except KeyError:
    # This case is now handled at GUI startup
    pass

# --- PATH CONFIGURATION ---
BASE_DIR = pathlib.Path(__file__).resolve().parent
SCRIPTS_DIR = BASE_DIR / "Scripts"
RIPPED_DIR = BASE_DIR / "Ripped"
OUTPUTS_DIR = BASE_DIR / "Outputs"
PROMPTS_DIR = BASE_DIR / "prompts"

# --- Create necessary folders if they don't exist ---
SCRIPTS_DIR.mkdir(exist_ok=True)
RIPPED_DIR.mkdir(exist_ok=True)
OUTPUTS_DIR.mkdir(exist_ok=True)
PROMPTS_DIR.mkdir(exist_ok=True)


# --- PROMPT LOADING LOGIC ---

def load_master_prompt():
    try:
        with open(PROMPTS_DIR / "master_prompt.md", 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        messagebox.showerror("Error", f"FATAL: master_prompt.md not found in '{PROMPTS_DIR}'. Please create it.")
        return None

def load_prompt_profiles():
    profiles = {}
    json_files = list(PROMPTS_DIR.glob("*_prompts.json"))
    if not json_files:
        messagebox.showerror("Error", f"FATAL: No prompt profiles (*_prompts.json) found in '{PROMPTS_DIR}'.")
        return {}
    for prompt_file in json_files:
        profile_name = prompt_file.stem.replace('_prompts', '')
        try:
            with open(prompt_file, 'r', encoding='utf-8') as f:
                profiles[profile_name] = json.load(f)
        except Exception as e:
            messagebox.showwarning("Warning", f"Could not load {prompt_file.name}: {e}. Skipping.")
    return profiles

# --- ANALYSIS LOGIC ---

def analyze_transcript(transcript_path: pathlib.Path, selected_tasks: list, master_prompt: str, log_callback, progress_callback):
    """Analyzes a single transcript file, generates reports, and logs progress."""
    log_callback("-" * 50)
    log_callback(f"Processing transcript: {transcript_path.name}")
    
    try:
        with open(transcript_path, 'r', encoding='utf-8') as f:
            transcript_content = f.read()

        if not transcript_content.strip():
            log_callback("Warning: Transcript file is empty. Skipping analysis.")
            return False

        initial_message = master_prompt + "\n\n## MEETING TRANSCRIPT ##\n\n" + transcript_content
        model = genai.GenerativeModel('gemini-1.5-pro-latest')
        chat = model.start_chat()

        log_callback("Sending transcript to Gemini... (This may take several minutes)")
        request_options = {"timeout": 1800} # 30 minutes

        response = chat.send_message(initial_message, request_options=request_options)
        log_callback(f"Model Acknowledged: {response.text.strip()}")

        base_filename = transcript_path.stem
        total_tasks = len(selected_tasks)
        for i, task in enumerate(selected_tasks):
            task_name = task["task_name"]
            prompt = task["prompt"]
            log_callback(f"\nRequesting Analysis Task {i+1}/{total_tasks}: '{task_name}'...")
            response = chat.send_message(prompt, request_options=request_options)
            
            slug = task_name.lower().replace(' ', '-').replace('&', 'and').replace('/', '')
            output_filename = f"{base_filename}_output_{slug}.md"
            output_path = OUTPUTS_DIR / output_filename
            
            log_callback(f"Saving analysis to '{output_path}'...")
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(response.text)
            
            progress_callback((i + 1) / total_tasks * 100)
        
        log_callback("\nAnalysis successful.")
        return True

    except Exception as e:
        log_callback(f"!!-- An error occurred: {e} --!!")
        messagebox.showerror("Analysis Error", str(e))
        return False

# --- GUI APPLICATION CLASS ---

class ScriptRipperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ScriptRipper")
        self.root.geometry("400x150")

        self.master_prompt = load_master_prompt()
        self.prompt_profiles = load_prompt_profiles()

        if not self.master_prompt or not self.prompt_profiles:
            self.root.destroy()
            return
            
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        self.analyze_button = ttk.Button(
            main_frame,
            text="Select Transcript and Analyze",
            command=self.run_analysis_workflow
        )
        self.analyze_button.pack(pady=20, expand=True)

    def run_analysis_workflow(self):
        filepath = filedialog.askopenfilename(
            title="Select a Transcript File",
            initialdir=SCRIPTS_DIR,
            filetypes=(("Text files", "*.txt"), ("All files", "*.*"))
        )
        if not filepath:
            return

        transcript_path = pathlib.Path(filepath)
        
        try:
            profile_name = transcript_path.relative_to(SCRIPTS_DIR).parts[0]
        except ValueError:
             profile_name = None

        if profile_name not in self.prompt_profiles:
            messagebox.showerror(
                "Profile Error",
                f"Unknown or invalid profile folder.\nPlease select a transcript from within a valid profile folder (e.g., 'meetings', 'presentations') inside your '{SCRIPTS_DIR.name}' directory."
            )
            return
            
        all_tasks = self.prompt_profiles[profile_name]
        self.launch_task_selection_window(transcript_path, profile_name, all_tasks)

    def launch_task_selection_window(self, transcript_path, profile_name, all_tasks):
        popup = tk.Toplevel(self.root)
        popup.title("Select Tasks to Run")
        
        ttk.Label(popup, text=f"Profile: '{profile_name}'", font=("Helvetica", 12, "bold")).pack(pady=10)
        
        self.task_vars = {}
        for task in all_tasks:
            task_name = task["task_name"]
            var = tk.BooleanVar(value=True)
            self.task_vars[task_name] = var
            ttk.Checkbutton(popup, text=task_name, variable=var).pack(anchor='w', padx=20)
            
        run_button = ttk.Button(
            popup,
            text="Run Analysis",
            command=lambda: self.execute_analysis(popup, transcript_path, all_tasks)
        )
        run_button.pack(pady=15)

    def execute_analysis(self, popup, transcript_path, all_tasks):
        popup.destroy()
        selected_tasks = []
        for task in all_tasks:
            if self.task_vars[task["task_name"]].get():
                selected_tasks.append(task)
        if not selected_tasks:
            messagebox.showinfo("No Tasks", "No tasks were selected. Nothing to do.")
            return

        log_window = tk.Toplevel(self.root)
        log_window.title("Processing Log")
        log_window.geometry("600x450")
        
        log_frame = ttk.Frame(log_window)
        log_frame.pack(fill='both', expand=True, padx=10, pady=10)

        log_text = tk.Text(log_frame, wrap='word', state='disabled', bg="black", fg="white", font=("Courier", 12))
        log_text.pack(fill='both', expand=True)
        
        progress_var = tk.DoubleVar()
        progressbar = ttk.Progressbar(log_frame, variable=progress_var, maximum=100)
        progressbar.pack(fill='x', pady=(5, 0))

        def log_to_gui(message):
            log_text.config(state='normal')
            log_text.insert('end', message + '\n')
            log_text.config(state='disabled')
            log_text.see('end')
            self.root.update_idletasks()
            
        def progress_update_gui(value):
            progress_var.set(value)
            self.root.update_idletasks()

        success = analyze_transcript(transcript_path, selected_tasks, self.master_prompt, log_to_gui, progress_update_gui)
        
        if success:
            destination_path = RIPPED_DIR / transcript_path.name
            counter = 1
            while destination_path.exists():
                destination_path = RIPPED_DIR / f"{transcript_path.stem}-{counter}{transcript_path.suffix}"
                counter += 1
            log_to_gui(f"\nMoving processed transcript to '{destination_path.name}'...")
            shutil.move(transcript_path, destination_path)
        
        messagebox.showinfo("Complete", "Analysis run is complete. Check the Outputs folder and the log window for details.")
        log_window.title("Processing Log (Complete)")


# --- MAIN EXECUTION BLOCK ---
if __name__ == "__main__":
    if "GOOGLE_API_KEY" not in os.environ:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Startup Error", "FATAL: GOOGLE_API_KEY not found in .env file.")
    else:
        root = tk.Tk()
        app = ScriptRipperApp(root)
        root.mainloop()