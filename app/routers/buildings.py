from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.database import get_db
from app.models.building import Building
from app.models.room import Room
from app.schemas.schemas import BuildingCreate, BuildingOut, RoomOut

router = APIRouter(prefix="/buildings", tags=["Buildings"])


@router.get("/", response_model=list[BuildingOut], summary="Lista todos os edifícios")
async def list_buildings(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Building).order_by(Building.id))
    return result.scalars().all()


@router.get("/{building_id}", response_model=BuildingOut, summary="Detalhes de um edifício")
async def get_building(building_id: str, db: AsyncSession = Depends(get_db)):
    building = await db.get(Building, building_id)
    if not building:
        raise HTTPException(status_code=404, detail=f"Edifício '{building_id}' não encontrado")
    return building


@router.post("/", response_model=BuildingOut, status_code=201, summary="Criar edifício")
async def create_building(data: BuildingCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.get(Building, data.id)
    if existing:
        raise HTTPException(status_code=409, detail=f"Edifício '{data.id}' já existe")
    building = Building(**data.model_dump())
    db.add(building)
    await db.commit()
    await db.refresh(building)
    return building


@router.put("/{building_id}", response_model=BuildingOut, summary="Atualizar edifício")
async def update_building(building_id: str, data: BuildingCreate, db: AsyncSession = Depends(get_db)):
    building = await db.get(Building, building_id)
    if not building:
        raise HTTPException(status_code=404, detail=f"Edifício '{building_id}' não encontrado")
    for key, value in data.model_dump().items():
        setattr(building, key, value)
    await db.commit()
    await db.refresh(building)
    return building


@router.delete("/{building_id}", status_code=204, summary="Apagar edifício")
async def delete_building(building_id: str, db: AsyncSession = Depends(get_db)):
    building = await db.get(Building, building_id)
    if not building:
        raise HTTPException(status_code=404, detail=f"Edifício '{building_id}' não encontrado")
    await db.delete(building)
    await db.commit()


@router.get("/{building_id}/rooms", response_model=list[RoomOut], summary="Salas de um edifício")
async def get_building_rooms(building_id: str, db: AsyncSession = Depends(get_db)):
    building = await db.get(Building, building_id)
    if not building:
        raise HTTPException(status_code=404, detail=f"Edifício '{building_id}' não encontrado")
    result = await db.execute(select(Room).where(Room.building_id == building_id))
    return result.scalars().all()