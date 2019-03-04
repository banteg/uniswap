from web3 import Web3, HTTPProvider

from uniwatch.config import config

w3 = Web3(HTTPProvider(
    getattr(config, 'ethereum', 'http://127.0.0.1:8545'),
    {'timeout': 120}
))
