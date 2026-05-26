from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.database import get_db
from app.models.alert import Alert
from app.schemas.schemas import AlertOut

router = APIRouter(prefix="/alerts", tags=["Alerts"])


@router.get("/", response_model=list[AlertOut], summary="Lista alertas")
async def list_alerts(
    resolved: bool | None = None,
    sensor_id: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Lista alertas. Parâmetros:
    - resolved: true = resolvidos, false = activos, omitir = todos
    - sensor_id: filtrar por sensor
    """
    q = select(Alert).order_by(Alert.created_at.desc()).limit(100)
    if resolved is not None:
        q = q.where(Alert.resolved.is_(resolved))
    if sensor_id:
        q = q.where(Alert.sensor_id == sensor_id)
    result = await db.execute(q)
    return result.scalars().all()


@router.get("/{alert_id}", response_model=AlertOut, summary="Detalhes de um alerta")
async def get_alert(alert_id: int, db: AsyncSession = Depends(get_db)):
    alert = await db.get(Alert, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alerta não encontrado")
    return alert


@router.patch("/{alert_id}/resolve", response_model=AlertOut, summary="Resolver alerta")
async def resolve_alert(alert_id: int, db: AsyncSession = Depends(get_db)):
    alert = await db.get(Alert, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alerta não encontrado")
    if alert.resolved:
        raise HTTPException(status_code=400, detail="Alerta já está resolvido")
    alert.resolved = True
    alert.resolved_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(alert)
    return alert