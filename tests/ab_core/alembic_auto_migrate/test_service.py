"""Tests for AlembicAutoMigrate service."""

import sys

from sqlalchemy import inspect
from sqlmodel import SQLModel

from ab_core.alembic_auto_migrate.service import AlembicAutoMigrate
from ab_core.database.databases import Database


def test_run_no_models(
    alembic_service_and_db: tuple[AlembicAutoMigrate, Database],
):
    """No models imported => no diffs => no revision."""
    alembic_service, _ = alembic_service_and_db
    created = alembic_service.run()
    assert created is None


def test_run_with_models(
    alembic_service_and_db: tuple[AlembicAutoMigrate, Database],
):
    """Import static models via ALEMBIC_MODELS_IMPORT so autogenerate sees diffs."""
    alembic_service, db = alembic_service_and_db

    # --- 1) Import v1 models (id, name), migrate ---
    import tests.sample_sql_models.v1  # noqa registers tables in SQLModel.metadata

    created_v1 = alembic_service.run()
    assert created_v1 is not None  # first revision created

    # Verify table exists and only has id, name
    with db.sync_engine.begin() as conn:
        insp = inspect(conn)
        cols_v1 = [c["name"] for c in insp.get_columns("gadgets")]

    assert "gadgets" in {"gadgets"}  # sanity
    assert set(cols_v1) == {"id", "name"}

    # --- 2) Clear SQLModel metadata, import v2 models (adds description), migrate again ---
    # Remove v1 module to avoid caching, clear metadata so v2 re-defines the table
    SQLModel.metadata.clear()
    sys.modules.pop("tests.sample_sql_models", None)

    # Import v2 (id, name, description)
    import tests.sample_sql_models.v2  # noqa registers tables in SQLModel.metadata

    created_v2 = alembic_service.run()
    assert created_v2 is not None  # a new revision for the new column

    # Verify new column exists
    with db.sync_engine.begin() as conn:
        insp = inspect(conn)
        cols_v2 = [c["name"] for c in insp.get_columns("gadgets")]

    assert set(cols_v2) == {"id", "name", "description"}

    # --- 3) Idempotency: running again with v2 should create no new revision ---
    created_again = alembic_service.run()
    assert created_again is None
