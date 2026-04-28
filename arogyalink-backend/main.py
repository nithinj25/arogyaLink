from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from firebase.client import init_firebase
from routes import voice, app as app_routes, asha, phc, families, cases
from config.settings import get_settings
from utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("ArogyaLink backend starting...")
    init_firebase()
    logger.info("Firebase initialized")
    yield
    logger.info("ArogyaLink backend shutting down")


app = FastAPI(
    title="ArogyaLink API",
    description="Rural Healthcare Coordination OS — Backend",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Tighten for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(voice.router)
app.include_router(app_routes.router)
app.include_router(asha.router)
app.include_router(phc.router)
app.include_router(families.router)
app.include_router(cases.router)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "arogyalink-backend"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=settings.port, reload=True)
