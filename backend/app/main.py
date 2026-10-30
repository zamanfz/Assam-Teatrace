from fastapi import FastAPI

from backend.app.routers.dashboard import router as dashboard_router
from backend.app.routers.compliance import router as compliance_router
from backend.app.database.database import Base, engine
from fastapi.middleware.cors import CORSMiddleware
from backend.app.models.entities import (
    Organization,
    User,
    TeaGarden,
    GreenLeafLot
)

from backend.app.routers.tea import router as tea_router


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Assam TeaTrace",
    description="Digital tea supply-chain traceability platform",
    version="0.3.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(tea_router)
app.include_router(compliance_router)
app.include_router(dashboard_router)


@app.get("/")
def root():
    return {
        "project": "Assam TeaTrace",
        "status": "running",
        "version": "0.3.0"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "database": "connected"
    }