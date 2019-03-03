create table events (
  id bigserial primary key,
  exchange text references exchanges(exchange),
  event text,
  data json,
  block bigint,
  log_index int,
  ts timestamptz,
  constraint unq_block_log_index unique(block, log_index)
);
