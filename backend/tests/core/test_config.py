from app.core.config import Settings


def test_default_sqlalchemy_database_uri():
    s = Settings(_env_file=None)

    assert s.SQLALCHEMY_DATABASE_URI == (
        "postgresql+asyncpg://repstash_user:repstash_password@localhost:5433/repstash"
    )


def test_default_redis_url():
    s = Settings(_env_file=None)

    assert s.REDIS_URL == "redis://localhost:6379"


def test_overridden_fields_change_computed_uris():
    s = Settings(
        _env_file=None,
        POSTGRES_SERVER="db.internal",
        POSTGRES_USER="custom_user",
        POSTGRES_PASSWORD="custom_pass",
        POSTGRES_PORT=1234,
        POSTGRES_DB="custom_db",
        REDIS_HOST="redis-test",
        REDIS_PORT=6380,
    )

    assert s.SQLALCHEMY_DATABASE_URI == "postgresql+asyncpg://custom_user:custom_pass@db.internal:1234/custom_db"
    assert s.REDIS_URL == "redis://redis-test:6380"
