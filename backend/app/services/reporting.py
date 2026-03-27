from __future__ import annotations

from collections import Counter
from statistics import mean

from app.models.inspection import Inspection
from app.schemas.inspection import DashboardResponse, InspectionRow


class ReportingService:
    @staticmethod
    def build_dashboard(items: list[Inspection]) -> DashboardResponse:
        if not items:
            return DashboardResponse(
                total_analyses=0,
                review_rate=0.0,
                average_confidence=0.0,
                approval_rate=0.0,
                label_distribution={},
                risk_distribution={},
                recent_items=[],
            )

        total = len(items)
        review_rate = sum(item.needs_manual_review for item in items) / total
        average_confidence = mean(item.confidence for item in items)
        approvals = sum(item.reviewer_status == 'approved' for item in items)

        recent_rows = [
            InspectionRow(
                id=item.id,
                filename=item.filename,
                predicted_label=item.predicted_label,
                confidence=item.confidence,
                risk_level=item.risk_level,
                needs_manual_review=item.needs_manual_review,
                reviewer_status=item.reviewer_status,
                reviewed_by=item.reviewed_by,
                reviewer_note=item.reviewer_note,
                created_at=item.created_at,
                model_version=item.model_version,
            )
            for item in items[:10]
        ]

        return DashboardResponse(
            total_analyses=total,
            review_rate=round(review_rate, 3),
            average_confidence=round(average_confidence, 3),
            approval_rate=round(approvals / total, 3),
            label_distribution=dict(Counter(item.predicted_label for item in items)),
            risk_distribution=dict(Counter(item.risk_level for item in items)),
            recent_items=recent_rows,
        )
