from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.inspection import Inspection
from app.schemas.inspection import InspectionCreateResponse, InspectionReviewRequest
from app.services.ml_model import DefectModelService
from app.services.storage import StorageService


class InspectionService:
    def __init__(self) -> None:
        self.storage = StorageService()
        self.model = DefectModelService()

    def analyze_upload(self, db: Session, filename: str, content: bytes) -> InspectionCreateResponse:
        inspection_id, upload_path = self.storage.save_upload(filename, content)
        overlay_path = self.storage.overlay_path(inspection_id)
        mask_path = self.storage.mask_path(inspection_id)

        prediction = self.model.predict(upload_path, overlay_path, mask_path)

        risk_level = self._risk_level(prediction.confidence, prediction.defect_score, prediction.label)
        needs_review = risk_level != 'low' or prediction.label != 'OK'
        summary = self._summary(prediction.label, prediction.confidence, needs_review)

        inspection = Inspection(
            id=inspection_id,
            filename=upload_path.name,
            predicted_label=prediction.label,
            confidence=round(prediction.confidence, 4),
            risk_level=risk_level,
            needs_manual_review=needs_review,
            model_version=prediction.model_version,
            summary=summary,
            original_image_path=f'/files/uploads/{upload_path.name}',
            overlay_image_path=f'/files/overlays/{overlay_path.name}',
            mask_image_path=f'/files/masks/{mask_path.name}',
            metrics={k: round(v, 4) if isinstance(v, float) else v for k, v in prediction.metrics.items()},
            reviewer_status='pending',
        )
        db.add(inspection)
        db.commit()
        db.refresh(inspection)

        return InspectionCreateResponse(
            id=inspection.id,
            filename=inspection.filename,
            predicted_label=inspection.predicted_label,
            confidence=inspection.confidence,
            risk_level=inspection.risk_level,
            needs_manual_review=inspection.needs_manual_review,
            summary=inspection.summary,
            model_version=inspection.model_version,
            original_image_path=inspection.original_image_path,
            overlay_image_path=inspection.overlay_image_path,
            mask_image_path=inspection.mask_image_path,
            reviewer_status=inspection.reviewer_status,
            metrics=inspection.metrics,
            created_at=inspection.created_at,
        )

    def list_inspections(self, db: Session) -> list[Inspection]:
        stmt = select(Inspection).order_by(Inspection.created_at.desc())
        return list(db.scalars(stmt))

    def get_inspection(self, db: Session, inspection_id: str) -> Inspection | None:
        return db.get(Inspection, inspection_id)

    def review_inspection(self, db: Session, inspection_id: str, payload: InspectionReviewRequest) -> Inspection | None:
        inspection = db.get(Inspection, inspection_id)
        if inspection is None:
            return None
        inspection.reviewer_status = payload.reviewer_status
        inspection.reviewed_by = payload.reviewed_by
        inspection.reviewer_note = payload.reviewer_note
        inspection.reviewed_at = datetime.now(timezone.utc)
        db.add(inspection)
        db.commit()
        db.refresh(inspection)
        return inspection

    @staticmethod
    def _risk_level(confidence: float, defect_score: float, label: str) -> str:
        if label == 'Crack' or defect_score > 0.45:
            return 'high'
        if confidence < 0.72 or label in {'Scratch', 'Dent', 'Stain'}:
            return 'medium'
        return 'low'

    @staticmethod
    def _summary(label: str, confidence: float, needs_review: bool) -> str:
        if needs_review:
            return f'Model predicted {label} with {confidence * 100:.1f}% confidence. The localized overlay highlights regions that should be manually reviewed.'
        return f'Model predicted {label} with {confidence * 100:.1f}% confidence. No significant defect region was identified.'