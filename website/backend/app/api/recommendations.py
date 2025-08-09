from __future__ import annotations

import time
from fastapi import APIRouter, HTTPException

from app.models.event import RecommendationRequest, RecommendationResponse
from app.services.recommendation_service import RecommendationService


router = APIRouter()
service = RecommendationService()


@router.post("/recommend", response_model=RecommendationResponse)
def post_recommend(request: RecommendationRequest) -> RecommendationResponse:
    if not request.query or not request.query.strip():
        raise HTTPException(status_code=400, detail="Query must not be empty")

    start = time.time()
    try:
        events = service.get_recommendations(request.query, request.max_results)
    except Exception as exc:
        # For Phase 4, return a generic 503 and a helpful message
        raise HTTPException(status_code=503, detail="Recommendation service unavailable") from exc

    elapsed_ms = (time.time() - start) * 1000.0
    return RecommendationResponse(events=events, query=request.query, processing_time_ms=elapsed_ms)


@router.get("/events/{event_id}")
def get_event(event_id: str):
    for ev in service.events:
        if ev.id == event_id:
            return ev
    raise HTTPException(status_code=404, detail="Event not found")


