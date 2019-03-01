import json
from operator import itemgetter
from dataclasses import dataclass
from decimal import Decimal

from web3.auto import w3
from web3.contract import ConciseContract
from web3.exceptions import BadFunctionCallOutput

from uniswap.utils import from_wei
from uniswap import abi


class Exchange:

    def __init__(self, factory, token_address, exchange_address):
        self.factory = factory
        self.token = Token(token_address)
        self.exchange = w3.eth.contract(exchange_address, abi=abi.exchange)

    @classmethod
    def from_token(cls, factory, token_address):
        exchange_address = factory.functions.getExchange(token_address).call()
        return cls(factory, token_address, exchange_address)

    @classmethod
    def from_address(cls, factory, exchange_address):
        token_adderss = factory.functions.getToken(exchange_address).call()
        return cls(factory, token_address, exchange_address)

    @property
    def reserves(self):
        return Reserves(
            eth=from_wei(w3.eth.getBalance(self.exchange.address)),
            token=from_wei(
                self.token.functions.balanceOf(self.exchange.address).call(),
                self.token.decimals
            ),
        )

    def get_share(self, provider):
        return Decimal(self.exchange.functions.balanceOf(provider).call()) / self.exchange.functions.totalSupply().call()

    def get_actions(self, provider):
        filters = {'fromBlock': 6627917, 'argument_filters': {'provider': provider}}
        adds = self.exchange.events.AddLiquidity.createFilter(**filters).get_all_entries()
        rems = self.exchange.events.RemoveLiquidity.createFilter(**filters).get_all_entries()
        return [Reserves.from_event(log, self.token.decimals) for log in adds + rems]

    def __repr__(self):
        return f'<Uniswap {self.token.symbol} Exchange>'


class Token:

    def __init__(self, address):
        self.token = w3.eth.contract(address, abi=abi.token)
        try:
            self.symbol = self.token.functions.symbol().call()
        except (OverflowError, BadFunctionCallOutput, ValueError):
            self.token = w3.eth.contract(address, abi=abi.token_bytes)
            try:    
                self.symbol = self.token.functions.symbol().call().replace(b'\x00', b'').decode()
            except (OverflowError, BadFunctionCallOutput, ValueError):
                self.symbol = None

        try:
            self.decimals = self.functions.decimals().call()
        except (OverflowError, BadFunctionCallOutput, ValueError):
            self.decimals = 0

    def __getattr__(self, name):
        return getattr(self.token, name)


@dataclass
class Reserves:
    eth: Decimal
    token: Decimal

    @classmethod
    def from_event(cls, log, decimals):
        signs = {
            'AddLiquidity': 1,
            'RemoveLiquidity': -1,
        }
        sign = signs.get(log.event)
        return cls(
            eth=from_wei(log.args.eth_amount) * sign,
            token=from_wei(log.args.token_amount, decimals) * sign
        )

    def __add__(self, other):
        if isinstance(other, Reserves):
            return Reserves(self.eth + other.eth, self.token + other.token)

    def __radd__(self, other):
        if isinstance(other, int):
            return self

    def __mul__(self, other):
        if isinstance(other, Decimal):
            return Reserves(self.eth * other, self.token * other)

    @property
    def price(self):
        if self.token == 0:
            return None
        return self.eth / self.token

    @property
    def product(self):
        return self.eth * self.token

    def __repr__(self):
        return f'<Reserves ETH={self.eth} Token={self.token} Price={self.price:.8f} InvPrice={1 / self.price:.8f}>'
