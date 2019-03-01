create table tokens (
  id bigserial primary key,
  token text unique,
  symbol text,
  name text,
  decimals int
);
