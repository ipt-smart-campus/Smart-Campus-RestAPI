from datetime import datetime, timezone
from sqlalchemy import Float, String, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    sensor_id: Mapped[str] = mapped_column(
        ForeignKey("sensors.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Tipo do alerta — facilita filtrar no dashboard
    type: Mapped[str] = mapped_column(String(30), nullable=False)
    # Tipos:
    #   "temp_high"    → temperatura acima do máximo
    #   "temp_low"     → temperatura abaixo do mínimo
    #   "co2_high"     → CO₂ acima do máximo
    #   "humidity_high"→ humidade excessiva
    #   "light_waste"  → luz ligada com sala vazia

    message: Mapped[str] = mapped_column(String(500), nullable=False)
    value: Mapped[float] = mapped_column(Float, nullable=False)  # valor que causou o alerta

    resolved: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    sensor: Mapped["Sensor"] = relationship(back_populates="alerts")  # noqa: F821

    __table_args__ = (
        Index("ix_alerts_sensor_resolved", "sensor_id", "resolved"),
    )

    def __repr__(self) -> str:
        return f"<Alert id={self.id} type={self.type} resolved={self.resolved}>"