from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.schemas import EmailAccount, EmailAccountCreate, BulkEmailImport
from app.db.session import get_db
from app.db.models import EmailAccount as EmailAccountModel, User
from app.api.dependencies import get_current_active_user
from app.email.service import fetch_emails_for_account

router = APIRouter()

@router.post("", response_model=EmailAccount)
async def create_email_account(
    email_account_in: EmailAccountCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Create new email account.
    """
    # Check if this email account already exists for this user
    query = select(EmailAccountModel).where(
        EmailAccountModel.email_address == email_account_in.email_address,
        EmailAccountModel.user_id == current_user.id
    )
    result = await db.execute(query)
    if result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email account already exists",
        )
    
    # Create new account
    email_account = EmailAccountModel(
        user_id=current_user.id,
        email_address=email_account_in.email_address,
        refresh_token=email_account_in.refresh_token,
        client_id=email_account_in.client_id
    )
    db.add(email_account)
    await db.commit()
    await db.refresh(email_account)
    
    # Schedule background task to fetch emails
    background_tasks.add_task(
        fetch_emails_for_account,
        account_id=email_account.id,
        user_id=current_user.id
    )
    
    return email_account

@router.post("/bulk-import", response_model=List[EmailAccount])
async def bulk_import_email_accounts(
    bulk_import: BulkEmailImport,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Bulk import email accounts.
    """
    created_accounts = []
    
    for account_str in bulk_import.email_accounts:
        try:
            # Support both '——' and '----' separators
            if '——' in account_str:
                parts = account_str.split('——')
            elif '----' in account_str:
                parts = account_str.split('----')
            else:
                continue
                
            if len(parts) != 4:
                continue
                
            email_address, password, refresh_token, client_id = parts
            
            # Check if this email account already exists for this user
            query = select(EmailAccountModel).where(
                EmailAccountModel.email_address == email_address,
                EmailAccountModel.user_id == current_user.id
            )
            result = await db.execute(query)
            if result.scalars().first():
                continue
            
            # Create new account
            email_account = EmailAccountModel(
                user_id=current_user.id,
                email_address=email_address,
                refresh_token=refresh_token,
                client_id=client_id
            )
            db.add(email_account)
            await db.commit()
            await db.refresh(email_account)
            
            # Schedule background task to fetch emails
            background_tasks.add_task(
                fetch_emails_for_account,
                account_id=email_account.id,
                user_id=current_user.id
            )
            
            created_accounts.append(email_account)
        except Exception:
            # Skip any accounts that couldn't be processed
            continue
    
    return created_accounts

@router.get("", response_model=List[EmailAccount])
async def read_email_accounts(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve email accounts.
    """
    query = select(EmailAccountModel).where(
        EmailAccountModel.user_id == current_user.id
    ).offset(skip).limit(limit)
    result = await db.execute(query)
    accounts = result.scalars().all()
    return accounts

@router.get("/{account_id}", response_model=EmailAccount)
async def read_email_account(
    account_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get a specific email account by id.
    """
    query = select(EmailAccountModel).where(
        EmailAccountModel.id == account_id,
        EmailAccountModel.user_id == current_user.id
    )
    result = await db.execute(query)
    account = result.scalars().first()
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email account not found",
        )
    return account

@router.delete("/{account_id}", response_model=EmailAccount)
async def delete_email_account(
    account_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Delete an email account.
    """
    query = select(EmailAccountModel).where(
        EmailAccountModel.id == account_id,
        EmailAccountModel.user_id == current_user.id
    )
    result = await db.execute(query)
    account = result.scalars().first()
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email account not found",
        )
    
    await db.delete(account)
    await db.commit()
    return account

@router.post("/{account_id}/sync", response_model=EmailAccount)
async def sync_email_account(
    account_id: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Manually trigger a sync for an email account.
    """
    query = select(EmailAccountModel).where(
        EmailAccountModel.id == account_id,
        EmailAccountModel.user_id == current_user.id
    )
    result = await db.execute(query)
    account = result.scalars().first()
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email account not found",
        )
    
    # Trigger background task to fetch emails
    background_tasks.add_task(
        fetch_emails_for_account,
        account_id=account.id,
        user_id=current_user.id
    )
    
    return account 