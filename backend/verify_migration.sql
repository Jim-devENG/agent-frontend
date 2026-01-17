-- ============================================================================
-- Verification Query: Check if discovery_query_id column exists
-- ============================================================================
-- Run this query to verify the column exists in production:
-- 
-- psql $DATABASE_URL -c "SELECT column_name, data_type, is_nullable FROM information_schema.columns WHERE table_name = 'prospects' AND column_name = 'discovery_query_id';"
-- ============================================================================

SELECT 
    column_name, 
    data_type, 
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_name = 'prospects' 
AND column_name = 'discovery_query_id';

-- Expected result if column exists:
-- column_name          | data_type | is_nullable | column_default
-- ---------------------+-----------+-------------+---------------
-- discovery_query_id   | uuid      | YES         | NULL

-- If no rows returned, the column does not exist and migration needs to be run.

-- ============================================================================
-- Check foreign key constraint
-- ============================================================================

SELECT 
    constraint_name,
    table_name,
    column_name,
    foreign_table_name,
    foreign_column_name
FROM information_schema.table_constraints tc
JOIN information_schema.key_column_usage kcu 
    ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage ccu 
    ON ccu.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY'
AND tc.table_name = 'prospects'
AND kcu.column_name = 'discovery_query_id';

-- Expected result if FK exists:
-- constraint_name                  | table_name | column_name          | foreign_table_name    | foreign_column_name
-- ---------------------------------+------------+---------------------+-----------------------+--------------------
-- fk_prospects_discovery_query_id | prospects  | discovery_query_id  | discovery_queries     | id

-- ============================================================================
-- Check index
-- ============================================================================

SELECT 
    indexname,
    tablename,
    indexdef
FROM pg_indexes
WHERE tablename = 'prospects'
AND indexname = 'ix_prospects_discovery_query_id';

-- Expected result if index exists:
-- indexname                      | tablename | indexdef
-- -------------------------------+-----------+------------------------------------------
-- ix_prospects_discovery_query_id | prospects | CREATE INDEX ix_prospects_discovery_query_id ON public.prospects USING btree (discovery_query_id)

