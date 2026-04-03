from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Sistema Académico API"
    app_version: str = "1.0.0"
    # SQLite para desarrollo — Semana 10: cambia esta línea a PostgreSQL
    database_url: str = "sqlite:///./academico.db"

    class Config:
        env_file = ".env"


# Instancia global — importar desde otros módulos
settings = Settings()