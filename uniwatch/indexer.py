import asyncio

from uniwatch.db import db
from uniwatch.models import Exchange, Event, Token
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


async def get_exchanges() -> [Exchange]:
    last = await db.fetchval('select max(block) + 1 from exchanges') or uniswap.genesis
    new_exchanges = [
        Exchange.from_log(log) for log in
        uniswap.events.NewExchange.createFilter(fromBlock=last).get_all_entries()
    ]
    for exchange in new_exchanges:
        await exchange.save()
        print(f'new exchange: {exchange}')
        market = uniswap.get_exchange(exchange.token)
        token = Token(token=exchange.token, symbol=market.token.symbol, decimals=market.token.decimals)
        await token.save()
        print(f'new token: {token}')
    exchanges = await db.fetch('select token, exchange, block from exchanges')
    return [Exchange(*row) for row in exchanges]


async def index_parallel(exchanges: [Exchange], step=4096):
    addresses = {x.exchange for x in exchanges}
    start = await db.fetchval('select max(block) + 1 from events') or uniswap.genesis
    last = w3.eth.blockNumber
    for offset in trange(start, last, step):
        to_block = min(offset + step - 1, last)
        params = filter_params(addresses, from_block=offset, to_block=to_block)
        batch = w3.eth.getLogs(params)
        decoded = decode_logs(batch)
        events = [Event.from_log(log) for log in decoded]
        for event in events:
            await event.save()


async def start():
    await db.init()
    exchanges = await get_exchanges()
    await index_parallel(exchanges)


def main():
    asyncio.run(start())


if __name__ == "__main__":
    main()
