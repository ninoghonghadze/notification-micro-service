from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MONGODB_URL: str
    RABBITMQ_URL: str
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_REGION: str
    SES_SENDER_EMAIL: str

    class Config:
        env_file = ".env"
settings = Settings()