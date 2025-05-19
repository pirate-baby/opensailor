from enum import Enum
import re
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import List, Any, Optional
from webapp.schemas.attributes import AttributeAssignment
from django.core.files.uploadedfile import UploadedFile
from webapp.models.user import User
class VesselFilterOperator(str, Enum):
    eq = "eq"
    ne = "ne"
    gt = "gt"
    gte = "gte"
    lt = "lt"
    lte = "lte"

class VesselFilter(BaseModel):
    """filtering for a vessel. Something like `beam is greater or equal to 10 feet`"""
    attribute: str = Field(..., description="The attribute to filter on")
    value: Any = Field(..., description="The value to filter on")
    operator: VesselFilterOperator = Field(..., description="The operator to use for the filter")

class VesselListRequest(BaseModel):
    filters: List[VesselFilter]
    order_by: List[str] = Field(default_factory=lambda: [])
    page: int = Field(default=1, description="The page number to return")
    page_size: int = Field(default=25, ge=1, le=100, description="The number of items per page")

class VesselCreateRequest(BaseModel):
    """create a new vessel"""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    user: User = Field(..., description="The user creating the vessel")
    model_config = ConfigDict(arbitrary_types_allowed=True)
    sailboat: Optional[int] = Field(None, description="The sailboat to create the vessel for, if exists")
    make: Optional[str] = Field(None, description="The make of the sailboat to create the vessel for, if it doesn't exist")
    sailboat_name: Optional[str] = Field(None, description="The name of the sailboat to create the vessel for, if exists")
    hull_identification_number: str = Field(..., description="The hull identification number of the vessel")
    year_built: int = Field(int, description="The year the vessel was built")
    name: str = Field(..., description="The name of the vessel")
    attributes: List[AttributeAssignment] = Field(..., description="The attributes to create the vessel with")
    images: List[UploadedFile] = Field(..., description="The images to create the vessel with")

    @field_validator("hull_identification_number")
    def validate_hull_identification_number(cls, v):
        """alphanumeric only"""
        if not re.match(r'^[a-zA-Z0-9]+$', v):
            raise ValueError("Hull identification number must be alphanumeric")
        return v

    @field_validator("year_built")
    def validate_year_built(cls, v):
        """must be between 1800 and next year"""
        if v < 1800 or v > datetime.now().year + 1:
            raise ValueError("Year built must be between 1800 and the current year")
        return v
