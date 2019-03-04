# uniswap analytics

## installation

- install python 3.7, poetry, postgres and a local ethereum node (optional)

- run `createdb uniswap` to create a database

- create `config.toml` and specify connection parameters:

```toml
postgres = "postgresql://postgres@127.0.0.1:5432/uniswap"
# by default it connects to a local node at http://127.0.0.1:8545
# if you want to use infura, specify it here
ethereum = "https://mainnet.infura.io/metamask"
```

- run `poetry install` to install all dependencies.

## usage

indexer is the only part that works currently.
it fetches all exchanges, tokens and events (decoded) in parallel up to the current block and beyond (think `tail -f`) and stores them to the database.
the full process takes about 10 minutes.

- `poetry run index`
