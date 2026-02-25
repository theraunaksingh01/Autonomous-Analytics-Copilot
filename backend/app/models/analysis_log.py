from sqlalchemy import Column, Integer, ForeignKey, DateTime, Float, Text, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class AnalysisLog(Base):
    __tablename__ = "analysis_logs"

    id = Column(Integer, primary_key=True, index=True)

    file_id = Column(Integer, ForeignKey("uploaded_files.id"), nullable=False)

    question = Column(Text, nullable=False)
    answer = Column(Text)
    summary = Column(Text)

    analysis_type = Column(String)

    
    tools_used = Column(Text)

    confidence = Column(Float)
    latency = Column(Float)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    file = relationship("UploadedFile", back_populates="logs")