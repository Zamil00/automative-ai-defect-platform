from __future__ import annotations

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.inspection import DashboardResponse, InspectionCreateResponse, InspectionReviewRequest
from app.services.inspection_service import InspectionService
from app.services.reporting import ReportingService

router = APIRouter()
inspection_service = InspectionService()
reporting_service = ReportingService()


@router.get('/health')
def health() -> dict:
    return {'status': 'ok'}


@router.post('/inspections', response_model=InspectionCreateResponse)
async def create_inspection(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> InspectionCreateResponse:
    if not file.filename:
        raise HTTPException(status_code=400, detail='A filename is required.')
    suffix = file.filename.lower().rsplit('.', 1)[-1]
    if suffix not in {'png', 'jpg', 'jpeg', 'bmp', 'webp'}:
        raise HTTPException(status_code=400, detail='Unsupported file type.')
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail='The uploaded file is empty.')
    return inspection_service.analyze_upload(db, file.filename, content)


@router.get('/dashboard', response_model=DashboardResponse)
def dashboard(db: Session = Depends(get_db)) -> DashboardResponse:
    items = inspection_service.list_inspections(db)
    return reporting_service.build_dashboard(items)


@router.get('/inspections')
def list_inspections(db: Session = Depends(get_db)) -> list[dict]:
    items = inspection_service.list_inspections(db)
    return [
        {
            'id': item.id,
            'filename': item.filename,
            'predicted_label': item.predicted_label,
            'confidence': item.confidence,
            'risk_level': item.risk_level,
            'needs_manual_review': item.needs_manual_review,
            'reviewer_status': item.reviewer_status,
            'reviewed_by': item.reviewed_by,
            'reviewer_note': item.reviewer_note,
            'created_at': item.created_at,
            'model_version': item.model_version,
            'original_image_path': item.original_image_path,
            'overlay_image_path': item.overlay_image_path,
            'mask_image_path': item.mask_image_path,
            'summary': item.summary,
            'metrics': item.metrics,
        }
        for item in items
    ]


@router.patch('/inspections/{inspection_id}/review')
def review_inspection(
    inspection_id: str,
    payload: InspectionReviewRequest,
    db: Session = Depends(get_db),
) -> dict:
    inspection = inspection_service.review_inspection(db, inspection_id, payload)
    if inspection is None:
        raise HTTPException(status_code=404, detail='Inspection not found.')
    return {
        'id': inspection.id,
        'reviewer_status': inspection.reviewer_status,
        'reviewed_by': inspection.reviewed_by,
        'reviewer_note': inspection.reviewer_note,
    }