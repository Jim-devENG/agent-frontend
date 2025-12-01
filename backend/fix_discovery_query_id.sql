-- Emergency fix: Add discovery_query_id column to prospects table
-- This is SAFE: column is nullable, no data loss

-- Step 1: Add column (idempotent - safe to run multiple times)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'prospects' 
        AND column_name = 'discovery_query_id'
    ) THEN
        ALTER TABLE prospects 
        ADD COLUMN discovery_query_id UUID;
        
        RAISE NOTICE '✅ Added discovery_query_id column';
    ELSE
        RAISE NOTICE 'ℹ️  Column discovery_query_id already exists';
    END IF;
END $$;

-- Step 2: Create index (idempotent)
CREATE INDEX IF NOT EXISTS ix_prospects_discovery_query_id 
ON prospects(discovery_query_id);

-- Step 3: Add foreign key if discovery_queries table exists
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'discovery_queries') THEN
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.table_constraints 
            WHERE constraint_name = 'fk_prospects_discovery_query_id'
        ) THEN
            ALTER TABLE prospects
            ADD CONSTRAINT fk_prospects_discovery_query_id
            FOREIGN KEY (discovery_query_id)
            REFERENCES discovery_queries(id)
            ON DELETE SET NULL;
            
            RAISE NOTICE '✅ Added foreign key constraint';
        ELSE
            RAISE NOTICE 'ℹ️  Foreign key constraint already exists';
        END IF;
    ELSE
        RAISE NOTICE '⚠️  discovery_queries table does not exist, skipping FK';
    END IF;
END $$;

-- Step 4: Verify
SELECT 
    column_name, 
    data_type, 
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_name = 'prospects' 
AND column_name = 'discovery_query_id';

