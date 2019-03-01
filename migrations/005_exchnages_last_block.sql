alter table exchanges add column last_block bigint;
update exchanges set last_block = (select max(block) from events where exchanges.exchange = events.exchange);
