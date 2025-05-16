import base64
import imaplib
import requests
import email as email_module
from email.header import decode_header
from email.parser import BytesParser
import os
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import AsyncSessionLocal
from app.db.models import EmailAccount, Email, Attachment

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def get_access_token(client_id: str, refresh_token: str) -> str:
    """Get access token from refresh token"""
    data = {
        'client_id': client_id,
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
        'redirect_uri': 'http://localhost:8000/auth/callback',
        'scope': 'offline_access https://outlook.office.com/IMAP.AccessAsUser.All'
    }
    
    try:
        response = requests.post('https://login.live.com/oauth20_token.srf', data=data)
        if response.status_code != 200:
            logger.error(f"OAuth error: {response.status_code} {response.text}")
            logger.error(f"Request data: {data}")
        response.raise_for_status()
        return response.json()['access_token']
    except Exception as e:
        logger.error(f"Error getting access token: {str(e)}")
        raise

def generate_auth_string(user: str, token: str) -> str:
    """Generate OAuth2 authentication string"""
    auth_string = f"user={user}\1auth=Bearer {token}\1\1"
    return auth_string

async def process_email_message(
    msg: email_module.message.Message,
    email_account_id: str,
    db: AsyncSession
) -> Optional[Email]:
    """Process a single email message and save to database"""
    try:
        # Extract message ID
        message_id = msg.get("Message-ID", "")
        
        # Check if this email already exists in the database
        if message_id:
            query = select(Email).where(
                Email.message_id == message_id,
                Email.email_account_id == email_account_id
            )
            result = await db.execute(query)
            if result.scalars().first():
                # Email already exists, skip processing
                return None
        
        # Get subject
        subject = decode_header(msg.get("Subject", ""))
        if subject[0][1] is not None:
            # If encoded, decode according to encoding
            subject = subject[0][0].decode(subject[0][1])
        else:
            # Otherwise get subject directly
            subject = subject[0][0]
            if isinstance(subject, bytes):
                subject = subject.decode('utf-8', errors='replace')
        
        # Get sender
        from_ = decode_header(msg.get("From", ""))
        if from_[0][1] is not None:
            from_ = from_[0][0].decode(from_[0][1])
        else:
            from_ = from_[0][0]
            if isinstance(from_, bytes):
                from_ = from_.decode('utf-8', errors='replace')
        
        # Get recipients
        to = msg.get("To", "")
        
        # Get date
        date_str = msg.get("Date", "")
        try:
            # Try to parse the date
            date_received = email_module.utils.parsedate_to_datetime(date_str)
        except:
            # If parsing fails, use current time
            date_received = datetime.now()
        
        # Get email content
        email_body = ""
        html_body = ""
        
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))
                
                # Skip attachments for now
                if "attachment" in content_disposition:
                    continue
                
                try:
                    if content_type == "text/plain":
                        body = part.get_payload(decode=True)
                        charset = part.get_content_charset()
                        if charset:
                            body = body.decode(charset, errors='replace')
                        else:
                            body = body.decode('utf-8', errors='replace')
                        email_body = body
                    elif content_type == "text/html":
                        body = part.get_payload(decode=True)
                        charset = part.get_content_charset()
                        if charset:
                            body = body.decode(charset, errors='replace')
                        else:
                            body = body.decode('utf-8', errors='replace')
                        html_body = body
                except Exception as e:
                    logger.error(f"Error decoding email part: {str(e)}")
        else:
            # Not multipart
            content_type = msg.get_content_type()
            try:
                body = msg.get_payload(decode=True)
                charset = msg.get_content_charset()
                if charset:
                    body = body.decode(charset, errors='replace')
                else:
                    body = body.decode('utf-8', errors='replace')
                    
                if content_type == "text/plain":
                    email_body = body
                elif content_type == "text/html":
                    html_body = body
            except Exception as e:
                logger.error(f"Error decoding email content: {str(e)}")
        
        # Determine category based on email properties
        category = categorize_email(subject, from_, email_body)
        
        # Create and save email
        email = Email(
            email_account_id=email_account_id,
            message_id=message_id,
            subject=subject,
            sender=from_,
            recipients=to,
            date_received=date_received,
            body_text=email_body,
            body_html=html_body,
            is_read=False,
            category=category
        )
        
        db.add(email)
        await db.commit()
        await db.refresh(email)
        
        # Process attachments if any
        if msg.is_multipart():
            attachments_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "attachments")
            os.makedirs(attachments_dir, exist_ok=True)
            
            for part in msg.walk():
                if part.get_content_disposition() == 'attachment':
                    filename = part.get_filename()
                    if not filename:
                        continue
                    
                    # Sanitize filename
                    filename = os.path.basename(filename)
                    
                    # Create a unique path
                    file_path = os.path.join(attachments_dir, f"{email.id}_{filename}")
                    
                    # Save attachment
                    with open(file_path, 'wb') as f:
                        f.write(part.get_payload(decode=True))
                    
                    # Create attachment record
                    attachment = Attachment(
                        email_id=email.id,
                        filename=filename,
                        content_type=part.get_content_type(),
                        file_path=file_path,
                        size=os.path.getsize(file_path)
                    )
                    
                    db.add(attachment)
            
            await db.commit()
        
        return email
    except Exception as e:
        logger.error(f"Error processing email: {str(e)}")
        return None

