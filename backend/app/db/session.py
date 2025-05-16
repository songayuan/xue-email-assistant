from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# Convert SQLite URL to async format if needed
if settings.DATABASE_URL.startswith("sqlite"):
    database_url = settings.DATABASE_URL.replace("sqlite:///", "sqlite+aiosqlite:///")
else:
    database_url = settings.DATABASE_URL

# Create async engine
engine = create_async_engine(database_url, echo=True)

# Create session factory for async operations
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Dependency to get DB session
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session 