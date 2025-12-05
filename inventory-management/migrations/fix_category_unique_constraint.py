"""
Migration script to fix category unique constraint
Changes the unique constraint from just 'name' to composite ('name', 'category_type')
This allows the same category name to be used for both materials and items.

Run this script to update the database schema
"""
import sqlite3
import os

def migrate():
    """Update categories table to use composite unique constraint"""
    db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'inventory.db')

    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        print("This is normal if you haven't created the database yet.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Check if categories table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='categories'")
        categories_exists = cursor.fetchone() is not None

        if not categories_exists:
            print("Categories table doesn't exist. Skipping migration.")
            return

        print("Updating categories table unique constraint...")

        # Check current schema
        cursor.execute("PRAGMA table_info(categories)")
        columns = cursor.fetchall()
        print(f"Current columns: {[col[1] for col in columns]}")

        # SQLite doesn't support dropping constraints, so we need to recreate the table
        # 1. Create new table with correct schema
        print("Creating new categories table with composite unique constraint...")
        cursor.execute("""
            CREATE TABLE categories_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) NOT NULL,
                description TEXT,
                category_type VARCHAR(20) NOT NULL,
                active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(name, category_type)
            )
        """)

        # 2. Copy data from old table
        print("Copying data from old categories table...")
        cursor.execute("""
            INSERT INTO categories_new (id, name, description, category_type, active, created_at)
            SELECT id, name, description, category_type, active, created_at
            FROM categories
        """)

        # 3. Drop old table
        print("Dropping old categories table...")
        cursor.execute("DROP TABLE categories")

        # 4. Rename new table
        print("Renaming new table...")
        cursor.execute("ALTER TABLE categories_new RENAME TO categories")

        # 5. Recreate indexes
        print("Recreating indexes...")
        cursor.execute("CREATE INDEX idx_categories_name ON categories(name)")
        cursor.execute("CREATE INDEX idx_categories_type ON categories(category_type)")

        conn.commit()
        print("\n✓ Migration completed successfully!")
        print("\nCategories table now allows the same name for different category types.")
        print("For example, you can now have 'Metals' as both a material and item category.")

    except Exception as e:
        conn.rollback()
        print(f"Error during migration: {e}")
        raise
    finally:
        conn.close()

if __name__ == '__main__':
    migrate()
