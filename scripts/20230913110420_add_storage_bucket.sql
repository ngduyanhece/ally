insert into
  storage.buckets (id, name)
values
  ('ally', 'ally');

-- Update migrations table
INSERT INTO migrations (name) 
SELECT '20230913110420_add_storage_bucket'
WHERE NOT EXISTS (
    SELECT 1 FROM migrations WHERE name = '20230913110420_add_storage_bucket'
);

COMMIT;
