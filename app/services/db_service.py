from pymongo import MongoClient
from pymongo.errors import PyMongoError
from app.config.settings import settings
from app.models.message import ResetPasswordMessage
from datetime import datetime, timezone

client = MongoClient(settings.MONGODB_URL)

db = client["notification_service"]

collection = db["reset_password_messages"]

def save_message(session, message: ResetPasswordMessage):
    collection.insert_one(
        {
            "_id": str(message.id),
            "user_id": message.user_id,
            "email_address": message.email_address,
            "subject": message.subject,
            "body": message.body,
            "published_at": message.published_at,
            "sent_at": None,
        },
        session=session,
    )
def mark_as_sent(session, message_id: str):
    collection.update_one(
        {"_id": message_id},
        {"$set": {"sent_at": datetime.now(timezone.utc)}},
        session=session,
    )