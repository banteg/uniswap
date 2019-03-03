from datetime import datetime
from dataclasses import dataclass, astuple

from uniwatch.db import db


@dataclass
class Exchange:
    token: str
    exchange: str
    block: int
    symbol: str = None
    decimals: str = None

    @classmethod
    def from_log(cls, log):
        return cls(token=log.args.token, exchange=log.args.exchange, block=log.blockNumber)

    async def save(self):
        await db.execute(
            'insert into exchanges (token, exchange, block, symbol, decimals) values ($1, $2, $3, $4, $5)',
            *astuple(self)
        )


@dataclass
class Event:
    exchange: str
    event: str
    data: dict
    block: int
    log_index: int
    ts: datetime = None

    @classmethod
    def from_log(cls, log):
        return cls(log.address, log.event, dict(log.args), log.blockNumber, log.logIndex)

    async def save(self):
        await db.execute(
            'insert into events (exchange, event, data, block, log_index, ts) values ($1, $2, $3, $4, $5, $6)',
            *astuple(self)
        )
