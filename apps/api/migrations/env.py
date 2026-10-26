from alembic import context
from sqlalchemy import create_engine, pool

from report_api import saved_report_schema
from report_api.settings import ReportSettings

target_metadata = saved_report_schema.SavedReport.metadata
config = context.config


def run_migrations() -> None:
    url = config.attributes.get("database_url") or ReportSettings().database_url
    if context.is_offline_mode():
        context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
        with context.begin_transaction():
            context.run_migrations()
        return
    engine = create_engine(url, poolclass=pool.NullPool, hide_parameters=True)
    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata, compare_type=True)
        with context.begin_transaction():
            context.run_migrations()
    engine.dispose()


run_migrations()
