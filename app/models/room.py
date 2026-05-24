from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base


class Room(Base):
    __tablename__ = "rooms"

    id: Mapped[str] = mapped_column(String(20), primary_key=True)   # "H216"
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    floor: Mapped[int] = mapped_column(Integer, default=0)
    capacity: Mapped[int] = mapped_column(Integer, default=30)
    type: Mapped[str] = mapped_column(
        String(50), default="classroom"
        # "classroom" | "lab" | "auditorium" | "office" | "common"
    )

    building_id: Mapped[str] = mapped_column(ForeignKey("buildings.id"), nullable=False)

    building: Mapped["Building"] = relationship(back_populates="rooms")  # noqa: F821
    sensors: Mapped[list["Sensor"]] = relationship(  # noqa: F821
        back_populates="room",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Room id={self.id} building={self.building_id}>"