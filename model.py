from typing import List
from pydantic import BaseModel


class SingleDetectModel(BaseModel):
    """
    #### Single Segment Model
    """

    confidence: float = None
    detected_class: str = None
    box_xy_list: List[float] = None


class ResponseModel(BaseModel):
    """
    #### Response model for the endpoint
    """

    imageURL: str = None
    detections: List[SingleDetectModel] = None
    error: str = None
