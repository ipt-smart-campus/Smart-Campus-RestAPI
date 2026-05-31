"""
Serviço de localização — GeoAPI Portugal
Docs: https://geoapi.pt
Sem chave API, dados oficiais portugueses.
"""
import httpx
from app.config import settings

# Header obrigatório — sem isto a GeoAPI devolve HTML em vez de JSON
HEADERS = {"Accept": "application/json"}

# Campos relevantes para o contexto do IPT
MUNICIPIO_FIELDS = ["nome", "distrito", "email", "telefone", "fax", "sitio", "areaha", "codigoine"]


def filter_municipio(data: dict) -> dict:
    """Filtra apenas os campos relevantes de um município."""
    return {k: data[k] for k in MUNICIPIO_FIELDS if k in data}


async def get_municipio(municipio: str) -> dict:
    url = f"{settings.GEO_API_URL}/municipios/{municipio}"
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(url, headers=HEADERS)
        resp.raise_for_status()
        return filter_municipio(resp.json())


async def get_campus_location() -> dict:
    municipio_data = {}
    try:
        municipio_data = await get_municipio(settings.CAMPUS_MUNICIPIO)
    except Exception:
        municipio_data = {"error": "GeoAPI indisponivel"}

    return {
        "campus": {
            "latitude":  settings.CAMPUS_LATITUDE,
            "longitude": settings.CAMPUS_LONGITUDE,
            "municipio": settings.CAMPUS_MUNICIPIO,
        },
        "municipio_info": municipio_data,
    }


async def get_all_municipios() -> dict:
    url = f"{settings.GEO_API_URL}/municipios"
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(url, headers=HEADERS)
        resp.raise_for_status()
        raw = resp.json()
        # A GeoAPI devolve {"municipios": [...]} ou uma lista direta
        if isinstance(raw, list):
            return [filter_municipio(m) for m in raw]
        if "municipios" in raw:
            return {"municipios": [filter_municipio(m) for m in raw["municipios"]]}
        return raw


async def get_distrito(distrito: str) -> dict:
    url = f"{settings.GEO_API_URL}/distritos/{distrito}"
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(url, headers=HEADERS)
        resp.raise_for_status()
        return resp.json()