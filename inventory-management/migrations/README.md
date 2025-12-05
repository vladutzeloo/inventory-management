# Database Migrations

This directory contains migration scripts to update the database schema.

## Running Migrations

Migrations should be run in order, from oldest to newest. Each migration script is designed to be idempotent (safe to run multiple times).

### Migration: fix_category_unique_constraint.py

**Purpose**: Fixes the UNIQUE constraint on the `categories` table to allow the same category name for different types (material vs item).

**When to run**:
- If you get an error like: `UNIQUE constraint failed: categories.name`
- After upgrading to a version that includes composite unique constraints on categories

**How to run**:
```bash
cd /path/to/inventory-management
python inventory-management/migrations/fix_category_unique_constraint.py
```

**What it does**:
- Changes the unique constraint from just `name` to `(name, category_type)`
- This allows you to have "Metals" as both a material category and an item category
- All existing data is preserved during the migration

**Note**: If you're creating a new database from scratch, this migration is not needed as the updated model will create the correct schema automatically.

## Migration Order

1. `add_categories_and_clients.py` - Initial categories and clients support
2. `add_dimensions_fields.py` - Adds dimensional fields to materials and items
3. `add_internal_order_number.py` - Adds internal order tracking
4. `fix_category_unique_constraint.py` - Fixes category unique constraint (NEW)

## Troubleshooting

If you encounter errors during migration:

1. **"Database not found"**: This is normal if you haven't created the database yet. Run the application first to initialize the database.

2. **"Table already exists"**: Some migrations check for existing tables and skip if already present. This is expected behavior.

3. **"Migration failed"**: Check the error message. Migrations include rollback on failure, so your database should remain in a consistent state.

## Creating New Migrations

When creating a new migration:

1. Create a descriptive filename: `action_description.py`
2. Include a docstring explaining what the migration does
3. Check for existing tables/columns before making changes
4. Use transactions (commit/rollback) for safety
5. Test on a backup database first
6. Update this README with the new migration
