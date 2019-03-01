from uniwatch.db import db
from uniwatch.models import Exchange
from uniwatch.config import config

from uniswap.factory import uniswap
from uniswap import abi

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


def get_exchanges() -> [Exchange]:
    return [
        Exchange.from_log(log) for log in
        uniswap.events.NewExchange.createFilter(fromBlock=config.genesis).get_all_entries()
    ]


def get_exchange_logs(exchange: Exchange):
    market = uniswap.get_exchange(exchange.token)
    print(market)


'''
1. get exchanges
2. fill logs in batches
3. main loop
4. watch new exchanges
5. watch new blocks
'''
if __name__ == "__main__":
    for e in get_exchanges():
        print(e)
        get_exchange_logs(e)
