import json
from typing import List, Dict, Any

import google.generativeai as genai
from google.generativeai.types import GenerationConfig, HarmCategory, HarmBlockThreshold
from tavily import TavilyClient

from .config import AgentConfig

class AITools:
    def __init__(self, config: AgentConfig, api_keys: Dict[str, str]):
        self.config = config
        genai.configure(api_key=api_keys['google'])
        self.tavily = TavilyClient(api_key=api_keys['tavily'])

    def text_completion(self, prompt: str, temperature: float) -> str:
        model = genai.GenerativeModel(self.config.WRITER_MODEL)
        generation_config = GenerationConfig(temperature=temperature)
        safety_settings = [
            {"category": HarmCategory.HARM_CATEGORY_HATE_SPEECH, "threshold": HarmBlockThreshold.BLOCK_ONLY_HIGH},
            {"category": HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT, "threshold": HarmBlockThreshold.BLOCK_ONLY_HIGH},
            {"category": HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT, "threshold": HarmBlockThreshold.BLOCK_ONLY_HIGH},
            {"category": HarmCategory.HARM_CATEGORY_HARASSMENT, "threshold": HarmBlockThreshold.BLOCK_ONLY_HIGH},
        ]
        try:
            response = model.generate_content(prompt, generation_config=generation_config, safety_settings=safety_settings)
            return response.text
        except Exception as e: return f"[Error: LLM call failed. {e}]"

    def json_completion(self, prompt: str) -> Dict[str, Any]:
        model = genai.GenerativeModel(self.config.WRITER_MODEL)
        try:
            response = model.generate_content(prompt, generation_config=GenerationConfig(response_mime_type="application/json", temperature=self.config.PLANNER_TEMPERATURE))
            return json.loads(response.text)
        except Exception as e:
            print(f"Warning: Failed to parse JSON. Error: {e}")
            return {}

    def search(self, queries: List[str], num_results: int) -> List[Dict[str, str]]:
        research = []
        print(f"-> Gathering research for {len(queries)} queries...")
        for query in queries:
            if not query: continue # Skip empty queries
            try:
                response = self.tavily.search(query=query, search_depth="advanced", max_results=num_results, include_raw_content=True)
                for result in response['results']:
                    if result.get('content') and result.get('url'):
                        research.append({"content": result['content'], "source": result['url']})
            except Exception as e: print(f"Tavily search failed for '{query}': {e}")
        return research 