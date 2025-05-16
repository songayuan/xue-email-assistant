from fastapi import APIRouter

from app.api.api_v1.endpoints import auth, users, emails, email_accounts

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(email_accounts.router, prefix="/email-accounts", tags=["email-accounts"])
api_router.include_router(emails.router, prefix="/emails", tags=["emails"]) 