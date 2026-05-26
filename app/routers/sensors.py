from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.database import get_db
from app.models.sensor import Sensor
from app.schemas.schemas import SensorCreate, SensorOut

router = APIRouter(prefix="/sensors", tags=["Sensors"])


@router.get("/", response_model=list[SensorOut], summary="Lista todos os sensores")
async def list_sensors(
    room_id: str | None = None,
    type: str | None = None,
    active: bool | None = None,
    db: AsyncSession = Depends(get_db),
):
    q = select(Sensor).order_by(Sensor.id)
    if room_id:
        q = q.where(Sensor.room_id == room_id)
    if type:
        q = q.where(Sensor.type == type)
    if active is not None:
        q = q.where(Sensor.active.is_(active))
    result = await db.execute(q)
    return result.scalars().all()


@router.get("/{sensor_id}", response_model=SensorOut, summary="Detalhes de um sensor")
async def get_sensor(sensor_id: str, db: AsyncSession = Depends(get_db)):
    sensor = await db.get(Sensor, sensor_id)
    if not sensor:
        raise HTTPException(status_code=404, detail=f"Sensor '{sensor_id}' não encontrado")
    return sensor


@router.post("/", response_model=SensorOut, status_code=201, summary="Criar sensor")
async def create_sensor(data: SensorCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.get(Sensor, data.id)
    if existing:
        raise HTTPException(status_code=409, detail=f"Sensor '{data.id}' já existe")
    sensor = Sensor(**data.model_dump())
    db.add(sensor)
    await db.commit()
    await db.refresh(sensor)
    return sensor


@router.put("/{sensor_id}", response_model=SensorOut, summary="Atualizar sensor")
async def update_sensor(sensor_id: str, data: SensorCreate, db: AsyncSession = Depends(get_db)):
    sensor = await db.get(Sensor, sensor_id)
    if not sensor:
        raise HTTPException(status_code=404, detail=f"Sensor '{sensor_id}' não encontrado")
    for key, value in data.model_dump().items():
        setattr(sensor, key, value)
    await db.commit()
    await db.refresh(sensor)
    return sensor


@router.delete("/{sensor_id}", status_code=204, summary="Apagar sensor")
async def delete_sensor(sensor_id: str, db: AsyncSession = Depends(get_db)):
    sensor = await db.get(Sensor, sensor_id)
    if not sensor:
        raise HTTPException(status_code=404, detail=f"Sensor '{sensor_id}' não encontrado")
    await db.delete(sensor)
    await db.commit()