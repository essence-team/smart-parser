import logging
from contextlib import asynccontextmanager

from core.config import main_config
from core.config.models.database import DatabaseConfig
from models.base import Base
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# from core.logger import main_logger
main_logger = logging.getLogger("app")


class AsyncDatabaseSession:
    def __init__(self, cfg: DatabaseConfig, logger: logging.Logger):
        self._session_factory = None
        self._engine = None
        self.cfg = cfg
        self.logger = logger

    async def init(self):
        try:
            self._engine = create_async_engine(
                url=(
                    f"postgresql+asyncpg://{self.cfg.db_user}:{self.cfg.db_password}"
                    f"@{self.cfg.db_host}:{self.cfg.db_port}/{self.cfg.db_name}"
                ),
                future=True,
                echo=False,
                pool_size=20,
                max_overflow=10,
                pool_timeout=30,
                pool_recycle=1800,
                pool_pre_ping=True,
            )
            self._session_factory = sessionmaker(self._engine, expire_on_commit=False, class_=AsyncSession)
            self.logger.debug("Database engine and session factory initialized successfully.")

            await self._check_connection()

        except Exception as e:
            self.logger.error(f"Error initializing database engine: {e}", exc_info=True)
            raise

    @asynccontextmanager
    async def get_session(self):
        session = self._session_factory()
        try:
            yield session
            self.logger.debug("Session used successfully.")
        except Exception as e:
            self.logger.error(f"Error during session usage: {e}", exc_info=True)
            raise
        finally:
            try:
                await session.close()
                self.logger.debug("Session closed successfully.")
            except Exception as e:
                self.logger.error(f"Error closing session: {e}", exc_info=True)

    async def create_all(self):
        try:
            async with self._engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            self.logger.debug("All tables created successfully.")
        except Exception as e:
            self.logger.error(f"Error creating tables: {e}", exc_info=True)
            raise

    async def close(self):
        try:
            if self._engine:
                await self._engine.dispose()
                self.logger.debug("Engine disposed successfully.")
        except Exception as e:
            self.logger.error(f"Error during close method: {e}", exc_info=True)

    async def _check_connection(self):
        try:
            async with self._engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
                self.logger.debug("Connection to the database is successful.")
        except Exception as e:
            self.logger.error(f"Failed to connect to the database: {e}", exc_info=True)
            raise


database = AsyncDatabaseSession(main_config.database, logger=main_logger)


async def initialize_database():
    await database.init()
    await database.create_all()


async def close_db_connection():
    await database.close()


async def get_db_session():
    async with database.get_session() as session:
        yield session
