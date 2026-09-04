from pydantic import BaseModel


class HealthData(BaseModel):
    status: str
    service: str
    database: str

