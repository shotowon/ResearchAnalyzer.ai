from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    create_async_engine,
    AsyncEngine,
    AsyncSession,
)


class DB:
    def __init__(self, dsn: str, echo: bool) -> None:
        self.engine: AsyncEngine = create_async_engine(dsn, echo=echo)
        self.session_maker: async_sessionmaker[AsyncSession] = async_sessionmaker(
            self.engine,
            expire_on_commit=False,
            class_=AsyncSession,
        )
