from fastapi import APIRouter, HTTPException
from app.services.weather import get_current_weather, get_forecast

router = APIRouter(prefix="/weather", tags=["Weather"])


@router.get("/current", summary="Clima atual no campus")
async def current_weather():
    """
    Clima atual no campus via Open-Meteo.
    Sem chave API. Atualizado a cada hora.
    """
    try:
        return await get_current_weather()
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Erro ao obter clima: {str(e)}")


@router.get("/forecast", summary="Previsão para 3 dias")
async def forecast():
    """Previsão diária para os próximos 3 dias."""
    try:
        return await get_forecast()
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Erro ao obter previsão: {str(e)}")