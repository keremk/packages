from pydantic import BaseModel, Field
import uuid
from typing import Optional

class Package(BaseModel):
    package_id: str
    width: float
    height: float
    length: float

    class Config:
        schema_extra = {
            "example": {
                "package_id": "123e4567-e89b-12d3-a456-426614174000",
                "width": 10.5,
                "height": 20.0,
                "length": 15.5
            }
        }
