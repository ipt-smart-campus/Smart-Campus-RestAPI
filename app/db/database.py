from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.config import settings

# Motor assíncrono — não bloqueia o event loop do FastAPI
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DB_ECHO,       # True em dev: mostra SQL no terminal
    pool_size=10,                 # ligações simultâneas
    max_overflow=20,              # ligações extra em pico de carga
)

# Fábrica de sessões — expire_on_commit=False evita lazy-load após commit
AsyncSessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Classe base de todos os models SQLAlchemy."""
    pass


async def get_db() -> AsyncSession:
    """
    Dependency do FastAPI.
    Uso nos routers:
        db: AsyncSession = Depends(get_db)
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def create_tables():
    """Cria todas as tabelas (usado em dev sem Alembic)."""
    async with engine.begin() as conn:
        # Importar todos os models para registar os metadados
        from app.models import building, room, sensor, sensor_reading, alert  # noqa
        await conn.run_sync(Base.metadata.create_all)


async def drop_tables():
    """Apaga tudo — útil para reset em desenvolvimento."""
    async with engine.begin() as conn:
        from app.models import building, room, sensor, sensor_reading, alert  # noqa
        await conn.run_sync(Base.metadata.drop_all)