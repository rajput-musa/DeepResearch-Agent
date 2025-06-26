import os
import subprocess
import shutil

def is_tool_installed(name):
    """Check whether `name` is on PATH and marked as executable."""
    return shutil.which(name) is not None

def export_to_pdf(markdown_content: str, output_filename: str):
    # Pandoc and LaTeX check
    if not is_tool_installed("pandoc"):
        print("🔴 ERROR: Pandoc is not installed or not in your system's PATH.")
        print("Please install it from https://pandoc.org/installing.html")
        return False
    
    # Simple check for a latex distribution, might not be foolproof
    if not is_tool_installed("xelatex"):
        print("🔴 ERROR: A LaTeX distribution (like MiKTeX or TeX Live) is not installed or not in your system's PATH.")
        print("MiKTeX (Windows): https://miktex.org/download")
        print("TeX Live (Multi-platform): https://www.tug.org/texlive/")
        return False

    markdown_filename = "temp_report.md"
    print(f"-> Exporting report to {output_filename} via LaTeX...")
    
    # 1. Save the final markdown to a temporary file
    with open(markdown_filename, "w", encoding="utf-8") as f:
        f.write(markdown_content)
        
    command = [
        "pandoc",
        markdown_filename,
        "-o", output_filename,
        "--from", "markdown",
        "--to", "pdf",
        "--pdf-engine", "xelatex",
        "-V", "geometry:margin=1in",
        "-V", "mainfont:Latin Modern Roman", # Use a standard, high-quality LaTeX font
        "-V", "sansfont:Latin Modern Sans", # Define a sans-serif font for headings
        "-V", "monofont:Latin Modern Mono", # Define a monospaced font for code
        "-V", "fontsize=12pt",
        "--toc",
    ]
    
    try:
        # 3. Run the command
        process = subprocess.run(command, check=True, capture_output=True, text=True)
        print(f"-> Successfully created PDF: {output_filename}")
        os.remove(markdown_filename)
        return True
    except FileNotFoundError:
        print("🔴 ERROR: Pandoc or LaTeX command not found.")
        print("Please ensure both Pandoc and a LaTeX distribution (like MiKTeX/TeX Live) are installed and in your system's PATH.")
        os.remove(markdown_filename)
        return False
    except subprocess.CalledProcessError as e:
        print("--- PANDOC ERROR ---")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        print("--------------------")
        os.remove(markdown_filename)
        return False 