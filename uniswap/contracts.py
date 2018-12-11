import json
from pathlib import Path

from web3.auto import w3
from web3.exceptions import BadFunctionCallOutput

deployed = 6627917
deployments = {
    '1': '0xc0a47dFe034B400B47bDaD5FecDa2621de6c4d95',
    '4': '0xf5D915570BC477f9B8D6C0E980aA81757A3AaC36',
}
abi = {
    f.stem: json.loads(f.read_text()) for f
    in Path('abi').iterdir() if f.suffix == '.json'
}


def get_factory():
    return w3.eth.contract(
        deployments[w3.version.network],
        abi=abi['factory']
    )


def get_exchange(factory, token_address):
    return w3.eth.contract(
        factory.functions.getExchange(token_address).call(),
        abi=abi['exchange']
    )


def get_exchanges(factory):
    # token -> exchange
    filt = factory.events.NewExchange().createFilter(fromBlock=deployed)
    return {x['args']['token']: x['args']['exchange'] for x in filt.get_all_entries()}


def get_token(address):
    try:
        token = w3.eth.contract(address, abi=abi['erc20'])
        token.functions.symbol().call()
    except (OverflowError, BadFunctionCallOutput, ValueError):
        token = w3.eth.contract(address, abi=abi['erc20_symbol_bytes32'])
    return token
