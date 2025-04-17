import logging
from logging.handlers import TimedRotatingFileHandler

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
import sentry_sdk

from app.routers import reports, audio, plan
from app.config import settings

# Sentry 설정
sentry_dsn = settings.sentry_dsn
sentry_environment = settings.sentry_environment

sentry_sdk.init(
    dsn=sentry_dsn,
    environment=sentry_environment,
    integrations=[FastApiIntegration(), LoggingIntegration()],
    traces_sample_rate=0.1,
    send_default_pii=True,
)

# 로깅 설정
log_formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)
log_file = "app.log"

file_handler = TimedRotatingFileHandler(
    log_file, when="midnight", interval=1, backupCount=14, encoding="utf-8"
)
file_handler.setFormatter(log_formatter)
file_handler.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)
console_handler.setLevel(logging.INFO)

logging.basicConfig(level=logging.INFO, handlers=[file_handler, console_handler])
logger = logging.getLogger(__name__)

# FastAPI 앱 생성
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://talk-d-fe.vercel.app",
        "http://localhost:3000",
        "http://localhost:3100",
        "https://talk-d-demo.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(reports.router)
app.include_router(audio.router)
app.include_router(plan.router)

# depends api key
# app.include_router(audio.router, prefix="/audio", dependencies=[Depends(get_api_key)])
# app.include_router(users.router, dependencies=[Depends(get_api_key)])
# app.include_router(stt.router, prefix="/stt", dependencies=[Depends(get_api_key)])
# app.include_router(reports.router, dependencies=[Depends(get_api_key)])


@app.get("/")
async def home():
    return {"status": "ok"}


@app.get("/debug-sentry")
async def trigger_error():
    division_by_zero = 1 / 0
