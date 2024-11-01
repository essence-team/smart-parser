from pydantic_settings import BaseSettings


class TelethonConfig(BaseSettings):
    api_id: str
    api_hash: str
    session_name: str
    phone_number: str
