from dataclasses import dataclass


@dataclass
class Exchange:
    token: str
    exchange: str
    block: int

    @classmethod
    def from_log(cls, log):
        return cls(token=log.args.token, exchange=log.args.exchange, block=log.blockNumber)
