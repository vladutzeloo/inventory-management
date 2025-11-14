#!/usr/bin/env python3
"""
Setup script to create .env file with a secure SECRET_KEY
Run this script to set up your environment for the first time
"""
import os
import secrets
import shutil

def setup_env():
    """Create .env file from .env.example with generated SECRET_KEY"""
    env_path = '.env'
    example_path = '.env.example'

    # Check if .env already exists
    if os.path.exists(env_path):
        response = input('.env file already exists. Overwrite? (y/N): ').strip().lower()
        if response != 'y':
            print('Setup cancelled.')
            return

    # Check if .env.example exists
    if not os.path.exists(example_path):
        print(f'Error: {example_path} not found!')
        return

    # Generate a secure SECRET_KEY
    secret_key = secrets.token_hex(32)
    print(f'\nGenerated SECRET_KEY: {secret_key}')

    # Read .env.example and replace the SECRET_KEY
    with open(example_path, 'r') as f:
        content = f.read()

    # Replace the placeholder SECRET_KEY
    content = content.replace(
        'SECRET_KEY=your-secret-key-here-generate-a-random-string',
        f'SECRET_KEY={secret_key}'
    )

    # Write to .env
    with open(env_path, 'w') as f:
        f.write(content)

    print(f'\n✓ Successfully created {env_path}')
    print('\nIMPORTANT:')
    print('- Keep your .env file secure and never commit it to version control')
    print('- The .env file is already in .gitignore')
    print('- Review and update other settings in .env as needed')
    print('\nYou can now run the application!')

if __name__ == '__main__':
    setup_env()
