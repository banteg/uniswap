# uniswap analytics

## installation

- install python 3.7, poetry, postgres and a local ethereum node

- run `createdb uniswap` to create a database

- create `config.toml` and specify postgres connection parameters:

```toml
postgres = "postgresql://postgres@127.0.0.1:5432/uniswap"
```

- run `poetry install` to install all dependencies.

## usage

indexer is the only part that works currently.
it fetches all exchanges, tokens and events (decoded) in parallel up to the current block and beyond (think `tail -f`) and stores them to the database.
the full process takes about 10 minutes.

- `poetry run index`
