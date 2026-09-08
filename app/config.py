from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SUPABASE_URL: str
    SUPABASE_KEY: str
    GROQ_API_KEY: str
    FRONTEND_URL: str

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
