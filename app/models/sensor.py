from sqlalchemy import String, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base


class Sensor(Base):
    __tablename__ = "sensors"

    # ID descritivo: "temp-h216", "co2-h216", "occ-h216", "light-h216"
    id: Mapped[str] = mapped_column(String(50), primary_key=True)

    type: Mapped[str] = mapped_column(String(30), nullable=False)
    # Tipos válidos:
    #   "temperature"  → °C
    #   "humidity"     → %
    #   "co2"          → ppm
    #   "occupancy"    → pessoas
    #   "light"        → lux

    unit: Mapped[str] = mapped_column(String(10), nullable=False)
    description: Mapped[str | None] = mapped_column(String(200), nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)

    room_id: Mapped[str] = mapped_column(ForeignKey("rooms.id"), nullable=False)

    room: Mapped["Room"] = relationship(back_populates="sensors")  # noqa: F821
    readings: Mapped[list["SensorReading"]] = relationship(  # noqa: F821
        back_populates="sensor",
        cascade="all, delete-orphan",
        order_by="SensorReading.timestamp.desc()",
    )
    alerts: Mapped[list["Alert"]] = relationship(  # noqa: F821
        back_populates="sensor",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Sensor id={self.id} type={self.type} room={self.room_id}>"