import logging
from app.consumers.reset_password_consumer import start_consuming

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("Starting notification micro-service...")
    start_consuming()