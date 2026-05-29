import boto3
from app.config.settings import settings

client = boto3.client(
    "ses",
    region_name=settings.AWS_REGION,
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
)
def send_email(to: str, subject: str, body: str):
    client.send_email(
        Source=settings.SES_SENDER_EMAIL,
        Destination={"ToAddresses": [to]},
        Message={
            "Subject": {"Data": subject},
            "Body": {"Text": {"Data": body}},
        },
    )