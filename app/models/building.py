from sqlalchemy import String, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base


class Building(Base):
    __tablename__ = "buildings"

    # Usamos string como PK ("H", "A", "D") — mais legível nas FKs
    id: Mapped[str] = mapped_column(String(10), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)

    # Relação: um edifício tem muitas salas
    rooms: Mapped[list["Room"]] = relationship(  # noqa: F821
        back_populates="building",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Building id={self.id} name={self.name}>"