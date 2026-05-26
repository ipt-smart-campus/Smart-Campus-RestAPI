from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.database import get_db
from app.models.room import Room
from app.models.sensor import Sensor
from app.models.sensor_reading import SensorReading
from app.models.alert import Alert
from app.schemas.schemas import RoomCreate, RoomOut, SensorOut, RoomStatus

router = APIRouter(prefix="/rooms", tags=["Rooms"])


@router.get("/", response_model=list[RoomOut], summary="Lista todas as salas")
async def list_rooms(
    building_id: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    q = select(Room).order_by(Room.id)
    if building_id:
        q = q.where(Room.building_id == building_id)
    result = await db.execute(q)
    return result.scalars().all()


@router.get("/{room_id}", response_model=RoomOut, summary="Detalhes de uma sala")
async def get_room(room_id: str, db: AsyncSession = Depends(get_db)):
    room = await db.get(Room, room_id)
    if not room:
        raise HTTPException(status_code=404, detail=f"Sala '{room_id}' não encontrada")
    return room


@router.post("/", response_model=RoomOut, status_code=201, summary="Criar sala")
async def create_room(data: RoomCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.get(Room, data.id)
    if existing:
        raise HTTPException(status_code=409, detail=f"Sala '{data.id}' já existe")
    room = Room(**data.model_dump())
    db.add(room)
    await db.commit()
    await db.refresh(room)
    return room


@router.put("/{room_id}", response_model=RoomOut, summary="Atualizar sala")
async def update_room(room_id: str, data: RoomCreate, db: AsyncSession = Depends(get_db)):
    room = await db.get(Room, room_id)
    if not room:
        raise HTTPException(status_code=404, detail=f"Sala '{room_id}' não encontrada")
    for key, value in data.model_dump().items():
        setattr(room, key, value)
    await db.commit()
    await db.refresh(room)
    return room


@router.delete("/{room_id}", status_code=204, summary="Apagar sala")
async def delete_room(room_id: str, db: AsyncSession = Depends(get_db)):
    room = await db.get(Room, room_id)
    if not room:
        raise HTTPException(status_code=404, detail=f"Sala '{room_id}' não encontrada")
    await db.delete(room)
    await db.commit()


@router.get("/{room_id}/sensors", response_model=list[SensorOut], summary="Sensores de uma sala")
async def get_room_sensors(room_id: str, db: AsyncSession = Depends(get_db)):
    room = await db.get(Room, room_id)
    if not room:
        raise HTTPException(status_code=404, detail=f"Sala '{room_id}' não encontrada")
    result = await db.execute(select(Sensor).where(Sensor.room_id == room_id))
    return result.scalars().all()


@router.get("/{room_id}/status", response_model=RoomStatus, summary="Estado atual da sala (dashboard)")
async def get_room_status(room_id: str, db: AsyncSession = Depends(get_db)):
    """Retorna a última leitura de cada sensor e alertas activos — endpoint principal do dashboard."""
    room = await db.get(Room, room_id)
    if not room:
        raise HTTPException(status_code=404, detail=f"Sala '{room_id}' não encontrada")

    sensors_result = await db.execute(
        select(Sensor).where(Sensor.room_id == room_id, Sensor.active.is_(True))
    )
    sensors = sensors_result.scalars().all()

    values: dict[str, float | None] = {
        "temperature": None, "humidity": None,
        "co2": None, "occupancy": None, "light": None,
    }

    for sensor in sensors:
        last = await db.execute(
            select(SensorReading)
            .where(SensorReading.sensor_id == sensor.id)
            .order_by(SensorReading.timestamp.desc())
            .limit(1)
        )
        reading = last.scalar_one_or_none()
        if reading and sensor.type in values:
            values[sensor.type] = reading.value

    sensor_ids = [s.id for s in sensors]
    alerts_result = await db.execute(
        select(Alert).where(
            Alert.sensor_id.in_(sensor_ids),
            Alert.resolved.is_(False),
        )
    )
    active_alerts = [a.message for a in alerts_result.scalars().all()]

    return RoomStatus(
        room_id=room_id,
        room_name=room.name,
        building_id=room.building_id,
        **values,
        active_alerts=active_alerts,
    )