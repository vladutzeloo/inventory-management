"""
Migration script to add categories, clients, and providers tables
Run this script to update the database schema
"""
import sqlite3
import os

def migrate():
    """Add categories and clients tables, and update materials/items with foreign keys"""
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
            print("Creating categories table...")
            cursor.execute("""
                CREATE TABLE categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(100) NOT NULL UNIQUE,
                    description TEXT,
                    category_type VARCHAR(20) NOT NULL,
                    active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("CREATE INDEX idx_categories_name ON categories(name)")
            cursor.execute("CREATE INDEX idx_categories_type ON categories(category_type)")
            print("✓ Created categories table")
        else:
            print("✓ categories table already exists")

        # Check if clients table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='clients'")
        clients_exists = cursor.fetchone() is not None

        if not clients_exists:
            print("Creating clients table...")
            cursor.execute("""
                CREATE TABLE clients (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(200) NOT NULL UNIQUE,
                    code VARCHAR(50) NOT NULL UNIQUE,
                    contact_person VARCHAR(200),
                    email VARCHAR(200),
                    phone VARCHAR(50),
                    address TEXT,
                    active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("CREATE INDEX idx_clients_name ON clients(name)")
            cursor.execute("CREATE INDEX idx_clients_code ON clients(code)")
            print("✓ Created clients table")
        else:
            print("✓ clients table already exists")

        # Check if providers table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='providers'")
        providers_exists = cursor.fetchone() is not None

        if not providers_exists:
            print("Creating providers table...")
            cursor.execute("""
                CREATE TABLE providers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(200) NOT NULL UNIQUE,
                    code VARCHAR(50) NOT NULL UNIQUE,
                    contact_person VARCHAR(200),
                    email VARCHAR(200),
                    phone VARCHAR(50),
                    address TEXT,
                    active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("CREATE INDEX idx_providers_name ON providers(name)")
            cursor.execute("CREATE INDEX idx_providers_code ON providers(code)")
            print("✓ Created providers table")
        else:
            print("✓ providers table already exists")

        # Check and add category_id to materials
        cursor.execute("PRAGMA table_info(materials)")
        material_columns = [column[1] for column in cursor.fetchall()]

        if 'category_id' not in material_columns:
            print("Adding category_id to materials table...")
            cursor.execute("ALTER TABLE materials ADD COLUMN category_id INTEGER REFERENCES categories(id)")
            print("✓ Added category_id to materials")
        else:
            print("✓ category_id already exists in materials")

        if 'provider_id' not in material_columns:
            print("Adding provider_id to materials table...")
            cursor.execute("ALTER TABLE materials ADD COLUMN provider_id INTEGER REFERENCES providers(id)")
            print("✓ Added provider_id to materials")
        else:
            print("✓ provider_id already exists in materials")

        # Check and add category_id and client_id to items
        cursor.execute("PRAGMA table_info(items)")
        item_columns = [column[1] for column in cursor.fetchall()]

        if 'category_id' not in item_columns:
            print("Adding category_id to items table...")
            cursor.execute("ALTER TABLE items ADD COLUMN category_id INTEGER REFERENCES categories(id)")
            print("✓ Added category_id to items")
        else:
            print("✓ category_id already exists in items")

        if 'client_id' not in item_columns:
            print("Adding client_id to items table...")
            cursor.execute("ALTER TABLE items ADD COLUMN client_id INTEGER REFERENCES clients(id)")
            print("✓ Added client_id to items")
        else:
            print("✓ client_id already exists in items")

        conn.commit()
        print("\nMigration completed successfully!")
        print("\nYou can now:")
        print("1. Manage categories at /categories")
        print("2. Manage clients at /clients")
        print("3. Assign categories to materials and items")
        print("4. Assign clients to finished goods/items")

    except Exception as e:
        conn.rollback()
        print(f"Error during migration: {e}")
        raise
    finally:
        conn.close()

if __name__ == '__main__':
    migrate()
