import asyncio

from aiomysql.sa import create_engine, result
from sqlalchemy import MetaData, Table, Column, BigInteger, String, Boolean, BLOB, Integer


jobs_table = Table(
    'jobs',
    MetaData(),
    Column('id', BigInteger, primary_key=True, nullable=False),
    Column('target', String(50), nullable=False),
    Column('url', String(2048), nullable=True),
    Column('query', String(2048), nullable=True),
    Column('geo_location', String(150), nullable=True),
    Column('domain', String(9), nullable=True),
    Column('parse', Boolean),
    Column('status', String(50)),
)


job_results_table = Table(
    'job_results',
    MetaData(),
    Column('id', BigInteger, primary_key=True, nullable=False),
    Column('internal_id', BigInteger, nullable=False),
    Column('job_id', BigInteger, nullable=False),
    Column('content', BLOB),
    Column('page', Integer),
    Column('url', String(2048)),
)


class Session:

    def __init__(
            self,
            user: str,
            password: str,
            host: str,
            port: int,
            database: str,
    ) -> None:
        self._loop = asyncio.get_event_loop()
        self._user = user
        self._password = password
        self._host = host
        self._port = port
        self._database = database

        self._engine = None
        self._id = id(self)

    async def __aenter__(self):
        await self.open()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()

    async def open(self) -> None:
        self._engine = await create_engine(
            loop=self._loop,
            db=self._database,
            host=self._host,
            port=self._port,
            user=self._user,
            password=self._password,
            charset='utf8mb4',
            use_unicode=True,
        )

    async def close(self) -> None:
        if self._engine:
            self._engine.close()
            await self._engine.wait_closed()
            self._engine = None

    async def exec(self, query) -> result.ResultProxy:
        async with self._engine.acquire() as conn:
            res = await conn.execute(query)
            await conn.execute('commit')
            return res

    async def insert(self, table, values):
        if not self._engine:
            await self.open()
        await self.exec(table.insert().values(values))
        await self.close()
