import logging

import toml
from attrdict import AttrDict

config = AttrDict(toml.load(open('config.toml')))

logging.basicConfig(
    level=getattr(logging, config.level),
    format='%(levelname)-8s %(name)s: %(message)s'
)
