import os
from datetime import datetime

# Function to generate a basic Markdown header based on the file name
def generate_markdown_header(title):
    return f"# {title}\n**Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}**\n\n"

# Function to simulate processing (you can plug GPT formatting later)
def process_transcript_to_markdown(transcript_text):
    lines = transcript_text.split('\n')
    markdown_content = ''
    for line in lines:
        if line.strip():
            markdown_content += f"- {line.strip()}\n"
    return markdown_content

# Main function to convert transcript to Markdown file
def transcript_to_markdown(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        transcript = f.read()

    title = os.path.splitext(os.path.basename(input_file))[0].replace('_', ' ').title()
    header = generate_markdown_header(title)
    body = process_transcript_to_markdown(transcript)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(header)
        f.write(body)

    print(f"Markdown file created: {output_file}")

# Example usage
if __name__ == "__main__":
    input_path = "your_transcript.txt"   # <--- CHANGE this to your transcript file
    output_path = "expanded_outline.md"   # Output Markdown file
    transcript_to_markdown(input_path, output_path)
