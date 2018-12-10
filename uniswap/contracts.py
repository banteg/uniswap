import json

from web3.auto import w3
from web3.exceptions import BadFunctionCallOutput

deployments = {
    '1': '0xc0a47dFe034B400B47bDaD5FecDa2621de6c4d95',
    '4': '0xf5D915570BC477f9B8D6C0E980aA81757A3AaC36',
}


def get_factory():
    return w3.eth.contract(
        deployments[w3.version.network],
        abi=json.load(open('abi/factory.json'))
    )


def get_exchange(factory, token_address):
    return w3.eth.contract(
        factory.functions.getExchange(token_address).call(),
        abi=json.load(open('abi/exchange.json'))
    )


def get_token(address):
    try:
        erc20_abi = json.load(open('abi/erc20.json'))
        token = w3.eth.contract(address, abi=erc20_abi)
        token.functions.symbol().call()
    except (OverflowError, BadFunctionCallOutput, ValueError):
        erc20_bytes_abi = json.load(open('abi/erc20_symbol_bytes32.json'))
        token = w3.eth.contract(address, abi=erc20_bytes_abi)
    return token
