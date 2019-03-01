import json

factory = json.load(open('abi/factory.json'))
exchange = json.load(open('abi/exchange.json'))
token = json.load(open('abi/erc20.json'))
token_bytes = json.load(open('abi/erc20_symbol_bytes32.json'))
