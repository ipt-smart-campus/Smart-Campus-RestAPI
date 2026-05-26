from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.database import get_db
from app.models.sensor import Sensor
from app.models.sensor_reading import SensorReading
from app.schemas.schemas import ReadingCreate, ReadingOut

router = APIRouter(prefix="/readings", tags=["Readings"])


@router.post("/", response_model=ReadingOut, status_code=201, summary="Registar leitura de sensor")
async def create_reading(data: ReadingCreate, db: AsyncSession = Depends(get_db)):
    """Endpoint principal: sensor envia valor → guarda na BD."""
    sensor = await db.get(Sensor, data.sensor_id)
    if not sensor:
        raise HTTPException(status_code=404, detail=f"Sensor '{data.sensor_id}' não encontrado")
    if not sensor.active:
        raise HTTPException(status_code=400, detail=f"Sensor '{data.sensor_id}' está inativo")

    reading = SensorReading(
        sensor_id=data.sensor_id,
        value=data.value,
        timestamp=data.timestamp or datetime.now(timezone.utc),
    )
    db.add(reading)
    await db.commit()
    await db.refresh(reading)
    return reading


@router.get("/", response_model=list[ReadingOut], summary="Histórico de leituras")
async def list_readings(
    sensor_id: str | None = None,
    room_id: str | None = None,
    hours: int = 24,
    limit: int = 500,
    db: AsyncSession = Depends(get_db),
):
    """
    Histórico filtrável. Parâmetros:
    - sensor_id: filtrar por sensor específico
    - room_id: filtrar por todos os sensores de uma sala
    - hours: últimas N horas (default 24)
    - limit: máximo de registos (default 500)
    """
    since = datetime.now(timezone.utc) - timedelta(hours=hours)

    q = (
        select(SensorReading)
        .where(SensorReading.timestamp >= since)
        .order_by(SensorReading.timestamp.desc())
        .limit(limit)
    )

    if sensor_id:
        q = q.where(SensorReading.sensor_id == sensor_id)
    elif room_id:
        sensor_ids_result = await db.execute(
            select(Sensor.id).where(Sensor.room_id == room_id)
        )
        ids = sensor_ids_result.scalars().all()
        if not ids:
            return []
        q = q.where(SensorReading.sensor_id.in_(ids))

    result = await db.execute(q)
    return result.scalars().all()


@router.get("/latest/{sensor_id}", response_model=ReadingOut, summary="Última leitura de um sensor")
async def get_latest_reading(sensor_id: str, db: AsyncSession = Depends(get_db)):
    sensor = await db.get(Sensor, sensor_id)
    if not sensor:
        raise HTTPException(status_code=404, detail=f"Sensor '{sensor_id}' não encontrado")

    result = await db.execute(
        select(SensorReading)
        .where(SensorReading.sensor_id == sensor_id)
        .order_by(SensorReading.timestamp.desc())
        .limit(1)
    )
    reading = result.scalar_one_or_none()
    if not reading:
        raise HTTPException(status_code=404, detail="Nenhuma leitura encontrada para este sensor")
    return reading