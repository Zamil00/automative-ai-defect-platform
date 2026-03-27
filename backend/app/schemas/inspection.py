from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


DefectLabel = Literal['OK', 'Scratch', 'Crack', 'Stain', 'Dent']
RiskLevel = Literal['low', 'medium', 'high']
ReviewStatus = Literal['pending', 'approved', 'rejected']


class AnalysisMetrics(BaseModel):
    brightness_mean: float
    brightness_std: float
    edge_density: float
    dark_spot_ratio: float
    hotspot_ratio: float
    contour_count: int
    largest_contour_ratio: float
    texture_score: float
    mask_pixel_ratio: float
    defect_score: float


class InspectionCreateResponse(BaseModel):
    id: str
    filename: str
    predicted_label: DefectLabel
    confidence: float = Field(..., ge=0.0, le=1.0)
    risk_level: RiskLevel
    needs_manual_review: bool
    summary: str
    model_version: str
    original_image_path: str
    overlay_image_path: str
    mask_image_path: str
    reviewer_status: ReviewStatus
    metrics: AnalysisMetrics
    created_at: datetime


class InspectionRow(BaseModel):
    id: str
    filename: str
    predicted_label: str
    confidence: float
    risk_level: str
    needs_manual_review: bool
    reviewer_status: str
    reviewed_by: str | None = None
    reviewer_note: str | None = None
    created_at: datetime
    model_version: str


class InspectionReviewRequest(BaseModel):
    reviewer_status: ReviewStatus
    reviewed_by: str = Field(..., min_length=2, max_length=120)
    reviewer_note: str | None = Field(default=None, max_length=1000)


class DashboardResponse(BaseModel):
    total_analyses: int
    review_rate: float
    average_confidence: float
    approval_rate: float
    label_distribution: dict[str, int]
    risk_distribution: dict[str, int]
    recent_items: list[InspectionRow]