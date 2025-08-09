from typing import List, Optional
from pydantic import BaseModel, Field


class EventTime(BaseModel):
    """Represents a single event occurrence with date and time span.

    Dates and times are strings to mirror the source JSON exactly.
    """

    date: str = Field(..., description="Date in MM/DD/YYYY format")
    start_time: str = Field(..., description="Start time in HH:MM 24-hour format")
    end_time: str = Field(..., description="End time in HH:MM 24-hour format")


class Event(BaseModel):
    """Primary event model matching the structure in data/events.json."""

    id: str
    title: str = ""
    times: List[EventTime]
    type: str
    camp: str
    campurl: Optional[str] = ""
    location: str
    description: str


class RecommendationRequest(BaseModel):
    """Request body for recommendations."""

    query: str
    max_results: int = 5


class RecommendationResponse(BaseModel):
    """Response body for recommendations."""

    events: List[Event]
    query: str
    processing_time_ms: float
    rationale: Optional[str] = None


