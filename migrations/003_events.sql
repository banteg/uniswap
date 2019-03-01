create table events (
  id bigserial primary key,
  exchange text,
  event text,
  data json,
  block bigint,
  log_index int,
  constraint unq_block_log_index unique(block, log_index)
);
