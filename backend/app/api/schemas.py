from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

# Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenPayload(BaseModel):
    sub: Optional[str] = None

# User schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None

class UserInDB(UserBase):
    id: str
    is_active: bool
    is_admin: bool
    created_at: datetime

    class Config:
        from_attributes = True

class User(UserInDB):
    pass

# Email account schemas
class EmailAccountBase(BaseModel):
    email_address: EmailStr

class EmailAccountCreate(EmailAccountBase):
    refresh_token: str
    client_id: str

class EmailAccountInDB(EmailAccountBase):
    id: str
    user_id: str
    last_sync: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True

class EmailAccount(EmailAccountInDB):
    pass

# Email schemas
class EmailBase(BaseModel):
    subject: Optional[str] = None
    sender: str
    recipients: str
    date_received: datetime
    is_read: bool = False
    category: str = "inbox"

class EmailCreate(EmailBase):
    email_account_id: str
    message_id: str
    body_text: Optional[str] = None
    body_html: Optional[str] = None

class EmailInDB(EmailBase):
    id: str
    email_account_id: str
    message_id: str
    body_text: Optional[str] = None
    body_html: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class Email(EmailInDB):
    attachments: List["Attachment"] = []

# Attachment schemas
class AttachmentBase(BaseModel):
    filename: str
    content_type: str
    size: int

class AttachmentCreate(AttachmentBase):
    email_id: str
    file_path: str

class AttachmentInDB(AttachmentBase):
    id: str
    email_id: str
    file_path: str
    created_at: datetime

    class Config:
        from_attributes = True

class Attachment(AttachmentInDB):
    pass

# Update forward references
Email.model_rebuild()

# Bulk import schema
class BulkEmailImport(BaseModel):
    email_accounts: List[str] = Field(..., description="List of email accounts in the format 'email----password----refreshToken----clientId' where '----' is the separator") 