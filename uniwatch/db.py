from pathlib import Path

import asyncpg

from uniwatch.config import config


class DB:

    def __init__(self):
        self.pool = None

    async def init(self, dsn=None):
        dsn = dsn if dsn else config.postgres
        self.pool = await asyncpg.create_pool(dsn)
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


db = DB()
