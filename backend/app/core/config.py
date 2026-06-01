from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    SUPABASE_URL: str
    SUPABASE_ANON_KEY: str
    SUPABASE_SERVICE_ROLE_KEY: str

    # Local faster-whisper transcription. WHISPER_MODEL="mock" => skip ASR, return
    # a mock transcript (useful for testing Gemini + Notion without loading a model).
    WHISPER_MODEL: str = "large-v2"          # whisper model size, or "mock"
    WHISPER_DEVICE: str = "auto"             # auto | cuda | cpu
    WHISPER_COMPUTE_TYPE: str = "int8_float16"  # cuda: float16/int8_float16; cpu forced to int8

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
