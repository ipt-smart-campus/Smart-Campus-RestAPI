from fastapi import APIRouter, HTTPException
from app.services.geo import get_campus_location, get_municipio, get_all_municipios, get_distrito

router = APIRouter(prefix="/location", tags=["Location"])


@router.get("/campus", summary="Localização do campus")
async def campus_location():
    try:
        return await get_campus_location()
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Erro ao obter localização: {str(e)}")


@router.get("/municipios", summary="Lista todos os municípios de Portugal")
async def list_municipios():
    try:
        return await get_all_municipios()
    except Exception:
        return {"error": "GeoAPI indisponivel de momento", "info": "https://geoapi.pt"}


@router.get("/municipios/{municipio}", summary="Informação de um município")
async def get_municipio_info(municipio: str):
    try:
        return await get_municipio(municipio)
    except Exception:
        return {"error": "GeoAPI indisponivel de momento", "municipio": municipio}


@router.get("/distritos/{distrito}", summary="Informação de um distrito")
async def get_distrito_info(distrito: str):
    try:
        return await get_distrito(distrito)
    except Exception as e:
        return {"error": "GeoAPI indisponivel de momento", "distrito": distrito, "detalhe": str(e)}