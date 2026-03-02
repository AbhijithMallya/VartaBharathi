from pydantic import BaseModel

class OPENAI(BaseModel):
    BASE_URL: str
    API_KEY: str
    MODEL: str