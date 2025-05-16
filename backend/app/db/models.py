from sqlalchemy import Boolean, Column, String, Integer, ForeignKey, Text, DateTime, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

Base = declarative_base()

def generate_uuid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True, default=generate_uuid)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    email_accounts = relationship("EmailAccount", back_populates="user", cascade="all, delete-orphan")

class EmailAccount(Base):
    __tablename__ = "email_accounts"

    id = Column(String, primary_key=True, index=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"))
    email_address = Column(String, index=True)
    refresh_token = Column(String)
    client_id = Column(String)
    last_sync = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="email_accounts")
    emails = relationship("Email", back_populates="email_account", cascade="all, delete-orphan")

class Email(Base):
    __tablename__ = "emails"

    id = Column(String, primary_key=True, index=True, default=generate_uuid)
    email_account_id = Column(String, ForeignKey("email_accounts.id", ondelete="CASCADE"))
    message_id = Column(String, index=True)  # Email message ID for deduplication
    subject = Column(String)
    sender = Column(String)
    recipients = Column(String)
    date_received = Column(DateTime(timezone=True))
    body_text = Column(Text)
    body_html = Column(Text)
    is_read = Column(Boolean, default=False)
    category = Column(String, default="inbox", index=True)  # Email category/label
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    email_account = relationship("EmailAccount", back_populates="emails")
    attachments = relationship("Attachment", back_populates="email", cascade="all, delete-orphan")

class Attachment(Base):
    __tablename__ = "attachments"

    id = Column(String, primary_key=True, index=True, default=generate_uuid)
    email_id = Column(String, ForeignKey("emails.id", ondelete="CASCADE"))
    filename = Column(String)
    content_type = Column(String)
    file_path = Column(String)  # Path to stored attachment
    size = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    email = relationship("Email", back_populates="attachments") 