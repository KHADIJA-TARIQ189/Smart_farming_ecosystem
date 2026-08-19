from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app import models  # noqa: F401  (ensures all models are registered on Base)
from app.routers import auth, users, farms, devices, sensors, actuators, crops, alerts, ws
from app.services.mqtt_service import start_mqtt_client

app = FastAPI(
    title="Smart Farming Ecosystem API",
    description="Backend for the IoT/AI/Computer-Vision powered precision agriculture platform.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten this once the frontend origin is known
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Creates tables if they don't exist. Fine for dev; switch to Alembic migrations
# once the schema stabilizes (see alembic/ folder placeholder in the README).
Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(farms.router)
app.include_router(devices.router)
app.include_router(sensors.router)
app.include_router(actuators.router)
app.include_router(crops.router)
app.include_router(alerts.router)
app.include_router(ws.router)


@app.on_event("startup")
def on_startup():
    start_mqtt_client()


@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok"}
