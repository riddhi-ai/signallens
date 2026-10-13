from __future__ import annotations

from fastapi import APIRouter, Depends, Request, status

from app.schemas.report import ReportCreate, ReportDetail, ReportOut, StatusUpdate
from app.services.reports import ReportService

router = APIRouter(prefix="/reports", tags=["reports"])


def get_service(request: Request) -> ReportService:
    service: ReportService = request.app.state.report_service
    return service


@router.get("", response_model=list[ReportOut])
def list_reports(service: ReportService = Depends(get_service)) -> list[ReportOut]:
    return service.list_reports()


@router.post("", response_model=ReportDetail, status_code=status.HTTP_201_CREATED)
def create_report(payload: ReportCreate, service: ReportService = Depends(get_service)) -> ReportDetail:
    return service.create_report(payload)


@router.get("/{report_id}", response_model=ReportDetail)
def get_report(report_id: str, service: ReportService = Depends(get_service)) -> ReportDetail:
    return service.get_report(report_id)


@router.post("/{report_id}/classify", response_model=ReportDetail)
def classify_report(report_id: str, service: ReportService = Depends(get_service)) -> ReportDetail:
    """Run or retry text classification. Each run is stored as a new prediction row."""
    return service.classify(report_id)


@router.post("/{report_id}/weather", response_model=ReportDetail)
def refresh_weather(report_id: str, service: ReportService = Depends(get_service)) -> ReportDetail:
    """Retry or refresh the weather snapshot for this report's location."""
    return service.refresh_weather(report_id)


@router.patch("/{report_id}/status", response_model=ReportDetail)
def update_status(
    report_id: str, payload: StatusUpdate, service: ReportService = Depends(get_service)
) -> ReportDetail:
    return service.update_status(report_id, payload)
