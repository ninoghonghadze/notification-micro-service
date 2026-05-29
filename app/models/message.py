from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import datetime
from typing import Optional

class ResetPasswordMessage(BaseModel):
    id: UUID
    user_id: str
    email_address: EmailStr
    subject: str
    body: str
    published_at: datetime
    sent_at: Optional[datetime] = None