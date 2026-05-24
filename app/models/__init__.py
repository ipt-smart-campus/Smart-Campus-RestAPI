# Importar todos os models aqui para que o SQLAlchemy os registe
# antes de qualquer create_all / alembic autogenerate
from app.models.building import Building
from app.models.room import Room
from app.models.sensor import Sensor
from app.models.sensor_reading import SensorReading
from app.models.alert import Alert

__all__ = ["Building", "Room", "Sensor", "SensorReading", "Alert"]