from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.responses import FileResponse
from pydantic import BaseModel

from app.database import get_db
from app.models import UploadedFile, AnalysisLog
from app.services.orchestrator import Orchestrator
from app.services.insight_engine import generate_dataset_insights
from app.services.report_engine import generate_pdf_report

import json


router = APIRouter(prefix="/query", tags=["Query"])


class QueryRequest(BaseModel):
    question: str


# =========================
# ASK QUESTION
# =========================
@router.post("/{file_id}")
def query_dataset(file_id: int, request: QueryRequest, db: Session = Depends(get_db)):

    db_file = db.query(UploadedFile).filter(UploadedFile.id == file_id).first()

    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")

    orchestrator = Orchestrator(db)

    result = orchestrator.run(
        file_path=db_file.file_location,
        question=request.question,
        file_id=file_id
    )
    
    raw_answer = result.get("answer")

    if isinstance(raw_answer, (dict, list)):
        serialized_answer = json.dumps(raw_answer)
    else:
        serialized_answer = str(raw_answer)

    log = AnalysisLog(
        file_id=file_id,
        question=request.question,
        answer=serialized_answer,
        summary=result.get("summary"),
        analysis_type=result.get("plan", {}).get("analysis_type"),
        tools_used=str(result.get("plan", {}).get("steps")),
        confidence=result.get("confidence"),
        latency=result.get("latency"),
    )

    db.add(log)
    db.commit()

    return result


# =========================
# HISTORY
# =========================
@router.get("/history/{file_id}")
def get_history(file_id: int, db: Session = Depends(get_db)):

    logs = (
        db.query(AnalysisLog)
        .filter(AnalysisLog.file_id == file_id)
        .order_by(AnalysisLog.created_at.desc())
        .all()
    )

    return [
        {
            "id": log.id,
            "question": log.question,
            "answer": log.answer,
            "summary": log.summary,
            "confidence": log.confidence,
            "latency": log.latency,
            "created_at": log.created_at,
        }
        for log in logs
    ]


# =========================
# DOWNLOAD REPORT
# =========================
@router.get("/report/{file_id}")
def download_report(file_id: int, db: Session = Depends(get_db)):

    file = db.query(UploadedFile).filter(UploadedFile.id == file_id).first()

    if not file:
        raise HTTPException(status_code=404, detail="File not found")

    logs = (
        db.query(AnalysisLog)
        .filter(AnalysisLog.file_id == file_id)
        .order_by(AnalysisLog.created_at.desc())
        .limit(10)
        .all()
    )

    insights = generate_dataset_insights(file.file_location)

    pdf_path = generate_pdf_report(file.filename, insights, logs)

    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename="report.pdf"
    )