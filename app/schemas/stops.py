from pydantic import BaseModel
from typing import Optional
"""
id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                latitude DOUBLE PRECISION NOT NULL,
                longitude DOUBLE PRECISION NOT NULL,
                description TEXT,
                stop_code INTEGER
"""
class Stop(BaseModel):
    id: int
    name: str
    latitude: float
    longitude: float
    description: Optional[str] = None
    stop_code: Optional[int] = None

    class Config:
        from_attributes = True