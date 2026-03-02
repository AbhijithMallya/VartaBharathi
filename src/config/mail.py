from pydantic import BaseModel

class GMAIL(BaseModel):
    USERNAME: str
    PASSWORD: str