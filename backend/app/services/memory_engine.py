from app.models import AnalysisLog
from sqlalchemy.orm import Session


def build_memory_context(db: Session, file_id: int, limit: int = 5):
    logs = (
        db.query(AnalysisLog)
        .filter(AnalysisLog.file_id == file_id)
        .order_by(AnalysisLog.created_at.desc())
        .limit(limit)
        .all()
    )

    if not logs:
        return ""

    context = []
    for log in reversed(logs):
        context.append(f"User: {log.question}")
        context.append(f"Agent: {log.answer}")

    return "\n".join(context)


def update_memory(db: Session, file_id: int, question: str, answer: str):
    # Memory already stored in AnalysisLog via query router.
    # This function exists for extensibility (vector memory later).
    return