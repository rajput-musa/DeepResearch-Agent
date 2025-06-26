from pydantic import BaseModel

class AgentConfig:
    """Configuration settings for the Max-Depth agent."""
    WRITER_MODEL = "gemini-2.5-flash-lite-preview-06-17"
    
    # Research settings
    INITIAL_SEARCH_RESULTS = 5
    DEEP_DIVE_SEARCH_RESULTS = 5
    
    # RAG settings
    CHUNKS_TO_RETRIEVE = 20
    CHUNKS_TO_USE_FOR_WRITING = 7
    
    # LLM settings
    WRITER_TEMPERATURE = 0.4
    PLANNER_TEMPERATURE = 0.2
