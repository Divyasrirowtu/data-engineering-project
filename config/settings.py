import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")


POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")

POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")

if POSTGRES_HOST == "postgres" and os.getenv("RUNNING_IN_DOCKER") != "true":
    POSTGRES_HOST = "localhost"

POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:29092")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "orders")


def validate_settings():
    required_settings = {
        "POSTGRES_DB": POSTGRES_DB,
        "POSTGRES_USER": POSTGRES_USER,
        "POSTGRES_PASSWORD": POSTGRES_PASSWORD,
        "POSTGRES_HOST": POSTGRES_HOST,
        "POSTGRES_PORT": POSTGRES_PORT,
        "KAFKA_BROKER": KAFKA_BROKER,
        "KAFKA_TOPIC": KAFKA_TOPIC,
    }

    missing_settings = [
        name
        for name, value in required_settings.items()
        if not value
    ]

    if missing_settings:
        raise ValueError(
            "Missing environment variables: "
            + ", ".join(missing_settings)
        )

    return True