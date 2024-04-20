from pydantic_settings import BaseSettings
from typing import ClassVar


class Settings(BaseSettings):
    SECRET_KEY: ClassVar[str] = "secret"
    ALGORITHM: ClassVar[str] = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: ClassVar[int] = 30


settings = Settings()
