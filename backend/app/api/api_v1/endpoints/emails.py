from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.api.schemas import Email
from app.db.session import get_db
from app.db.models import Email as EmailModel, EmailAccount as EmailAccountModel, User, Attachment
from app.api.dependencies import get_current_active_user

router = APIRouter()

@router.get("", response_model=List[Email])
async def read_emails(
    account_id: str = None,
    skip: int = 0,
    limit: int = 100,
    is_read: bool = None,
    category: str = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve emails, optionally filtered by account, read status, and category.
    """
    # Build query
    filters = []
    
    # Get email accounts for current user
    accounts_query = select(EmailAccountModel.id).where(
        EmailAccountModel.user_id == current_user.id
    )
    result = await db.execute(accounts_query)
    account_ids = [row[0] for row in result]
    
    if not account_ids:
        # User has no accounts
        return []
    
    # Filter by account_id if provided, otherwise use all user's accounts
    if account_id:
        if account_id not in account_ids:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access to this email account is not permitted",
            )
        filters.append(EmailModel.email_account_id == account_id)
    else:
        filters.append(EmailModel.email_account_id.in_(account_ids))
    
    if is_read is not None:
        filters.append(EmailModel.is_read == is_read)
        
    if category:
        filters.append(EmailModel.category == category)
    
    # Combine filters and execute query
    query = select(EmailModel).where(
        and_(*filters)
    ).order_by(EmailModel.date_received.desc()).offset(skip).limit(limit)
    
    result = await db.execute(query)
    emails = result.scalars().all()
    
    # Process for response: create a list with attachments properly loaded
    response_emails = []
    for email in emails:
        # Create a dict representation with empty attachments list
        email_dict = {
            "id": email.id,
            "email_account_id": email.email_account_id,
            "message_id": email.message_id,
            "subject": email.subject,
            "sender": email.sender,
            "recipients": email.recipients,
            "date_received": email.date_received,
            "body_text": email.body_text,
            "body_html": email.body_html,
            "is_read": email.is_read,
            "category": email.category,
            "created_at": email.created_at,
            "attachments": []
        }
        response_emails.append(email_dict)
    
    return response_emails

@router.get("/{email_id}", response_model=Email)
async def read_email(
    email_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get a specific email by id.
    """
    # First check if the email exists
    email_query = select(EmailModel).where(EmailModel.id == email_id)
    result = await db.execute(email_query)
    email = result.scalars().first()
    
    if not email:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email not found",
        )
    
    # Then verify the user has access to this email's account
    account_query = select(EmailAccountModel).where(
        EmailAccountModel.id == email.email_account_id,
        EmailAccountModel.user_id == current_user.id
    )
    result = await db.execute(account_query)
    account = result.scalars().first()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access to this email is not permitted",
        )
    
    # Mark as read if not already
    if not email.is_read:
        email.is_read = True
        await db.commit()
    
    # Get attachments explicitly
    attachments_query = select(Attachment).where(Attachment.email_id == email.id)
    attachments_result = await db.execute(attachments_query)
    attachments = attachments_result.scalars().all()
    
    # Create a dict representation with loaded attachments
    email_dict = {
        "id": email.id,
        "email_account_id": email.email_account_id,
        "message_id": email.message_id,
        "subject": email.subject,
        "sender": email.sender,
        "recipients": email.recipients,
        "date_received": email.date_received,
        "body_text": email.body_text,
        "body_html": email.body_html,
        "is_read": email.is_read,
        "category": email.category,
        "created_at": email.created_at,
        "attachments": [
            {
                "id": att.id,
                "email_id": att.email_id,
                "filename": att.filename,
                "content_type": att.content_type,
                "file_path": att.file_path,
                "size": att.size,
                "created_at": att.created_at
            }
            for att in attachments
        ]
    }
    
    return email_dict

