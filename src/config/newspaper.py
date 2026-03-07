from pydantic import BaseModel

class UdayavaniConfig(BaseModel):
    BASE_URL: str = "https://www.tradingref.com/udayavani"
    LANGUAGE: str = "kannada"
    EDITION: str = "Manipal Edition"
    NEWSPAPER_NAME: str = "Udayavani"

class NewspaperSettings(BaseModel):
    udayavani: UdayavaniConfig = UdayavaniConfig()
    NEWS_DIR: str = "news"

newspaper_settings = NewspaperSettings()
