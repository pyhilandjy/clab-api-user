from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import reports, audio, plan

# FastAPI 앱 생성
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://talk-d-fe.vercel.app/",
        "http://localhost:3000",
        "http://localhost:3100",
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
