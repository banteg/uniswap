import asyncio
from itertools import count
from datetime import datetime, timezone

from uniwatch.db import db
from uniwatch.models import Exchange, Event
from uniwatch.config import config

from uniswap.factory import uniswap
from uniswap import abi

from tqdm import trange
from web3.auto import w3
from web3.utils.events import get_event_data
from eth_utils import event_abi_to_log_topic, encode_hex


topics_to_abi = {event_abi_to_log_topic(x): x for x in abi.exchange if x['type'] == 'event'}
topic_filter = [encode_hex(x) for x in topics_to_abi]


def decode_logs(logs):
    return [
        get_event_data(topics_to_abi[log['topics'][0]], log)
        for log in logs
    ]


def filter_params(address, from_block=None, to_block=None):
    return {
        'address': address,  # many addresses possible
        'fromBlock': from_block or config.genesis,
        'toBlock': to_block or 'latest',
        'topics': [topic_filter]
    }


async def fetch_events(addresses, from_block, to_block):
    params = filter_params(addresses, from_block, to_block)
    batch = w3.eth.getLogs(params)
    decoded = decode_logs(batch)
    events = [Event.from_log(log) for log in decoded]
    timestamps = {n: get_timestamp(n) for n in {x.block for x in events}}
    for event in events:
        event.ts = timestamps[event.block]
        await event.save()
    if events:
        print(f'+{len(events)} events')


async def fetch_new_exchanges(from_block=None) -> [Exchange]:
    last = from_block or await db.fetchval('select max(block) + 1 from exchanges') or uniswap.genesis
    new_exchanges = [
        Exchange.from_log(log) for log in
        uniswap.events.NewExchange.createFilter(fromBlock=last).get_all_entries()
    ]
    for exchange in new_exchanges:
        market = uniswap.get_exchange(exchange.token)
        exchange.symbol = market.token.symbol
        exchange.decimals = market.token.decimals
        await exchange.save()
        print(exchange)


async def get_exchanges() -> [Exchange]:
    exchanges = await db.fetch('select token, exchange, block, symbol, decimals from exchanges')
    return [Exchange(*row) for row in exchanges]


def get_timestamp(n):
    # TODO: make this async
    return datetime.fromtimestamp(w3.eth.getBlock(n).timestamp, tz=timezone.utc)


async def index_parallel(exchanges: [Exchange], step=4096):
    addresses = [x.exchange for x in exchanges]
    start = await db.fetchval('select max(block) + 1 from events') or uniswap.genesis
    last = w3.eth.blockNumber
    for from_block in trange(start, last, step):
        to_block = min(from_block + step - 1, last)
        await fetch_events(addresses, from_block, to_block)
    return last


async def index_tail(start):
    for block in count(start):
        while block > w3.eth.blockNumber:
            await asyncio.sleep(1)
        print(block)  # TODO check for reorgs
        await fetch_new_exchanges(block)
        exchanges = await get_exchanges()  # ineffective
        addresses = [x.exchange for x in exchanges]
        await fetch_events(addresses, from_block=block, to_block=block)


async def start():
    await db.init()
    await fetch_new_exchanges()
    exchanges = await get_exchanges()
    last = await index_parallel(exchanges)
    await index_tail(last + 1)


def main():
    asyncio.run(start())


if __name__ == "__main__":
    main()
