from pydantic import BaseModel, Field
from typing import List, Dict

from .config import AgentConfig
from .prompts import Prompts
from .tools import AITools
from .rag_pipeline import RAGPipeline

class Section(BaseModel):
    title: str = Field(description="The title of the report section.")
    description: str = Field(description="A detailed description of what the section will cover, including key sub-topics.")

class ResearchAgent:
    def __init__(self, config: AgentConfig, tools: AITools, rag: RAGPipeline, prompts: Prompts):
        self.config = config
        self.tools = tools
        self.rag = rag
        self.prompts = prompts

    def get_clarifying_questions(self, initial_topic: str) -> str:
        """Generates clarifying questions for the user."""
        prompt = self.prompts.CLARIFICATION.format(initial_topic=initial_topic)
        questions = self.tools.text_completion(prompt, 0.5)
        return questions

    def _construct_research_brief(self, initial_topic: str, user_answers: str) -> str:
        """Creates a detailed research brief."""
        print("\n--- Step 1: Constructing Detailed Research Brief ---")
        prompt = self.prompts.BRIEF_CONSTRUCTOR.format(initial_topic=initial_topic, user_answers=user_answers)
        brief = self.tools.text_completion(prompt, 0.2).strip()
        print(f"--> Final Research Brief: **{brief}**")
        return brief

    def _plan_and_expand_outline(self, detailed_topic: str) -> List[Section]:
        """Creates and then refines the report outline."""
        print("\n--- Step 2 & 3: Planning and Expanding Outline ---")
        print("-> Performing broad research for planning...")
        planning_research = self.tools.search([detailed_topic], self.config.INITIAL_SEARCH_RESULTS)
        planning_context = "\n\n".join(item['content'] for item in planning_research)
        
        print("-> Generating initial plan...")
        plan_prompt = self.prompts.PLANNER.format(topic=detailed_topic, context=planning_context[:20000])
        plan_response = self.tools.json_completion(plan_prompt)
        initial_sections = [Section(**s) for s in plan_response.get("sections", [])]
        if not initial_sections: return []
        
        print("-> Expanding outline for depth...")
        expanded_sections = []
        for section in initial_sections:
            expansion_prompt = self.prompts.OUTLINE_EXPANDER.format(section_title=section.title, section_description=section.description)
            sub_topics_text = self.tools.text_completion(expansion_prompt, 0.6)
            section.description += "\n\nKey areas to investigate:\n" + sub_topics_text
            expanded_sections.append(section)
            print(f"--> Refined section: {section.title}")
        return expanded_sections

    def _write_and_verify_section(self, detailed_topic: str, section: Section, previous_sections_context: str) -> tuple[str, dict, list]:
        """Runs the full RAG and writing process for a single section."""
        print(f"\n--- Processing Section: {section.title} ---")
        
        section_queries = [f"{detailed_topic} - {section.title}"] + section.description.split('\n')[-4:]
        section_queries = [q[:400] for q in section_queries if q]
        section_research = self.tools.search(section_queries, self.config.DEEP_DIVE_SEARCH_RESULTS)
        
        top_chunks_with_meta = self.rag.run(section_research, section.description, self.config.CHUNKS_TO_USE_FOR_WRITING)
        
        if not top_chunks_with_meta:
            return f"## {section.title}\n\nNo relevant research material could be found for this section.\n\n", {}, []
            
        context_for_llm, cited_sources = "", {}
        for i, item in enumerate(top_chunks_with_meta):
            source_url = item['source']
            context_for_llm += f"Source [{i+1}]: {item['content']}\n\n"
            cited_sources[i+1] = source_url

        writer_prompt = f"{self.prompts.WRITER_SYSTEM}\n\n{self.prompts.SECTION_WRITER.format(topic=detailed_topic, section_title=section.title, previous_sections_context=previous_sections_context, research=context_for_llm)}"
        
        draft_content = self.tools.text_completion(writer_prompt, self.config.WRITER_TEMPERATURE)
        
        return draft_content, cited_sources, section_queries

    def run(self, user_request: str, user_answers: str):
        """The main orchestrator that runs the full agent process."""
        # --- Step 1: Construct Brief ---
        detailed_topic = self._construct_research_brief(user_request, user_answers)
        yield f"### Research Brief Constructed\n> {detailed_topic}\n\n---\n"

        # --- Step 2: Plan Outline ---
        yield "### Generating Report Outline..."
        sections = self._plan_and_expand_outline(detailed_topic)
        if not sections:
            yield "# Report Generation Failed\nCould not create a valid report outline."
            return
            
        plan_text = "### Report Outline\n"
        for i, section in enumerate(sections):
            plan_text += f"{i+1}. **{section.title}**\n"
        yield plan_text + "\n---\n"

        # --- Step 3: Write Report ---
        full_report_text = f"# Deep Research Report: {detailed_topic}\n\n"
        master_bibliography = {}
        citation_master_counter = 1

        for i, section in enumerate(sections):
            yield f"### Processing Section {i+1}/{len(sections)}: {section.title}...\n"
            
            section_content, section_sources, section_queries = self._write_and_verify_section(detailed_topic, section, full_report_text)
            
            # Yield the search queries used for this section
            queries_md = "\n".join(f"- `{q}`" for q in section_queries)
            yield f"-> Searching with queries:\n{queries_md}\n"

            # Remap citations
            final_section_text = section_content
            for local_num, url in section_sources.items():
                if url not in master_bibliography:
                    master_bibliography[url] = citation_master_counter
                    citation_master_counter += 1
                master_num = master_bibliography[url]
                final_section_text = final_section_text.replace(f"[Source {local_num}]", f"[{master_num}]")

            full_report_text += final_section_text + "\n\n"
            yield full_report_text # This yields the cumulative report
            
        # --- Step 4: Final Bibliography ---
        full_report_text += "## Master Bibliography\n\n"
        for url, num in sorted(master_bibliography.items(), key=lambda item: item[1]):
            full_report_text += f"[{num}] {url}\n"
            
        yield full_report_text
