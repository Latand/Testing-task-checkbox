from dataclasses import dataclass
from pydantic_settings import BaseSettings, SettingsConfigDict


class DBConfig(BaseSettings):
    postgres_user: str
    postgres_password: str
    postgres_db: str
    db_host: str

    def get_connection_string(self):
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.db_host}/{self.postgres_db}"

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


class ApiConfig(BaseSettings):
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_days: int = 30

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


@dataclass
class Config:
    db: DBConfig
    api: ApiConfig


def load_config():
    return Config(db=DBConfig(), api=ApiConfig())  # type: ignore
