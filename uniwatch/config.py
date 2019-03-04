import toml
from attrdict import AttrDict

config = AttrDict(toml.load(open('config.toml')))
