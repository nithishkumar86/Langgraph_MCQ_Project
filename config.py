from pydantic_settings import BaseSettings,SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env',env_file_encoding='utf-8')
    GROQ_API_KEY: str
    LLM: str
    
    LANGSMITH_API_KEY: str
    LANGSMITH_TRACING:bool
    LANGSMITH_ENDPOINT: str
    LANGCHAIN_PROJECT: str