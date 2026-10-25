from functools import lru_cache

from openai import OpenAI

from app.config import settings


@lru_cache
def get_openai() -> OpenAI:
    return OpenAI(api_key=settings.openai_api_key)
