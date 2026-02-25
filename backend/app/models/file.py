from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.database import Base
from sqlalchemy.orm import relationship

class UploadedFile(Base):
    __tablename__ = "uploaded_files"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    file_location = Column(String, nullable=False)
    filesize = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    logs = relationship("AnalysisLog", back_populates="file", cascade="all, delete")