from datetime import datetime, timezone
from sqlalchemy import Float, String, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base
from app.models.sensor import Sensor


class SensorReading(Base):
    __tablename__ = "sensor_readings"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    sensor_id: Mapped[str] = mapped_column(
        ForeignKey("sensors.id", ondelete="CASCADE"),
        nullable=False,
    )
    value: Mapped[float] = mapped_column(Float, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    sensor: Mapped["Sensor"] = relationship(back_populates="readings")  # noqa: F821

    
    __table_args__ = (
        Index("ix_readings_sensor_time", "sensor_id", "timestamp"),
    )

    def __repr__(self) -> str:
        return f"<SensorReading sensor={self.sensor_id} value={self.value} ts={self.timestamp}>"