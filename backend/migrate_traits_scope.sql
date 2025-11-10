-- Migration script to add organizational scope to review traits
-- This adds scope_type and organization_id to support trait inheritance

-- Create enum type for trait scope
CREATE TYPE traitscopetype AS ENUM ('global', 'directorate', 'department', 'unit');

-- Add new columns to review_traits table
ALTER TABLE review_traits
    ADD COLUMN IF NOT EXISTS scope_type traitscopetype NOT NULL DEFAULT 'global',
    ADD COLUMN IF NOT EXISTS organization_id UUID;

-- Add foreign key constraint
ALTER TABLE review_traits
    ADD CONSTRAINT fk_review_traits_organization_id
    FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE CASCADE;

-- Create index for performance
CREATE INDEX IF NOT EXISTS idx_review_traits_scope ON review_traits(scope_type, organization_id);
CREATE INDEX IF NOT EXISTS idx_review_traits_organization_id ON review_traits(organization_id);

-- Drop old unique constraint on name only
ALTER TABLE review_traits DROP CONSTRAINT IF EXISTS review_traits_name_key;

-- Add new unique constraint on name, scope_type, and organization_id
ALTER TABLE review_traits
    ADD CONSTRAINT unique_trait_name_scope
    UNIQUE (name, scope_type, organization_id);

-- Update existing traits to be global scope
UPDATE review_traits SET scope_type = 'global' WHERE scope_type IS NULL OR organization_id IS NULL;

COMMIT;
