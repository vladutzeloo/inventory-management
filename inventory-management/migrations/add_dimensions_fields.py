"""
Migration script to add dimension fields to materials and items tables
Run this script to update the database schema
"""
import sqlite3
import os

def migrate():
    """Add diameter, length, width, and height fields to materials and items tables"""
    db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'inventory.db')

    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        print("This is normal if you haven't created the database yet.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Check if columns already exist in materials table
        cursor.execute("PRAGMA table_info(materials)")
        material_columns = [column[1] for column in cursor.fetchall()]

        # Check if columns already exist in items table
        cursor.execute("PRAGMA table_info(items)")
        item_columns = [column[1] for column in cursor.fetchall()]

        # Add dimension fields to materials table
        print("Updating materials table...")
        if 'diameter' not in material_columns:
            print("  Adding diameter to materials table...")
            cursor.execute("ALTER TABLE materials ADD COLUMN diameter FLOAT")
            print("  ✓ Added diameter to materials")
        else:
            print("  ✓ diameter already exists in materials")

        if 'length' not in material_columns:
            print("  Adding length to materials table...")
            cursor.execute("ALTER TABLE materials ADD COLUMN length FLOAT")
            print("  ✓ Added length to materials")
        else:
            print("  ✓ length already exists in materials")

        if 'width' not in material_columns:
            print("  Adding width to materials table...")
            cursor.execute("ALTER TABLE materials ADD COLUMN width FLOAT")
            print("  ✓ Added width to materials")
        else:
            print("  ✓ width already exists in materials")

        if 'height' not in material_columns:
            print("  Adding height to materials table...")
            cursor.execute("ALTER TABLE materials ADD COLUMN height FLOAT")
            print("  ✓ Added height to materials")
        else:
            print("  ✓ height already exists in materials")

        # Add dimension fields to items table
        print("\nUpdating items table...")
        if 'diameter' not in item_columns:
            print("  Adding diameter to items table...")
            cursor.execute("ALTER TABLE items ADD COLUMN diameter FLOAT")
            print("  ✓ Added diameter to items")
        else:
            print("  ✓ diameter already exists in items")

        if 'length' not in item_columns:
            print("  Adding length to items table...")
            cursor.execute("ALTER TABLE items ADD COLUMN length FLOAT")
            print("  ✓ Added length to items")
        else:
            print("  ✓ length already exists in items")

        if 'width' not in item_columns:
            print("  Adding width to items table...")
            cursor.execute("ALTER TABLE items ADD COLUMN width FLOAT")
            print("  ✓ Added width to items")
        else:
            print("  ✓ width already exists in items")

        if 'height' not in item_columns:
            print("  Adding height to items table...")
            cursor.execute("ALTER TABLE items ADD COLUMN height FLOAT")
            print("  ✓ Added height to items")
        else:
            print("  ✓ height already exists in items")

        conn.commit()
        print("\n✅ Migration completed successfully!")
        print("   Dimension fields (diameter, length, width, height) have been added to materials and items tables.")

    except Exception as e:
        conn.rollback()
        print(f"❌ Error during migration: {e}")
        raise
    finally:
        conn.close()

if __name__ == '__main__':
    migrate()
