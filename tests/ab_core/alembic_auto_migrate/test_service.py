"""Tests for AlembicAutoMigrate service."""

import pytest

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
    # this import updates sqlmodel.SQLModel.metadata globally, so the env.py
    # will see the models when it imports this module
    import tests.sample_sql_models  # noqa: F401

    # this will create a new revision and apply it to the database
    created = await alembic_auto_migrate_service.run(tmp_database_async.async_engine)

    assert created is not None

    # Verify the table exists
    async with tmp_database_async.async_engine.begin() as aconn:

        def _check(sync_conn):
            from sqlalchemy import inspect as _inspect

            insp = _inspect(sync_conn)
            return "gadgets" in insp.get_table_names()

        assert await aconn.run_sync(_check)

    # Idempotency: running again should produce no new revision
    created_again = await alembic_auto_migrate_service.run(tmp_database_async.async_engine)

    assert created_again is None
