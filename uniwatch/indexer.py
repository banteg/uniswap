import asyncio
from itertools import count
from datetime import datetime, timezone
from collections import Counter
from concurrent.futures import ThreadPoolExecutor

from uniwatch.db import db
from uniwatch.models import Exchange, Event
from uniwatch.config import config
from uniwatch.eth import w3

from uniswap.factory import uniswap
from uniswap import abi

from web3.utils.events import get_event_data
from eth_utils import event_abi_to_log_topic, encode_hex


loop = asyncio.get_event_loop()
pool = ThreadPoolExecutor(10)
topics_to_abi = {event_abi_to_log_topic(x): x for x in abi.exchange if x['type'] == 'event'}
topic_filter = [encode_hex(x) for x in topics_to_abi]


def decode_logs(logs):
    return [
        get_event_data(topics_to_abi[log['topics'][0]], log)
        for log in logs
    ]


def filter_params(address, from_block=None, to_block=None, topics=None):
    return {
        'address': address,  # many addresses possible
        'fromBlock': from_block or uniswap.genesis,
        'toBlock': to_block or 'latest',
        'topics': topics or [],
    }


async def fetch_events(addresses, from_block, to_block):
    params = filter_params(addresses, from_block, to_block, [topic_filter])
    batch = w3.eth.getLogs(params)
    decoded = decode_logs(batch)
    events = [Event.from_log(log) for log in decoded]
    blocks = list({x.block for x in events})
    futures = [get_timestamp(n) for n in blocks]
    results = await asyncio.gather(*futures)
    timestamps = {n: result for n, result in zip(blocks, results)}
    for event in events:
        event.ts = timestamps[event.block]
        await event.save()
    return events


async def fetch_new_exchanges(from_block=None) -> [Exchange]:
    last_indexed = await db.fetchval('select max(block) + 1 from exchanges')
    last = from_block or last_indexed or uniswap.genesis
    event = uniswap.events.NewExchange()
    topics = [encode_hex(event_abi_to_log_topic(event._get_event_abi()))]
    params = filter_params(uniswap.address, last, 'latest', topics)
    logs = w3.eth.getLogs(params)
    decoded = event.processReceipt({'logs': logs})
    new_exchanges = [Exchange.from_log(log) for log in decoded]
    for exchange in new_exchanges:
        market = uniswap.get_exchange(exchange.token)
        exchange.symbol = market.token.symbol
        exchange.decimals = market.token.decimals
        await exchange.save()
        print(exchange)


async def get_exchanges() -> [Exchange]:
    exchanges = await db.fetch('select token, exchange, block, symbol, decimals from exchanges')
    return [Exchange(*row) for row in exchanges]


async def get_timestamp(n):
    block = await loop.run_in_executor(pool, w3.eth.getBlock, n)
    return datetime.fromtimestamp(block.timestamp, tz=timezone.utc)


async def index_parallel(exchanges: [Exchange], step=1024):
    addresses = [x.exchange for x in exchanges]
    start = await db.fetchval('select max(block) + 1 from events') or uniswap.genesis
    last = w3.eth.blockNumber
    for from_block in range(start, last, step):
        t0 = datetime.now()
        to_block = min(from_block + step - 1, last)
        events = await fetch_events(addresses, from_block, to_block)
        counts = Counter(x.event for x in events)
        counts_pretty = ", ".join(f'{c} x {e}' for e, c in counts.most_common()) if counts else '(no events)'
        print(f'{from_block:,d}-{to_block:,d} ({last-from_block:,d} left): {counts_pretty}, took {datetime.now() - t0}')
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
    loop.run_until_complete(start())


if __name__ == "__main__":
    main()
