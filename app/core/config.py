from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # PostGIS
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    
    # Redis
    REDIS_HOST: str
    REDIS_PORT: int
    
    # Kafka
    KAFKA_BOOTSTRAP_SERVERS: str
    
    # MongoDB
    MONGO_URI: str
    
    # Elasticsearch
    ELASTICSEARCH_URL: str

    # Pydantic v2 Config
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()