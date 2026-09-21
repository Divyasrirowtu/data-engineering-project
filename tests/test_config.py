from config.settings import (
    POSTGRES_DB,
    POSTGRES_USER,
    POSTGRES_PASSWORD,
    POSTGRES_HOST,
    POSTGRES_PORT,
    KAFKA_BROKER,
    KAFKA_TOPIC,
    validate_settings,
)


def test_required_settings_are_loaded():
    assert validate_settings() is True


def test_postgres_settings():
    assert POSTGRES_DB == "data_engineering"
    assert POSTGRES_USER == "postgres"
    assert POSTGRES_PASSWORD == "postgres"
    assert POSTGRES_HOST == "postgres"
    assert POSTGRES_PORT == "5432"


def test_kafka_settings():
    assert KAFKA_BROKER == "kafka:9092"
    assert KAFKA_TOPIC == "orders"