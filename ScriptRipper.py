import google.generativeai as genai
import os
import shutil
import pathlib
import json
from dotenv import load_dotenv

# --- GUI Library ---
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# --- 1. CONFIGURATION (Same as before) ---

load_dotenv()

try:
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
except KeyError:
    print("FATAL: GOOGLE_API_KEY not found. Please ensure you have a .env file.")
    # We'll show this in a GUI popup instead of exiting the console.
    # exit() 

# --- PATH CONFIGURATION (Same as before) ---
BASE_DIR = pathlib.Path(__file__).resolve().parent
SCRIPTS_DIR = BASE_DIR / "Scripts"
RIPPED_DIR = BASE_DIR / "Ripped"
OUTPUTS_DIR = BASE_DIR / "Outputs"
PROMPTS_DIR = BASE_DIR / "prompts"

# Create necessary folders if they don't exist
SCRIPTS_DIR.mkdir(exist_ok=True)
RIPPED_DIR.mkdir(exist_ok=True)
OUTPUTS_DIR.mkdir(exist_ok=True)
PROMPTS_DIR.mkdir(exist_ok=True)

# --- PROMPT LOADING LOGIC (Same as before) ---

def load_master_prompt():
    # ... (same function as before)
    try:
        with open(PROMPTS_DIR / "master_prompt.md", 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        messagebox.showerror("Error", f"FATAL: master_prompt.md not found in '{PROMPTS_DIR}'. Please create it.")
        return None

def load_prompt_profiles():
    # ... (same function as before)
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

# --- ANALYSIS LOGIC (Same as before, but with logging for GUI) ---

def analyze_transcript(transcript_path: pathlib.Path, selected_tasks: list, master_prompt: str, log_callback):
    """Analyzes a single transcript file, generates reports, and logs progress."""
    log_callback("-" * 50)
    log_callback(f"Processing transcript: {transcript_path.name}")
    
    try:
        # ... (The core analysis logic is identical to our last version)
        with open(transcript_path, 'r', encoding='utf-8') as f:
            transcript_content = f.read()
        # ... etc.
        
        initial_message = master_prompt + "\n\n## MEETING TRANSCRIPT ##\n\n" + transcript_content
        model = genai.GenerativeModel('gemini-1.5-pro-latest')
        chat = model.start_chat()

        log_callback("Sending transcript to Gemini...")
        response = chat.send_message(initial_message)
        log_callback(f"Model Acknowledged: {response.text.strip()}")

        base_filename = transcript_path.stem
        for task in selected_tasks:
            task_name = task["task_name"]
            prompt = task["prompt"]
            log_callback(f"\nRequesting Analysis Task: '{task_name}'...")
            response = chat.send_message(prompt)
            
            slug = task_name.lower().replace(' ', '-').replace('&', 'and').replace('/', '')
            output_filename = f"{base_filename}_output_{slug}.md"
            output_path = OUTPUTS_DIR / output_filename
            
            log_callback(f"Saving analysis to '{output_path}'...")
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(response.text)
        
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

        # Load prompts once on startup
        self.master_prompt = load_master_prompt()
        self.prompt_profiles = load_prompt_profiles()

        if not self.master_prompt or not self.prompt_profiles:
            self.root.destroy()
            return
            
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Main button
        self.analyze_button = ttk.Button(
            main_frame,
            text="Select Transcript and Analyze",
            command=self.run_analysis_workflow
        )
        self.analyze_button.pack(pady=20, expand=True)

    def run_analysis_workflow(self):
        """Handles the entire process from file selection to analysis."""
        # Open file dialog to select a transcript
        filepath = filedialog.askopenfilename(
            title="Select a Transcript File",
            filetypes=(("Text files", "*.txt"), ("All files", "*.*"))
        )
        if not filepath:
            return # User cancelled

        transcript_path = pathlib.Path(filepath)
        
        # Determine the profile from the parent folder's name
        profile_name = transcript_path.parent.name
        if profile_name not in self.prompt_profiles:
            messagebox.showerror(
                "Profile Error",
                f"Unknown profile '{profile_name}'.\nPlease place transcript in a valid profile folder (e.g., 'meetings', 'presentations') inside 'Scripts'."
            )
            return
            
        # Get the list of all possible tasks for this profile
        all_tasks = self.prompt_profiles[profile_name]
        
        # Launch the task selection window
        self.launch_task_selection_window(transcript_path, profile_name, all_tasks)

    def launch_task_selection_window(self, transcript_path, profile_name, all_tasks):
        """Creates the popup checklist window."""
        popup = tk.Toplevel(self.root)
        popup.title("Select Tasks to Run")
        
        ttk.Label(popup, text=f"Profile: '{profile_name}'", font=("Helvetica", 12, "bold")).pack(pady=10)
        
        # Dictionary to hold the state of each checkbox
        self.task_vars = {}
        for task in all_tasks:
            task_name = task["task_name"]
            var = tk.BooleanVar(value=True) # Default to checked
            self.task_vars[task_name] = var
            ttk.Checkbutton(popup, text=task_name, variable=var).pack(anchor='w', padx=20)

        # Run Analysis button in the popup
        run_button = ttk.Button(
            popup,
            text="Run Analysis",
            command=lambda: self.execute_analysis(popup, transcript_path, all_tasks)
        )
        run_button.pack(pady=15)

    def execute_analysis(self, popup, transcript_path, all_tasks):
        """Gathers selected tasks and runs the main analysis function."""
        popup.destroy() # Close the checklist popup

        # Figure out which tasks were selected by the user
        selected_tasks = []
        for task in all_tasks:
            if self.task_vars[task["task_name"]].get():
                selected_tasks.append(task)

        if not selected_tasks:
            messagebox.showinfo("No Tasks", "No tasks were selected. Nothing to do.")
            return

        # --- Create a simple log window ---
        log_window = tk.Toplevel(self.root)
        log_window.title("Processing Log")
        log_window.geometry("600x400")
        log_text = tk.Text(log_window, wrap='word', state='disabled')
        log_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        def log_to_gui(message):
            log_text.config(state='normal')
            log_text.insert('end', message + '\n')
            log_text.config(state='disabled')
            log_text.see('end')
            self.root.update_idletasks()

        # Run the analysis
        success = analyze_transcript(transcript_path, selected_tasks, self.master_prompt, log_to_gui)

        # Move the file if successful
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
    root = tk.Tk()
    app = ScriptRipperApp(root)
    root.mainloop()