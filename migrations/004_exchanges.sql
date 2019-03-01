create table exchanges (
    id bigserial primary key,
    token text unique,
    exchange text unique,
    block bigint
);
