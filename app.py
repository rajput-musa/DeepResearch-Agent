import os
import re
import gradio as gr
from dotenv import load_dotenv

from research_agent.config import AgentConfig
from research_agent.prompts import Prompts
from research_agent.tools import AITools
from research_agent.rag_pipeline import RAGPipeline
from research_agent.agent import ResearchAgent
from research_agent.export import export_to_pdf

# Load environment variables from .env file
load_dotenv()

# --- CSS for a professional, ChatGPT-inspired look ---
CSS = """
body, .gradio-container { font-family: 'Inter', sans-serif; background-color: #343541; color: #ECECEC; }
.gradio-container { max-width: 1024px !important; margin: auto !important; padding-top: 2rem !important;}
h1 { text-align: center; font-weight: 700; font-size: 2.5em; color: white; }
.sub-header { text-align: center; color: #C5C5D2; margin-bottom: 2rem; font-size: 1.1em; }
.accordion { background-color: #40414F; border: 1px solid #565869 !important; border-radius: 8px !important; }
.accordion .gr-button { background-color: #4B4C5A; color: white; }
#chatbot { box-shadow: none !important; border: none !important; background-color: transparent !important; }
.message-bubble { background: #40414F !important; border: 1px solid #565869 !important; color: #ECECEC !important; padding: 12px !important; }
.message-bubble.user { background: #343541 !important; border: none !important; }
footer { display: none !important; }
.gr-box.gradio-container { padding: 0 !important; }
.gr-form { background-color: transparent !important; border: none !important; box-shadow: none !important; }
.gradio-container .gr-form .gr-button { display: none; } /* Hide the default submit button */
#chat-input-container { position: relative; }
#chat-input-container textarea { background-color: #40414F; color: white; border: 1px solid #565869 !important; }
#submit-button { position: absolute; right: 10px; top: 50%; transform: translateY(-50%); background: #2563EB; color: white; border-radius: 4px; padding: 4px 8px; }
"""

# --- Global Variables ---
agent_instance: ResearchAgent = None
IS_PROCESSING = False # Lock to prevent concurrent runs

def initialize_agent():
    """Initialize all components of the research agent from environment variables."""
    global agent_instance
    google_key = os.environ.get("GOOGLE_API_KEY")
    tavily_key = os.environ.get("TAVILY_API_KEY")

    if not google_key or not tavily_key:
        print("🔴 ERROR: GOOGLE_API_KEY and TAVILY_API_KEY must be set in your environment.")
        return False
    try:
        config = AgentConfig()
        prompts = Prompts()
        api_keys = {"google": google_key, "tavily": tavily_key}
        tools = AITools(config=config, api_keys=api_keys)
        rag_pipeline = RAGPipeline(config=config)
        agent_instance = ResearchAgent(config=config, tools=tools, rag=rag_pipeline, prompts=prompts)
        print("✅ Agent initialized successfully.")
        return True
    except Exception as e:
        print(f"🔴 Failed to initialize agent. Error: {str(e)}")
        return False

agent_initialized = initialize_agent()

