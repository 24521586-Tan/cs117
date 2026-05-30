from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    SUPABASE_URL: str
    SUPABASE_ANON_KEY: str
    SUPABASE_SERVICE_ROLE_KEY: str

    # WhisperX transcription server (Colab + ngrok). Empty => mock transcript.
    COLAB_WHISPER_URL: str = ""

    # Google Gemini (meeting analysis)
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.5-flash"

    # Notion output
    NOTION_TOKEN: str = ""
    NOTION_DATABASE_ID: str = ""

    # CORS origins (comma-separated)
    ALLOWED_ORIGINS: str = "http://localhost:5173"

    @property
    def origins(self) -> list[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",")]


settings = Settings()