def categorize_email(subject: str, sender: str, body: str) -> str:
    """
    Categorize email based on content
    
    Categories:
    - inbox: Default category
    - important: Important emails
    - social: Social network notifications
    - promotions: Marketing emails
    - updates: Updates and notifications
    - forums: Forum posts and mailing lists
    - spam: Potential spam
    """
    subject_lower = subject.lower()
    sender_lower = sender.lower()
    
    # Check for social media related emails
    social_terms = ['facebook', 'twitter', 'instagram', 'linkedin', 'weibo', 'wechat', 'qq', 'tiktok']
    if any(term in sender_lower or term in subject_lower for term in social_terms):
        return "social"

    # Check for promotions/marketing
    promo_terms = ['promotion', 'discount', 'sale', 'off', 'deal', 'offer', '促销', '优惠', '折扣']
    if any(term in subject_lower for term in promo_terms):
        return "promotions"
    
    # Check for updates/notifications
    update_terms = ['update', 'notification', 'confirm', 'verify', 'security', '更新', '通知']
    if any(term in subject_lower for term in update_terms):
        return "updates"
    
    # Check for potential spam
    spam_terms = ['urgent', 'winner', 'won', 'prize', 'lottery', 'million', 'bitcoin', 'invest']
    if any(term in subject_lower for term in spam_terms):
        return "spam"
    
    # Check for important emails
    important_terms = ['important', 'urgent', 'attention', 'required', 'action', '重要', '紧急']
    if any(term in subject_lower for term in important_terms):
        return "important"
    
    # Default category
    return "inbox"

