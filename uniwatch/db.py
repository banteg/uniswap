import json
from pathlib import Path
from functools import partial

import asyncpg

from uniwatch.config import config


class DB:

    def __init__(self):
        self.pool = None

    async def init(self, dsn=None):
        dsn = dsn if dsn else config.postgres
        self.pool = await asyncpg.create_pool(dsn, init=self.codecs)
        await self.migrate()

    def __getattr__(self, item):
        return getattr(self.pool, item)

    async def migrate(self):
        await db.execute('create table if not exists migrations (version text, ts timestamptz)')
        done = {row['version'] for row in await db.fetch('select * from migrations')}
        for f in sorted(Path('migrations').glob('*.sql')):
            if f.name in done:
                continue
            print(f'migrate: {f.name}')
            await db.execute(f.read_text())
            await db.execute('insert into migrations (version, ts) values ($1, now())', f.name)

    @staticmethod
    async def codecs(conn: asyncpg.Connection):
        await conn.set_type_codec(
            'json',
            encoder=partial(json.dumps, ensure_ascii=False),
            decoder=json.loads,
            schema='pg_catalog',
            format='text'
        )


db = DB()
