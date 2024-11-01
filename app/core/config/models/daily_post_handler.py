from pydantic import BaseModel


class DailyPostHandlerConfig(BaseModel):
    days_to_keep: int
