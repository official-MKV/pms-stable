# User Name Fields Migration

## Overview

This migration updates the user database schema to use separate name fields instead of a single `name` field, making it more suitable for government software requirements.

## Changes Made

### Database Schema (models.py)
- **Removed**: `name` field (VARCHAR)
- **Added**:
  - `first_name` (VARCHAR(100), NOT NULL)
  - `last_name` (VARCHAR(100), NOT NULL)
  - `middle_name` (VARCHAR(100), NULLABLE)
- **Updated**: `level` field from VARCHAR to INTEGER (1-17 for civil service grade levels)

### API Schemas (schemas/users.py)
- Updated `UserBase`, `UserCreate`, `UserUpdate`, and `UserProfile` schemas
- Added computed `name` property for backward compatibility
- Added validation for civil service grade levels (1-17)

### Frontend (users/page.js)
- Updated user form with separate name fields
- Added searchable dropdowns for organizations and roles
- Changed level to number input with proper validation
- Updated terminology to "Organizational Unit"

## Migration Steps

### 1. Backup Your Database
```bash
pg_dump pms_db > backup_before_migration.sql
```

### 2. Run the Migration Script
```bash
cd /path/to/backend
python migrate_user_names.py
```

### 3. Verify Migration
- Check that new columns exist
- Verify data was migrated correctly
- Test API endpoints with new schema

### 4. Update Your Application
- Deploy updated backend code
- Deploy updated frontend code
- Test user creation and editing

## Migration Script Details

The `migrate_user_names.py` script:

1. **Adds new columns** without breaking existing functionality
2. **Migrates existing data** by splitting names intelligently:
   - Single name → first_name + last_name (same value)
   - Two names → first_name + last_name
   - Three+ names → first_name + middle_name(s) + last_name
3. **Converts level field** from string to integer (extracts numbers)
4. **Maintains backward compatibility** by keeping old name column

## Rollback Instructions

If you need to rollback (though database backup restore is recommended):

```bash
python migrate_user_names.py rollback
```

## Testing After Migration

### Backend API Tests
```bash
# Test user creation
curl -X POST http://localhost:8000/api/users \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "middle_name": "Middle",
    "email": "john.doe@nigcomsat.gov.ng",
    "level": 12,
    "organization_id": "...",
    "role_id": "..."
  }'

# Test user retrieval
curl http://localhost:8000/api/users
```

### Frontend Tests
1. Open user management page
2. Create new user with separate name fields
3. Edit existing user and verify name fields are populated
4. Search users by name
5. Verify grade level number input works

## Data Validation

After migration, verify:

- [ ] All users have `first_name` and `last_name`
- [ ] `middle_name` is properly populated or NULL
- [ ] Level values are integers between 1-17 where applicable
- [ ] API returns computed `name` field for backward compatibility
- [ ] Frontend displays names correctly
- [ ] User search functionality works

## Notes

- The migration script keeps the old `name` column for safety
- You can manually drop it after confirming everything works:
  ```sql
  ALTER TABLE users DROP COLUMN name;
  ```
- Civil service grade levels are validated as 1-17
- Middle names are optional and can contain multiple names

## Troubleshooting

### Common Issues

1. **Migration fails on name splitting**: Check for users with unusual name formats
2. **Level conversion fails**: Some string levels may not convert to integers
3. **NOT NULL constraint errors**: Script handles this by setting defaults

### Logs

The migration script provides detailed logging. Check the output for:
- Number of users migrated
- Any conversion warnings
- Successful completion message

## Support

After running the migration:
1. Test all user-related functionality
2. Verify reports and exports work correctly
3. Check that user search/filtering works
4. Confirm government naming requirements are met