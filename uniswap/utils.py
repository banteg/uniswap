from decimal import Decimal


def from_wei(value, decimals=18):
    return Decimal(value) / 10 ** decimals
