from pydantic import BaseModel


class Creature(BaseModel):
    name: str
    description: str
    country: str
    area: str
    aka: str
