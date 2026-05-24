import asyncio
from app.db.database import create_tables

asyncio.run(create_tables())