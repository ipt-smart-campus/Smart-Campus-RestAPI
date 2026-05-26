from datetime import datetime
from pydantic import BaseModel, Field


# ── Building ──────────────────────────────────────────────────────────────────

class BuildingCreate(BaseModel):
    id: str = Field(..., example="H", description="Letra identificadora do edifício")
    name: str = Field(..., example="Edifício H")
    description: str | None = Field(None, example="Edifício principal de engenharia")
    latitude: float = Field(..., example=39.6041)
    longitude: float = Field(..., example=-8.4128)

class BuildingOut(BuildingCreate):
    model_config = {"from_attributes": True}


# ── Room ──────────────────────────────────────────────────────────────────────

class RoomCreate(BaseModel):
    id: str = Field(..., example="H216")
    name: str = Field(..., example="Sala H216")
    floor: int = Field(0, example=2)
    capacity: int = Field(30, example=30)
    type: str = Field("classroom", example="classroom")
    building_id: str = Field(..., example="H")

class RoomOut(RoomCreate):
    model_config = {"from_attributes": True}


# ── Sensor ────────────────────────────────────────────────────────────────────

class SensorCreate(BaseModel):
    id: str = Field(..., example="temp-h216")
    type: str = Field(..., example="temperature")
    unit: str = Field(..., example="°C")
    description: str | None = Field(None, example="Sensor de temperatura sala H216")
    active: bool = Field(True)
    room_id: str = Field(..., example="H216")

class SensorOut(SensorCreate):
    model_config = {"from_attributes": True}


# ── SensorReading ─────────────────────────────────────────────────────────────

class ReadingCreate(BaseModel):
    sensor_id: str = Field(..., example="temp-h216")
    value: float = Field(..., example=24.5)
    timestamp: datetime | None = Field(None)

class ReadingOut(BaseModel):
    id: int
    sensor_id: str
    value: float
    timestamp: datetime

    model_config = {"from_attributes": True}


# ── Alert ─────────────────────────────────────────────────────────────────────

class AlertOut(BaseModel):
    id: int
    sensor_id: str
    type: str
    message: str
    value: float
    resolved: bool
    created_at: datetime
    resolved_at: datetime | None

    model_config = {"from_attributes": True}


# ── Room Status (dashboard) ───────────────────────────────────────────────────

class RoomStatus(BaseModel):
    room_id: str
    room_name: str
    building_id: str
    temperature: float | None
    humidity: float | None
    co2: float | None
    occupancy: float | None
    light: float | None
    active_alerts: list[str]


# ── Weather ───────────────────────────────────────────────────────────────────

class WeatherOut(BaseModel):
    temperature: float
    humidity: int
    wind_speed: float
    weather_code: int
    description: str
    timestamp: str