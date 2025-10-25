#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS AI Assistant - Setup Script
Prepares the environment for first run
"""

import os
import secrets
import sys
from pathlib import Path

# Fix encoding for Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')


def generate_secret_key():
    """Generate a secure random secret key"""
    return secrets.token_urlsafe(32)


def create_env_file():
    """Create .env file from template"""
    env_example = Path(".env.example")
    env_file = Path(".env")
    
    if env_file.exists():
        response = input(".env file already exists. Overwrite? (y/N): ")
        if response.lower() != 'y':
            print("Skipping .env creation")
            return
    
    if not env_example.exists():
        print("ERROR: .env.example not found!")
        print("Creating basic .env file...")
        
        # Create basic .env content
        basic_env = f"""# Database
POSTGRES_USER=jarvis
POSTGRES_PASSWORD={secrets.token_urlsafe(16)}
POSTGRES_DB=jarvis_db

# Security
SECRET_KEY={generate_secret_key()}

# Ollama
OLLAMA_URL=http://ollama:11434
OLLAMA_DEFAULT_MODEL=llama2

# Application
ENVIRONMENT=development
DEBUG=True
LOG_LEVEL=INFO
CORS_ORIGINS=http://localhost:3000,http://localhost:80
"""
        
        with open(env_file, 'w') as f:
            f.write(basic_env)
        
        print("Created basic .env file")
        return
    
    # Read template
    with open(env_example, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Generate secret key
    secret_key = generate_secret_key()
    
    # Replace placeholder
    content = content.replace(
        "change-this-to-a-strong-random-secret-key-in-production",
        secret_key
    )
    
    # Generate strong password
    db_password = secrets.token_urlsafe(16)
    content = content.replace(
        "jarvis_secret_change_in_production",
        db_password
    )
    
    # Write .env
    with open(env_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"[OK] Created .env file with secure credentials")
    print(f"   Secret Key: {secret_key[:20]}...")
    print(f"   DB Password: {db_password[:10]}...")


def create_directories():
    """Create necessary directories"""
    dirs = [
        "backend/logs",
        "backend/alembic/versions",
        "backend/app/plugins",
    ]
    
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"[OK] Created directory: {dir_path}")


def check_docker():
    """Check if Docker is installed and running"""
    import subprocess
    
    try:
        result = subprocess.run(
            ["docker", "info"],
            capture_output=True,
            text=True,
            check=False,
            encoding='utf-8',
            errors='replace'
        )
        
        if result.returncode == 0:
            print("[OK] Docker is installed and running")
            return True
        else:
            print("[ERROR] Docker is not running. Please start Docker Desktop.")
            return False
    except FileNotFoundError:
        print("[ERROR] Docker is not installed. Please install Docker Desktop.")
        print("   https://www.docker.com/products/docker-desktop")
        return False


def check_docker_compose():
    """Check if Docker Compose is available"""
    import subprocess
    
    try:
        result = subprocess.run(
            ["docker-compose", "--version"],
            capture_output=True,
            text=True,
            check=False,
            encoding='utf-8',
            errors='replace'
        )
        
        if result.returncode == 0:
            print(f"[OK] {result.stdout.strip()}")
            return True
        else:
            # Try docker compose (new syntax)
            result = subprocess.run(
                ["docker", "compose", "version"],
                capture_output=True,
                text=True,
                check=False,
                encoding='utf-8',
                errors='replace'
            )
            
            if result.returncode == 0:
                print(f"[OK] {result.stdout.strip()}")
                return True
            else:
                print("[ERROR] Docker Compose not found")
                return False
    except FileNotFoundError:
        print("[ERROR] Docker Compose not found")
        return False


def main():
    """Main setup function"""
    print("=" * 60)
    print("JARVIS AI Assistant - Setup")
    print("=" * 60)
    print()
    
    # Check Docker
    print("Checking Docker...")
    if not check_docker():
        sys.exit(1)
    
    print()
    
    # Check Docker Compose
    print("Checking Docker Compose...")
    if not check_docker_compose():
        sys.exit(1)
    
    print()
    
    # Create directories
    print("Creating directories...")
    create_directories()
    
    print()
    
    # Create .env
    print("Setting up environment variables...")
    create_env_file()
    
    print()
    print("=" * 60)
    print("[SUCCESS] Setup Complete!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("  1. Review and edit .env file if needed")
    print("  2. Run: docker-compose up -d --build")
    print("  3. Wait ~2-5 minutes for initialization")
    print("  4. Access: http://localhost")
    print()
    print("Or use Make (Linux/Mac):")
    print("  make install")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSetup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n[ERROR] Setup failed: {str(e)}")
        sys.exit(1)
