from pydantic import BaseModel, Field
from typing import Union


class AttributeAssignment(BaseModel):
    name: str = Field(..., description="The name of the attribute")
    value: Union[str, float, int] = Field(..., description="The value of the attribute")

