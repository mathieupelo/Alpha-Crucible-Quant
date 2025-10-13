#!/usr/bin/env python3
"""
Development Environment Setup Script for Alpha Crucible Quant

This script helps set up the development environment with proper dependencies,
pre-commit hooks, and configuration.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stdout:
            print(f"STDOUT: {e.stdout}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
        return False


def check_python_version():
    """Check if Python version is 3.11+."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 11):
        print(f"❌ Python 3.11+ required, found {version.major}.{version.minor}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")
    return True


def check_node_version():
    """Check if Node.js version is 18+."""
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True, check=True)
        version = result.stdout.strip()
        major_version = int(version[1:].split('.')[0])
        if major_version < 18:
            print(f"❌ Node.js 18+ required, found {version}")
            return False
        print(f"✅ Node.js {version} detected")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Node.js not found. Please install Node.js 18+")
        return False


def check_docker():
    """Check if Docker is available."""
    try:
        subprocess.run(["docker", "--version"], capture_output=True, check=True)
        subprocess.run(["docker-compose", "--version"], capture_output=True, check=True)
        print("✅ Docker and Docker Compose detected")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Docker not found. Please install Docker and Docker Compose")
        return False


def setup_python_environment():
    """Set up Python virtual environment and dependencies."""
    # Create virtual environment
    if not run_command("python -m venv venv", "Creating Python virtual environment"):
        return False
    
    # Determine activation script based on OS
    if platform.system() == "Windows":
        activate_script = "venv\\Scripts\\activate"
        pip_cmd = "venv\\Scripts\\pip"
    else:
        activate_script = "source venv/bin/activate"
        pip_cmd = "venv/bin/pip"
    
    # Upgrade pip
    if not run_command(f"{pip_cmd} install --upgrade pip", "Upgrading pip"):
        return False
    
    # Install dependencies
    if not run_command(f"{pip_cmd} install -r requirements.txt", "Installing Python dependencies"):
        return False
    
    if not run_command(f"{pip_cmd} install -r backend/requirements.txt", "Installing backend dependencies"):
        return False
    
    # Install development dependencies
    if not run_command(f"{pip_cmd} install pre-commit", "Installing pre-commit"):
        return False
    
    return True


def setup_node_environment():
    """Set up Node.js environment."""
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print("❌ Frontend directory not found")
        return False
    
    os.chdir(frontend_dir)
    
    # Install dependencies
    if not run_command("npm install", "Installing Node.js dependencies"):
        os.chdir("..")
        return False
    
    os.chdir("..")
    return True


def setup_pre_commit():
    """Set up pre-commit hooks."""
    if not run_command("pre-commit install", "Installing pre-commit hooks"):
        return False
    
    # Run pre-commit on all files
    if not run_command("pre-commit run --all-files", "Running pre-commit on all files"):
        print("⚠️  Pre-commit found issues. Please fix them before committing.")
        return False
    
    return True


def setup_environment_file():
    """Set up environment file from template."""
    env_file = Path(".env")
    template_file = Path(".env_template")
    
    if env_file.exists():
        print("✅ .env file already exists")
        return True
    
    if not template_file.exists():
        print("❌ .env_template file not found")
        return False
    
    # Copy template to .env
    try:
        with open(template_file, 'r') as src, open(env_file, 'w') as dst:
            dst.write(src.read())
        print("✅ Created .env file from template")
        print("⚠️  Please edit .env file with your actual database credentials")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False


def main():
    """Main setup function."""
    print("🚀 Alpha Crucible Quant - Development Environment Setup")
    print("=" * 60)
    
    # Check prerequisites
    print("\n📋 Checking prerequisites...")
    if not check_python_version():
        return 1
    if not check_node_version():
        return 1
    if not check_docker():
        return 1
    
    # Setup Python environment
    print("\n🐍 Setting up Python environment...")
    if not setup_python_environment():
        return 1
    
    # Setup Node.js environment
    print("\n📦 Setting up Node.js environment...")
    if not setup_node_environment():
        return 1
    
    # Setup pre-commit hooks
    print("\n🔧 Setting up pre-commit hooks...")
    if not setup_pre_commit():
        return 1
    
    # Setup environment file
    print("\n⚙️  Setting up environment configuration...")
    if not setup_environment_file():
        return 1
    
    print("\n🎉 Development environment setup completed successfully!")
    print("\n📝 Next steps:")
    print("1. Edit .env file with your database credentials")
    print("2. Run 'docker-compose up -d' to start the application")
    print("3. Access the application at http://localhost:8080")
    print("4. Run tests with 'pytest tests/'")
    print("5. Start developing! 🚀")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
