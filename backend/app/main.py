from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.models import UploadedFile, AnalysisLog
from app.routers import upload
from app.routers import profile
from dotenv import load_dotenv
from app.routers import query

load_dotenv()

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Analytics Copilot API")

origins = ["http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router)
app.include_router(profile.router)
app.include_router(query.router)

@app.get("/")
def health_check():
    return {"status": "ok", "message": "AI Analytics Copilot backend running"}
