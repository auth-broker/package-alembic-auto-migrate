"""Tests for AlembicAutoMigrate service."""

import sys

import pytest
from sqlalchemy import inspect
from sqlmodel import SQLModel

from ab_core.alembic_auto_migrate.service import AlembicAutoMigrate
from ab_core.database.databases import Database


@pytest.mark.asyncio
async def test_run_no_models(
    tmp_database_async: Database,
    alembic_auto_migrate_service: AlembicAutoMigrate,
):
    """No models imported => no diffs => no revision."""
    created = await alembic_auto_migrate_service.run(tmp_database_async.async_engine)
    assert created is None


@pytest.mark.asyncio
async def test_run_with_models_import_creates_revision_and_table(
    tmp_database_async: Database,
    alembic_auto_migrate_service: AlembicAutoMigrate,
):
    """Import static models via ALEMBIC_MODELS_IMPORT so autogenerate sees diffs."""
    # --- 1) Import v1 models (id, name), migrate ---
    import tests.sample_sql_models.v1  # noqa registers tables in SQLModel.metadata

    created_v1 = await alembic_auto_migrate_service.run(tmp_database_async.async_engine)
    assert created_v1 is not None  # first revision created

    # Verify table exists and only has id, name
    async with tmp_database_async.async_engine.begin() as aconn:

        def _cols(sync_conn):
            insp = inspect(sync_conn)
            cols = [c["name"] for c in insp.get_columns("gadgets")]
            return cols

        cols_v1 = await aconn.run_sync(_cols)

    assert "gadgets" in {"gadgets"}  # sanity
    assert set(cols_v1) == {"id", "name"}

    # --- 2) Clear SQLModel metadata, import v2 models (adds description), migrate again ---
    # Remove v1 module to avoid caching, clear metadata so v2 re-defines the table
    SQLModel.metadata.clear()
    sys.modules.pop("tests.sample_sql_models", None)

    # Import v2 (id, name, description)
    import tests.sample_sql_models.v2  # noqa registers tables in SQLModel.metadata

    created_v2 = await alembic_auto_migrate_service.run(tmp_database_async.async_engine)
    assert created_v2 is not None  # a new revision for the new column

    # Verify new column exists
    async with tmp_database_async.async_engine.begin() as aconn:

        def _cols(sync_conn):
            insp = inspect(sync_conn)
            cols = [c["name"] for c in insp.get_columns("gadgets")]
            return cols

        cols_v2 = await aconn.run_sync(_cols)

    assert set(cols_v2) == {"id", "name", "description"}

    # --- 3) Idempotency: running again with v2 should create no new revision ---
    created_again = await alembic_auto_migrate_service.run(tmp_database_async.async_engine)
    assert created_again is None
