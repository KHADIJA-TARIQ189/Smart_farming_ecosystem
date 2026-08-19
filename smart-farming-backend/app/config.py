from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "sqlite:///./smart_farming.db"
    secret_key: str = "dev-secret-change-me"
    access_token_expire_minutes: int = 60
    algorithm: str = "HS256"

    mqtt_broker_host: str = "localhost"
    mqtt_broker_port: int = 1883
    mqtt_enabled: bool = False

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
