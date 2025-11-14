"""
Migration script to add internal_order_number field to receipts and transfers
Run this script to update the database schema
"""
import sqlite3
import os

def migrate():
    """Add internal_order_number to receipts and transfers tables"""
    db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'inventory.db')

    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        print("This is normal if you haven't created the database yet.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(receipts)")
        receipt_columns = [column[1] for column in cursor.fetchall()]

        cursor.execute("PRAGMA table_info(transfers)")
        transfer_columns = [column[1] for column in cursor.fetchall()]

        # Add internal_order_number to receipts if it doesn't exist
        if 'internal_order_number' not in receipt_columns:
            print("Adding internal_order_number to receipts table...")
            cursor.execute("ALTER TABLE receipts ADD COLUMN internal_order_number VARCHAR(100)")
            print("✓ Added internal_order_number to receipts")
        else:
            print("✓ internal_order_number already exists in receipts")

        # Add internal_order_number to transfers if it doesn't exist
        if 'internal_order_number' not in transfer_columns:
            print("Adding internal_order_number to transfers table...")
            cursor.execute("ALTER TABLE transfers ADD COLUMN internal_order_number VARCHAR(100)")
            print("✓ Added internal_order_number to transfers")
        else:
            print("✓ internal_order_number already exists in transfers")

        conn.commit()
        print("\nMigration completed successfully!")

    except Exception as e:
        conn.rollback()
        print(f"Error during migration: {e}")
        raise
    finally:
        conn.close()

if __name__ == '__main__':
    migrate()
