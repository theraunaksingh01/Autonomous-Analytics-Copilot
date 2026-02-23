from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.models.file import UploadedFile
from app.services.agent import run_agent

router = APIRouter()


class QueryRequest(BaseModel):
    question: str


@router.post("/query/{file_id}")
def query_dataset(file_id: int, request: QueryRequest, db: Session = Depends(get_db)):
    db_file = db.query(UploadedFile).filter(UploadedFile.id == file_id).first()

    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")

    result = run_agent(db_file.filepath, request.question)

    return result