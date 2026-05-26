from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.database import create_tables
from app.routers import buildings, rooms, sensors, readings, alerts


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Corre no arranque: garante que as tabelas existem."""
    await create_tables()
    yield


app = FastAPI(
    title="Smart Campus API",
    description="""
API REST para monitorização de edifícios do campus.

## Recursos
- **Buildings** — edifícios do campus
- **Rooms** — salas com estado em tempo real
- **Sensors** — sensores de temperatura, CO₂, ocupação e luz
- **Readings** — leituras dos sensores (série temporal)
- **Alerts** — alertas automáticos por limiar
    """,
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — permite que o frontend React aceda à API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registar todos os routers sob /api
app.include_router(buildings.router, prefix="/api")
app.include_router(rooms.router,     prefix="/api")
app.include_router(sensors.router,   prefix="/api")
app.include_router(readings.router,  prefix="/api")
app.include_router(alerts.router,    prefix="/api")


@app.get("/health", tags=["System"])
async def health():
    """Verificar que a API está online."""
    return {"status": "ok", "version": "1.0.0"}