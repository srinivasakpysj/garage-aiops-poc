from pydantic_settings import BaseSettings, SettingsConfigDict
class Settings(BaseSettings):
    database_url: str = "sqlite:///./garage_aiops.db"
    cors_origins: str = "http://localhost:5173"
    seed_demo_data: bool = True
    model_config = SettingsConfigDict(env_file="../.env", extra="ignore")
    @property
    def allowed_origins(self): return [x.strip() for x in self.cors_origins.split(",") if x.strip()]
settings=Settings()
