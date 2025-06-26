# The system instruction now has a stronger mandate to use ONLY provided sources.
writer_system_instruction = """
You are a distinguished academic researcher. Your primary function is to synthesize information ONLY from the provided research materials. 
You MUST ignore any of your own prior knowledge and base your writing exclusively on the text provided to you.
You are meticulous about citing your sources. When you make a factual claim, you MUST cite the source.
"""

# The planner prompt is now more forceful about using the context.
planner_prompt = """
Your task is to create a detailed report outline based on the provided research topic.
You MUST respond with ONLY a valid JSON object.
The JSON object must contain a key "sections", which is a list of objects.
Each object in the "sections" list MUST have two keys: "title" and "description".

Topic: '{topic}'
Context: {context}

Example of a perfect response:
{{
  "sections": [
    {{
      "title": "Introduction to Vertical Farming",
      "description": "A brief overview of the concept, its history, and its relevance in modern agriculture."
    }},
    {{
      "title": "Key Technologies and Methods",
      "description": "An exploration of the core technologies like hydroponics, aeroponics, and LED lighting that enable vertical farming."
    }}
  ]
}}
"""

# The writer prompt is now more forceful about citations and ignoring prior knowledge.
section_writer_prompt = """
Your task is to write a single, detailed, and analytical section for a research paper on the topic of '{topic}'.
The section you are writing is: '## {section_title}'

**CRITICAL INSTRUCTIONS:**
1.  **USE ONLY PROVIDED SOURCES:** You MUST base your writing entirely on the "Research Material" provided below. Do not add any information from your own knowledge.
2.  **CITE EVERYTHING:** Every factual statement you make must be followed by an in-text citation in the format `[Source X]`, where 'X' is the number of the source from the list. If a single sentence synthesizes from multiple sources, cite them all (e.g., `[Source 1][Source 3]`).
3.  **SYNTHESIZE, DON'T SUMMARIZE:** Analyze and connect the information from different sources to build a comprehensive narrative.
4.  **FORMAL TONE:** Maintain a formal, academic tone.

**Research Material (Sources are numbered):**
---
{research}
---
Now, write the complete, cited content for the '{section_title}' section, remembering to cite every fact.
"""

# The final section prompt is also made more forceful.
final_section_writer_prompt = """
Your task is to write the {section_title} for a research paper on '{topic}'.
You MUST ONLY use the provided "Main Body Content" to write this section. Do not introduce any new information.

- For an **Introduction**, set the stage by summarizing the key themes present in the provided body content.
- For a **Conclusion**, synthesize the findings from the body content and discuss their implications.
- **At the end of the conclusion text**, add a `### Bibliography` section and list every single URL from the provided `Source URLs for Bibliography`.

**Main Body Content of the Report:**
---
{body_content}
---

**Source URLs for Bibliography:**
---
{source_urls}
---
Now, write the complete content for the '{section_title}' section.
"""

# The query writer can remain the same.
initial_research_prompt = """Generate 3 broad search queries for the topic: '{topic}'. Respond with ONLY a valid JSON object like this: {{"queries": ["query 1", "query 2"]}}"""
query_writer_prompt = """Generate {num_queries} specific search queries for the report section titled '{section_title}' about '{topic}'. Respond with ONLY a valid JSON object like this: {{"queries": ["query 1", "query 2"]}}"""

class Prompts:
    CLARIFICATION = """You are a research assistant. To provide the most relevant report on '{initial_topic}', please generate 3-4 clarifying questions for the user to help narrow down the scope, perspective, and focus. Present them as a simple, clear, numbered list."""
    BRIEF_CONSTRUCTOR = """Synthesize the user's request into a single, concise, and factual research topic string suitable for a report title. Do NOT add conversational preamble. Initial Topic: '{initial_topic}'. User's Refinements: '{user_answers}'. Synthesized Topic String:"""
    PLANNER = """Your sole task is to create a report outline for the topic: '{topic}'. Use context: {context}. You MUST respond with ONLY a valid JSON object with a "sections" key. Each section MUST have a "title" and a "description"."""
    OUTLINE_EXPANDER = """Given the report section '{section_title}: {section_description}', generate 3-5 specific sub-topics or key questions to investigate. Respond with a simple bulleted list."""
    WRITER_SYSTEM = "You are a distinguished academic researcher. Your primary function is to synthesize information ONLY from the provided research materials. You MUST ignore prior knowledge and base your writing exclusively on the text provided. You are meticulous about citing sources. Every factual statement MUST be followed by an in-text citation in the format [Source X]."
    SECTION_WRITER = """**Report So Far (for context and to avoid repetition):**\n---\n{previous_sections_context}\n---\n\nNow, using the following research material, write the next section of the report: '## {section_title}'. CITE EVERY FACT. Ensure your writing flows naturally.\n\n**Research Material for this Section:**\n---\n{research}\n---"""
    VERIFICATION_PROMPT = """
Here is a draft of a report section and the source material it was based on.
Your task is to act as a fact-checker. Read the draft and verify three things:
1. Are there any factual claims in the draft that are NOT supported by the source material?
2. Are there any misinterpretations of the source material (e.g., confusing a company's sale price with an investment)?
3. Is the draft free of future-dated or clearly speculative dates presented as fact?

If all checks pass, respond with "OK".
If you find an error, respond with a corrected version of the specific sentence or paragraph.

**DRAFT TO VERIFY:**
---
{section_text}
---

**SOURCE MATERIAL:**
---
{research_context}
---

Verification Result:
"""
