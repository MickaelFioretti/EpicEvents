from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SECRET_KEY = "secret"
    ALGORITHM = "HS256"


settings = Settings()
