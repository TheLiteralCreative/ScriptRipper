# Step 1: Use an official Python runtime as a parent image
# We'll use a slim version to keep the container lightweight.
FROM python:3.11-slim

# Step 2: Set the working directory inside the container
# All subsequent commands will be run from this directory.
WORKDIR /app

# Step 3: Copy over the dependency list first
# This is a Docker best practice. It allows Docker to cache the installed
# packages, so they don't need to be re-downloaded every time you change your code.
COPY requirements.txt .

# Step 4: Install the required packages
# The --no-cache-dir flag keeps the image size down.
RUN pip install --no-cache-dir -r requirements.txt

# Step 5: Copy the rest of your application code into the container
# This includes your ScriptRipper.py, the prompts folder, etc.
COPY . .

# Step 6: Expose the port that Streamlit runs on
# This tells Docker that the container will be listening for traffic on port 8501.
EXPOSE 8501

# Step 7: Define the command to run your application
# This is the command that will be executed when the container starts.
# It runs streamlit with settings ideal for a cloud environment.
CMD ["streamlit", "run", "ScriptRipper.py", "--server.port=8501", "--server.headless=true"]
