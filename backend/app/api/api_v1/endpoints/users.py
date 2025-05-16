from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.future import select

from app.api.schemas import User, UserUpdate
from app.db.session import get_db
from app.db.models import User as UserModel
from app.api.dependencies import get_current_active_user, get_current_active_admin

router = APIRouter()

@router.get("/me", response_model=User)
async def read_users_me(
    current_user: UserModel = Depends(get_current_active_user),
) -> Any:
    """
    Get current user
    """
    return current_user

@router.patch("/me", response_model=User)
async def update_user_me(
    user_in: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user),
) -> Any:
    """
    Update current user
    """
    from app.core.security import get_password_hash
    
    # Update user attributes
    if user_in.username is not None:
        # Check if username is already taken
        query = select(UserModel).where(
            UserModel.username == user_in.username,
            UserModel.id != current_user.id
        )
        result = await db.execute(query)
        if result.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered",
            )
        current_user.username = user_in.username
    
    if user_in.email is not None:
        # Check if email is already taken
        query = select(UserModel).where(
            UserModel.email == user_in.email,
            UserModel.id != current_user.id
        )
        result = await db.execute(query)
        if result.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )
        current_user.email = user_in.email
    
    if user_in.password is not None:
        current_user.hashed_password = get_password_hash(user_in.password)
    
    await db.commit()
    await db.refresh(current_user)
    return current_user

@router.get("", response_model=List[User])
async def read_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_admin),
) -> Any:
    """
    Retrieve users. Only for admins.
    """
    query = select(UserModel).offset(skip).limit(limit)
    result = await db.execute(query)
    users = result.scalars().all()
    return users

@router.get("/{user_id}", response_model=User)
async def read_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_admin),
) -> Any:
    """
    Get a specific user by id. Only for admins.
    """
    query = select(UserModel).where(UserModel.id == user_id)
    result = await db.execute(query)
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user

@router.patch("/{user_id}", response_model=User)
async def update_user(
    user_id: str,
    user_in: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_admin),
) -> Any:
    """
    Update a user. Only for admins.
    """
    from app.core.security import get_password_hash
    
    query = select(UserModel).where(UserModel.id == user_id)
    result = await db.execute(query)
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # Update user attributes
    if user_in.username is not None:
        user.username = user_in.username
    if user_in.email is not None:
        user.email = user_in.email
    if user_in.password is not None:
        user.hashed_password = get_password_hash(user_in.password)
    if user_in.is_active is not None:
        user.is_active = user_in.is_active
    
    await db.commit()
    await db.refresh(user)
    return user 