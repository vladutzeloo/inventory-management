#!/usr/bin/env python3
"""
Command-line user management script
Usage: python manage_users.py
"""
from app import create_app
from models import db, User


def list_users():
    """List all users"""
    users = User.query.order_by(User.username).all()

    print("\n" + "="*70)
    print("USER LIST")
    print("="*70)
    print(f"{'Username':<20} {'Full Name':<25} {'Email':<30} {'Active'}")
    print("-"*70)

    for user in users:
        active_status = "Yes" if user.active else "No"
        print(f"{user.username:<20} {user.full_name or '-':<25} {user.email or '-':<30} {active_status}")

    print("-"*70)
    print(f"Total users: {len(users)}")
    print("="*70 + "\n")


def add_user():
    """Add a new user"""
    print("\n" + "="*70)
    print("ADD NEW USER")
    print("="*70)

    username = input("Username: ").strip()
    if not username:
        print("❌ Username cannot be empty!")
        return

    # Check if user exists
    if User.query.filter_by(username=username).first():
        print(f"❌ User '{username}' already exists!")
        return

    full_name = input("Full Name (optional): ").strip()
    email = input("Email (optional): ").strip()
    password = input("Password: ").strip()

    if not password:
        print("❌ Password cannot be empty!")
        return

    # Create user
    user = User(
        username=username,
        full_name=full_name if full_name else None,
        email=email if email else None,
        active=True
    )
    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    print(f"✓ User '{username}' created successfully!")
    print("="*70 + "\n")


def change_password():
    """Change user password"""
    print("\n" + "="*70)
    print("CHANGE PASSWORD")
    print("="*70)

    username = input("Username: ").strip()
    user = User.query.filter_by(username=username).first()

    if not user:
        print(f"❌ User '{username}' not found!")
        return

    new_password = input("New Password: ").strip()

    if not new_password:
        print("❌ Password cannot be empty!")
        return

    user.set_password(new_password)
    db.session.commit()

    print(f"✓ Password for '{username}' changed successfully!")
    print("="*70 + "\n")


def toggle_active():
    """Enable or disable a user"""
    print("\n" + "="*70)
    print("ENABLE/DISABLE USER")
    print("="*70)

    username = input("Username: ").strip()
    user = User.query.filter_by(username=username).first()

    if not user:
        print(f"❌ User '{username}' not found!")
        return

    if username == 'admin':
        print("❌ Cannot disable the admin user!")
        return

    user.active = not user.active
    db.session.commit()

    status = "enabled" if user.active else "disabled"
    print(f"✓ User '{username}' {status} successfully!")
    print("="*70 + "\n")


def delete_user():
    """Delete a user"""
    print("\n" + "="*70)
    print("DELETE USER")
    print("="*70)

    username = input("Username: ").strip()
    user = User.query.filter_by(username=username).first()

    if not user:
        print(f"❌ User '{username}' not found!")
        return

    if username == 'admin':
        print("❌ Cannot delete the admin user!")
        return

    confirm = input(f"Are you sure you want to delete '{username}'? (yes/no): ").strip().lower()

    if confirm == 'yes':
        db.session.delete(user)
        db.session.commit()
        print(f"✓ User '{username}' deleted successfully!")
    else:
        print("❌ Deletion cancelled.")

    print("="*70 + "\n")


def main():
    """Main menu"""
    app = create_app('development')

    with app.app_context():
        while True:
            print("\n" + "="*70)
            print("INVENTORY MANAGEMENT - USER ADMINISTRATION")
            print("="*70)
            print("1. List all users")
            print("2. Add new user")
            print("3. Change password")
            print("4. Enable/Disable user")
            print("5. Delete user")
            print("6. Exit")
            print("="*70)

            choice = input("\nSelect option (1-6): ").strip()

            if choice == '1':
                list_users()
            elif choice == '2':
                add_user()
            elif choice == '3':
                change_password()
            elif choice == '4':
                toggle_active()
            elif choice == '5':
                delete_user()
            elif choice == '6':
                print("\nGoodbye!\n")
                break
            else:
                print("❌ Invalid option. Please try again.")


if __name__ == '__main__':
    main()
