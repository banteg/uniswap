import json
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed

from web3.auto import w3
from web3.contract import ConciseContract

from uniswap.exchange import Exchange
from uniswap import abi


class Uniswap:

    def __init__(self):
        self.genesis = 6627917
        self.factory = w3.eth.contract('0xc0a47dFe034B400B47bDaD5FecDa2621de6c4d95', abi=abi.factory)

    def get_exchange(self, token_address):
        return Exchange.from_token(self, token_address)

    def __getattr__(self, name):
        return getattr(self.factory, name)


uniswap = Uniswap()
