create table tokens (
  id bigserial primary key,
  token text references exchanges(token),
  symbol text,
  decimals int
);
