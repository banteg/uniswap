from dataclasses import dataclass, astuple

from uniwatch.db import db


@dataclass
class Exchange:
    token: str
    exchange: str
    block: int

    @classmethod
    def from_log(cls, log):
        return cls(token=log.args.token, exchange=log.args.exchange, block=log.blockNumber)

    async def save(self):
        await db.execute(
            'insert into exchanges (token, exchange, block) values ($1, $2, $3)',
            *astuple(self)
        )

    async def update_last_block(self, block):
        await db.execute('update exchanges set last_block = $2 where exchange = $1', self.exchange, block)


@dataclass
class Event:
    exchange: str
    event: str
    data: dict
    block: int
    log_index: int

    @classmethod
    def from_log(cls, log):
        return cls(log.address, log.event, dict(log.args), log.blockNumber, log.logIndex)

    async def save(self):
        await db.execute(
            'insert into events (exchange, event, data, block, log_index) values ($1, $2, $3, $4, $5)',
            *astuple(self)
        )
