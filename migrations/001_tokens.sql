create table tokens (
  id bigserial primary key,
  address bytea,
  symbol text,
  name text,
  decimals int
);