async def connect_imap(email_addr: str, access_token: str, email_account_id: str, user_id: str):
    """Connect to IMAP server and fetch emails"""
    try:
        # 在函数内部导入而不是在模块顶部
        from app.main import manager
        
        logger.info(f"Connecting to IMAP server for {email_addr}")
        
        # Connect to server
        mail = imaplib.IMAP4_SSL('outlook.office365.com')
        
        # Authenticate
        auth_string = generate_auth_string(email_addr, access_token)
        logger.info(f"Authenticating {email_addr} with OAuth2")
        
        try:
            auth_result = mail.authenticate('XOAUTH2', lambda x: auth_string)
            logger.info(f"Authentication result: {auth_result}")
        except Exception as auth_err:
            logger.error(f"Authentication error for {email_addr}: {str(auth_err)}")
            raise
        
        # Select inbox
        logger.info(f"Selecting INBOX for {email_addr}")
        select_result = mail.select("INBOX")
        logger.info(f"Select result: {select_result}")
        
        # Get all emails
        logger.info(f"Searching messages for {email_addr}")
        status, messages = mail.search(None, 'ALL')
        if status != 'OK':
            logger.error(f"Failed to search emails for {email_addr}: {status}")
            return
        
        message_ids = messages[0].split()
        logger.info(f"Found {len(message_ids)} messages in {email_addr}")
        
        # Process each email
        async with AsyncSessionLocal() as db:
            # Update last_sync time
            query = select(EmailAccount).where(EmailAccount.id == email_account_id)
            result = await db.execute(query)
            email_account = result.scalars().first()
            if email_account:
                email_account.last_sync = datetime.now()
                await db.commit()
            
            # Process emails in reverse order (newest first)
            new_emails = []
            for num in reversed(message_ids):
                status, data = mail.fetch(num, '(RFC822)')
                if status != 'OK':
                    logger.warning(f"Failed to fetch message {num} for {email_addr}: {status}")
                    continue
                
                raw_email = data[0][1]
                msg = email_module.message_from_bytes(raw_email)
                
                email = await process_email_message(msg, email_account_id, db)
                if email:
                    new_emails.append(email)
            
            # Notify via WebSocket if there are new emails
            if new_emails:
                logger.info(f"Processed {len(new_emails)} new emails for {email_addr}")
                for email in new_emails:
                    notification = {
                        "type": "new_email",
                        "data": {
                            "id": email.id,
                            "subject": email.subject,
                            "sender": email.sender,
                            "date": email.date_received.isoformat()
                        }
                    }
                    await manager.send_personal_message(notification, user_id)
            else:
                logger.info(f"No new emails found for {email_addr}")
        
        # Close the connection
        logger.info(f"Closing connection for {email_addr}")
        mail.close()
        mail.logout()
        
    except Exception as e:
        logger.error(f"Error in IMAP connection for {email_addr}: {str(e)}")
        # Don't raise, just log the error

async def fetch_emails_for_account(account_id: str, user_id: str):
    """Fetch emails for a specific account"""
    try:
        logger.info(f"Starting email fetch for account {account_id}")
        async with AsyncSessionLocal() as db:
            # Get account details
            query = select(EmailAccount).where(EmailAccount.id == account_id)
            result = await db.execute(query)
            account = result.scalars().first()
            
            if not account:
                logger.error(f"Account {account_id} not found")
                return
            
            logger.info(f"Fetching emails for {account.email_address}")
            
            try:
                # Get access token
                access_token = await get_access_token(account.client_id, account.refresh_token)
                logger.info(f"Successfully retrieved access token for {account.email_address}")
                
                # Fetch emails
                await connect_imap(account.email_address, access_token, account.id, user_id)
                logger.info(f"Email fetch completed for {account.email_address}")
            except Exception as token_error:
                logger.error(f"Failed to get access token for {account.email_address}: {str(token_error)}")
                # Update last_sync time with error status
                account.last_sync = datetime.now()
                await db.commit()
                # Re-raise to be caught by outer exception handler
                raise
            
    except Exception as e:
        logger.error(f"Error fetching emails for account {account_id}: {str(e)}")
        # Log stack trace for debugging
        import traceback
        logger.error(traceback.format_exc())

async def background_email_sync():
    """Background task to sync emails for all accounts periodically"""
    try:
        while True:
            async with AsyncSessionLocal() as db:
                # Get all active accounts
                query = select(EmailAccount)
                result = await db.execute(query)
                accounts = result.scalars().all()
                
                for account in accounts:
                    try:
                        await fetch_emails_for_account(account.id, account.user_id)
                    except Exception as e:
                        logger.error(f"Error syncing account {account.email_address}: {str(e)}")
                    
                    # Sleep briefly between accounts to avoid hammering the server
                    await asyncio.sleep(5)
            
            # Sleep for 5 minutes before checking again
            await asyncio.sleep(300)
    except Exception as e:
        logger.error(f"Error in background sync: {str(e)}")
        # Restart the task
        asyncio.create_task(background_email_sync()) 