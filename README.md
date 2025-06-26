# DeepSearch-Agent

A Multi-step autonomous research agent. It takes a high-level user query, interactively refines the research scope, dynamically plans a report outline, gathers information from the web, and writes a comprehensive, cited report in Markdown

It uses Tavily API for web search/scraping and Gemini AI API for LLM.

# Live Demo

Deployed on [Hugging Spaces](https://huggingface.co/spaces/MusaR/Mini-DeepResearch-Agent)

![image](https://github.com/user-attachments/assets/8fa82b4f-c67d-49d2-b186-2a4027c0dd12)

The UI is barebones, but it works.

## Features


-   **Human-in-the-Loop:** Starts by asking clarifying questions to narrow down the user's intent.
-   **Dynamic Outline Planning:** Generates a structured report outline based on initial search results, then expands each section with key questions.
-   **Deep Research:** Performs targeted, deep-dive searches for each section of the report.
-   **Retrieval-Augmented Generation (RAG):** Chunks and embeds research content into a vector store (FAISS) to find the most relevant information for writing.
-   **Source Citation:** Meticulously cites every factual statement, linking it back to the source URL.
-   **Context-Aware Writing:** Keeps track of previously written sections to maintain flow and avoid repetition.
-   **PDF Export:** Converts the final Markdown report into a high-quality, well-formatted PDF with a table of contents using Pandoc and LaTeX.

## Getting Started

### Prerequisites

-   Python 3.8+
-   [Pandoc](https://pandoc.org/installing.html): Required for converting the markdown report to PDF.
-   A LaTeX distribution, such as [MiKTeX](https://miktex.org/download) (for Windows) or [TeX Live](https://www.tug.org/texlive/) (for macOS and Linux). This is required by Pandoc to create PDFs.

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/rajput-musa/DeepResearch-Agent.git
    cd DeepResearch-Agent
    ```

2.  **Create a virtual environment and activate it:**
    ```bash
    python -m venv venv
    venv\Scripts\activate  # On Windows
    # source venv/bin/activate  # On macOS/Linux
    ```

3.  **Install the required Python packages:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up your environment variables:**

    Create a file named `.env` in the root of the project directory and add your API keys:

    ```
    GOOGLE_API_KEY="YOUR_GOOGLE_API_KEY"
    TAVILY_API_KEY="YOUR_TAVILY_API_KEY"
    ```

    You can get your API keys from:
    -   [Google AI Studio](https://aistudio.google.com/app/apikey)
    -   [Tavily](https://tavily.com/)

### Running the Application

Once you have completed the installation and setup steps, you can run the application with the following command:

```bash
python app.py
```

This will start the Gradio web server. Open the provided URL in your browser to start using the Mini-DeepSearch-Agent.

## How it Works

1.  **Initial Topic**: You provide a research topic.
2.  **Clarification**: The agent asks clarifying questions to narrow down the scope and understand your requirements.
3.  **Research & Report Generation**: Based on your answers, the agent conducts research and generates a report section by section. You can see the progress in the UI.
4.  **Download Report**: Once the report is complete, a "Download Report as PDF" button will appear. Click it to download the report.

## Project Structure

```
.
├── .env.example
├── app.py
├── research_agent
│   ├── agent.py
│   ├── config.py
│   ├── export.py
│   ├── prompts.py
│   ├── rag_pipeline.py
│   └── tools.py
├── LICENSE
└── requirements.txt
``` 
