# ScriptRipper: AI-Powered Transcript Analysis Tool

A sophisticated, GUI-driven application designed to perform deep, multi-faceted analysis on meeting and presentation transcripts using the Google Gemini API. This tool was built to prioritize accuracy, avoid summarization shortcuts, and produce publication-quality, structured outputs.

---

## About The Project

ScriptRipper was born from the need for a reliable and accurate transcript analysis tool that respects the integrity of the source material. It is designed to overcome the common frustrations of other AI tools that may truncate content or provide unreliable summaries. By using a powerful combination of a global style guide (`master_prompt`) and specific, modular analysis tasks (`prompt profiles`), this tool provides consistent, high-quality, and detailed outputs tailored to the user's exact needs.

## Key Features

* **User-Friendly GUI:** An interactive desktop application built with Tkinter for easy file selection and task execution.
* **Multiple Analysis Profiles:** Supports different workflows for `meetings` and `presentations`, each with its own suite of specialized analysis prompts.
* **Modular Prompt System:** All prompts are stored externally in a `prompts` directory, allowing for easy editing and expansion without touching the core application logic.
* **Comprehensive Analysis Suite:** Includes over 20 distinct analysis tasks ranging from metadata extraction and content summarization to deep analysis of interpersonal dynamics and content repurposing.
* **Automated File Management:** Automatically organizes processed transcripts into a `Ripped` folder and saves all generated reports to a clean `Outputs` folder.
* **Secure API Key Handling:** Uses a `.env` file to keep your Google Gemini API key secure and out of the source code.
* **High-Quality Markdown Outputs:** Adheres to a strict master style guide to produce publication-ready `.md` files.

## Prerequisites

* Python 3.8 or higher
* A Google Gemini API Key

## Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone [Your-GitHub-Repo-URL]
    cd ScriptRipper
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate

    # For Windows
    python -m venv venv
    venv\Scripts\activate
    ```

3.  **Install required packages:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Create the environment file:**
    * Create a file named `.env` in the root of the `ScriptRipper` folder.
    * Add your Gemini API key to this file:
        ```
        GOOGLE_API_KEY="YOUR_API_KEY_HERE"
        ```

5.  **Set up directories:**
    * The script will automatically create the `Scripts`, `Outputs`, and `Ripped` folders on first run.
    * Inside the `Scripts` folder, create your profile sub-folders (e.g., `meetings`, `presentations`).

## Usage

1.  **Run the application from the terminal:**
    ```bash
    python ScriptRipper.py
    ```
2.  The ScriptRipper GUI window will appear.
3.  Click the **"Select Transcript and Analyze"** button.
4.  Navigate to your `Scripts` folder and select a transcript file from within a profile sub-folder (e.g., `Scripts/meetings/my-meeting.txt`).
5.  A new window will pop up with a checklist of all available analysis tasks for that profile.
6.  Select the desired tasks and click **"Run Analysis"**.
7.  A log window will show the real-time progress. When complete, a confirmation message will appear.
8.  Your generated Markdown files will be in the `Outputs` folder, and the original transcript will be moved to the `Ripped` folder.

## Customization

To add or edit analysis prompts, you do not need to edit `ScriptRipper.py`. Simply edit the JSON files in the `prompts` directory:

* **`master_prompt.md`**: Contains the global formatting rules for all outputs.
* **`meetings_prompts.json`**: Contains the list of analysis tasks for the `meetings` profile.
* **`presentations_prompts.json`**: Contains the list of analysis tasks for the `presentations` profile.

To add a new profile (e.g., "interviews"), simply add a corresponding folder `Scripts/interviews` and a prompt file `prompts/interviews_prompts.json`. The application will automatically detect and use it.