# --- Gradio Application Logic ---
with gr.Blocks(css=CSS, theme=gr.themes.Base()) as app:
    gr.Markdown("<h1>Mini DeepSearch Agent</h1>")
    gr.Markdown("<p class='sub-header'>Your AI partner for in-depth research and analysis.</p>")

    if not agent_initialized:
        gr.Markdown("## 🔴 Agent Initialization Failed!")
        gr.Markdown("Please ensure `GOOGLE_API_KEY` and `TAVILY_API_KEY` are set in your environment and restart.")
    else:
        # State variables
        agent_state = gr.State("INITIAL")
        initial_topic_state = gr.State("")
        final_report_md = gr.State("")
        report_topic = gr.State("")

        # UI Components
        chatbot = gr.Chatbot(elem_id="chatbot", bubble_full_width=False, height=650, value=[(None, "Agent initialized. Please enter your research topic to begin.")])
        with gr.Row(elem_id="chat-input-container"):
            chat_input = gr.Textbox(placeholder="What would you like to research?", interactive=True, visible=True, show_label=False, scale=8)
            submit_button = gr.Button("Submit", elem_id="submit-button", visible=True, scale=1)
        
        with gr.Row():
            pdf_button = gr.Button("Download Report as PDF", visible=False)
            pdf_file = gr.File(label="Download PDF", visible=False)

        # --- Chat Logic ---
        def chat_step_wrapper(user_input, history, current_agent_state, topic_state):
            global IS_PROCESSING
            if IS_PROCESSING:
                # Prevent multiple requests from running at once.
                # Yielding from an empty list exits the generator cleanly.
                yield from []
                return

            IS_PROCESSING = True
            # This is the first update to the UI. It now yields 8 values, matching the outputs.
            # The two empty strings are for the final_report_md and report_topic states.
            yield history, current_agent_state, topic_state, gr.update(interactive=False), "", "", gr.update(visible=False), gr.update(visible=False)
            
            try:
                yield from chat_step(user_input, history, current_agent_state, topic_state)
            except Exception as e:
                error_message = f"An error occurred: {str(e)}"
                history.append((user_input, error_message))
                yield history, "INITIAL", "", gr.update(interactive=True, placeholder="Let's try again."), None, None, gr.update(visible=False), gr.update(visible=False)
            finally:
                IS_PROCESSING = False

        def chat_step(user_input, history, current_agent_state, topic_state):
            history = history or []
            history.append((user_input, None))
            # This first yield now includes the correct number of values.
            yield history, current_agent_state, topic_state, gr.update(interactive=False, placeholder="Thinking..."), "", "", gr.update(visible=False), gr.update(visible=False)

            if current_agent_state == "INITIAL":
                questions = agent_instance.get_clarifying_questions(user_input)
                history[-1] = (user_input, "To give you the best report, could you answer these questions for me?\n\n" + questions)
                yield history, "CLARIFYING", user_input, gr.update(interactive=True, placeholder="Provide your answers..."), "", "", gr.update(visible=False), gr.update(visible=False)

            elif current_agent_state == "CLARIFYING":
                report_generator = agent_instance.run(user_request=topic_state, user_answers=user_input)
                stream_content = ""
                for update in report_generator:
                    stream_content = update
                    history[-1] = (user_input, stream_content)
                    # The report topic state is now correctly passed as topic_state
                    yield history, "GENERATING", topic_state, gr.update(interactive=False), stream_content, topic_state, gr.update(visible=False), gr.update(visible=False)
                
                yield history, "INITIAL", "", gr.update(interactive=True, placeholder="Research complete. What's next?"), stream_content, topic_state, gr.update(visible=True), gr.update(visible=False)
        
        def export_report_to_pdf(markdown_content, topic):
            if not markdown_content or not topic: 
                gr.Warning("Cannot export an empty report.")
                return gr.update(visible=False)
            
            cleaned_topic = re.sub(r'[^\w\s-]', '', topic).strip()
            cleaned_topic = re.sub(r'[-\s]+', '_', cleaned_topic)
            pdf_filename = f"{cleaned_topic}_Report.pdf"
            success = export_to_pdf(markdown_content, pdf_filename)
            if success:
                return gr.update(value=pdf_filename, visible=True)
            else:
                gr.Warning("Failed to create PDF. Is Pandoc installed on your system?")
                return gr.update(visible=False)

        # --- Event Listeners ---
        chat_input.submit(chat_step_wrapper, [chat_input, chatbot, agent_state, initial_topic_state], [chatbot, agent_state, initial_topic_state, chat_input, final_report_md, report_topic, pdf_button, pdf_file]).then(lambda: gr.update(value=""), None, [chat_input], queue=False)
        submit_button.click(chat_step_wrapper, [chat_input, chatbot, agent_state, initial_topic_state], [chatbot, agent_state, initial_topic_state, chat_input, final_report_md, report_topic, pdf_button, pdf_file]).then(lambda: gr.update(value=""), None, [chat_input], queue=False)
        pdf_button.click(export_report_to_pdf, [final_report_md, report_topic], [pdf_file])

app.launch(debug=True, share=True) 