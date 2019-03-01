import json
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed

from web3.auto import w3
from web3.contract import ConciseContract

from uniswap.exchange import Exchange


class Uniswap:

    def __init__(self):
        factory_addresses = {
            '1': '0xc0a47dFe034B400B47bDaD5FecDa2621de6c4d95',
            '4': '0xf5D915570BC477f9B8D6C0E980aA81757A3AaC36',
        }
        factory_address = factory_addresses[w3.version.network]
        factory_abi = json.load(open('abi/factory.json'))
        self.factory = w3.eth.contract(factory_address, abi=factory_abi)

    def get_exchange(self, token_address):
        return Exchange.from_token(self, token_address)

    def __getattr__(self, name):
        return getattr(self.factory, name)


uniswap = Uniswap()