@router.patch("/{email_id}/read", response_model=Email)
async def mark_email_as_read(
    email_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Mark an email as read.
    """
    # First check if the email exists
    email_query = select(EmailModel).where(EmailModel.id == email_id)
    result = await db.execute(email_query)
    email = result.scalars().first()
    
    if not email:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email not found",
        )
    
    # Then verify the user has access to this email's account
    account_query = select(EmailAccountModel).where(
        EmailAccountModel.id == email.email_account_id,
        EmailAccountModel.user_id == current_user.id
    )
    result = await db.execute(account_query)
    account = result.scalars().first()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access to this email is not permitted",
        )
    
    # Mark as read
    email.is_read = True
    await db.commit()
    await db.refresh(email)
    
    # Get attachments explicitly
    attachments_query = select(Attachment).where(Attachment.email_id == email.id)
    attachments_result = await db.execute(attachments_query)
    attachments = attachments_result.scalars().all()
    
    # Create a dict representation with loaded attachments
    email_dict = {
        "id": email.id,
        "email_account_id": email.email_account_id,
        "message_id": email.message_id,
        "subject": email.subject,
        "sender": email.sender,
        "recipients": email.recipients,
        "date_received": email.date_received,
        "body_text": email.body_text,
        "body_html": email.body_html,
        "is_read": email.is_read,
        "category": email.category,
        "created_at": email.created_at,
        "attachments": [
            {
                "id": att.id,
                "email_id": att.email_id,
                "filename": att.filename,
                "content_type": att.content_type,
                "file_path": att.file_path,
                "size": att.size,
                "created_at": att.created_at
            }
            for att in attachments
        ]
    }
    
    return email_dict

@router.patch("/{email_id}/unread", response_model=Email)
async def mark_email_as_unread(
    email_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Mark an email as unread.
    """
    # First check if the email exists
    email_query = select(EmailModel).where(EmailModel.id == email_id)
    result = await db.execute(email_query)
    email = result.scalars().first()
    
    if not email:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email not found",
        )
    
    # Then verify the user has access to this email's account
    account_query = select(EmailAccountModel).where(
        EmailAccountModel.id == email.email_account_id,
        EmailAccountModel.user_id == current_user.id
    )
    result = await db.execute(account_query)
    account = result.scalars().first()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access to this email is not permitted",
        )
    
    # Mark as unread
    email.is_read = False
    await db.commit()
    await db.refresh(email)
    
    # Get attachments explicitly
    attachments_query = select(Attachment).where(Attachment.email_id == email.id)
    attachments_result = await db.execute(attachments_query)
    attachments = attachments_result.scalars().all()
    
    # Create a dict representation with loaded attachments
    email_dict = {
        "id": email.id,
        "email_account_id": email.email_account_id,
        "message_id": email.message_id,
        "subject": email.subject,
        "sender": email.sender,
        "recipients": email.recipients,
        "date_received": email.date_received,
        "body_text": email.body_text,
        "body_html": email.body_html,
        "is_read": email.is_read,
        "category": email.category,
        "created_at": email.created_at,
        "attachments": [
            {
                "id": att.id,
                "email_id": att.email_id,
                "filename": att.filename,
                "content_type": att.content_type,
                "file_path": att.file_path,
                "size": att.size,
                "created_at": att.created_at
            }
            for att in attachments
        ]
    }
    
    return email_dict

@router.patch("/{email_id}/category", response_model=Email)
async def update_email_category(
    email_id: str,
    category: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Update the category of an email.
    """
    # First check if the email exists
    email_query = select(EmailModel).where(EmailModel.id == email_id)
    result = await db.execute(email_query)
    email = result.scalars().first()
    
    if not email:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email not found",
        )
    
    # Then verify the user has access to this email's account
    account_query = select(EmailAccountModel).where(
        EmailAccountModel.id == email.email_account_id,
        EmailAccountModel.user_id == current_user.id
    )
    result = await db.execute(account_query)
    account = result.scalars().first()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access to this email is not permitted",
        )
    
    # Update the category
    email.category = category
    await db.commit()
    await db.refresh(email)
    
    # Get attachments explicitly
    attachments_query = select(Attachment).where(Attachment.email_id == email.id)
    attachments_result = await db.execute(attachments_query)
    attachments = attachments_result.scalars().all()
    
    # Create a dict representation with loaded attachments
    email_dict = {
        "id": email.id,
        "email_account_id": email.email_account_id,
        "message_id": email.message_id,
        "subject": email.subject,
        "sender": email.sender,
        "recipients": email.recipients,
        "date_received": email.date_received,
        "body_text": email.body_text,
        "body_html": email.body_html,
        "is_read": email.is_read,
        "category": email.category,
        "created_at": email.created_at,
        "attachments": [
            {
                "id": att.id,
                "email_id": att.email_id,
                "filename": att.filename,
                "content_type": att.content_type,
                "file_path": att.file_path,
                "size": att.size,
                "created_at": att.created_at
            }
            for att in attachments
        ]
    }
    
    return email_dict 