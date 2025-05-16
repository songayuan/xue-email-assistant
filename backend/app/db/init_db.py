from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select

from app.db.models import Base, User
from app.db.session import engine, AsyncSessionLocal
from app.core.security import get_password_hash
from app.core.config import settings

async def init_db():
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Check if first admin user exists
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).limit(1))
        user = result.scalars().first()
        
        # If no users, create default admin
        if not user and settings.FIRST_USER_IS_ADMIN:
            await create_first_admin(session)

async def create_first_admin(db: AsyncSession):
    # This is just for demonstration, in production you would want to use environment variables
    admin = User(
        username="admin",
        email="admin@example.com",
        hashed_password=get_password_hash("adminpassword"),
        is_admin=True
    )
    db.add(admin)
    await db.commit()
    await db.refresh(admin)
    return admin 