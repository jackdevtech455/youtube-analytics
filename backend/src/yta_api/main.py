from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from yta_api.settings import ApiSettings
from yta_api.routes.trackers import router as trackers_router
from yta_api.routes.videos import router as videos_router
from yta_api.routes.channels import router as channels_router

api_settings = ApiSettings()

app = FastAPI(title="YouTube Tracker Analytics API", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=api_settings.cors_allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check() -> dict[str, bool]:
    return {"ok": True}


app.include_router(trackers_router)
app.include_router(videos_router)
app.include_router(channels_router)
