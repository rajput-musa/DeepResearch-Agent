# Mini-DeepSearch-Agent

Mini-DeepSearch-Agent is a Python-based research agent that uses AI to conduct in-depth research and generate comprehensive reports. It takes a research topic, asks clarifying questions, and then performs multi-step research to create a detailed report that can be downloaded as a PDF.

This agent is built using Gradio for the user interface, and leverages Google's Gemini models for language understanding and generation, and the Tavily API for web searches.

## Features

-   **Interactive Research Process**: The agent starts by asking clarifying questions to better understand the user's request.
-   **Multi-Step Research**: It formulates a research brief, creates a plan, and expands on an outline to cover the topic in depth.
-   **RAG Pipeline**: Utilizes a Retrieval-Augmented Generation (RAG) pipeline to gather and process information.
-   **PDF Report Generation**: The final report can be exported as a professional-looking PDF document.
-   **Web-based UI**: A simple and clean user interface built with Gradio.

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
    -   [Google AI Studio](https://makersuite.google.com/app/apikey)
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