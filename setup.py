#!/usr/bin/env python3
"""
Setup script for AI-Powered CRM System
This script helps you set up the development environment
"""

import os
import sys
import subprocess
import platform

def run_command(command, cwd=None):
    """Run a command and return the result"""
    try:
        result = subprocess.run(command, shell=True, cwd=cwd, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        print("❌ Python 3.9+ is required")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def check_node_version():
    """Check if Node.js version is compatible"""
    success, stdout, stderr = run_command("node --version")
    if not success:
        print("❌ Node.js is not installed")
        return False
    
    version = stdout.strip().replace('v', '')
    major_version = int(version.split('.')[0])
    if major_version < 18:
        print(f"❌ Node.js 18+ is required (found {version})")
        return False
    
    print(f"✅ Node.js {version} is compatible")
    return True

def setup_backend():
    """Set up the backend"""
    print("\n🔧 Setting up backend...")
    
    # Create virtual environment
    if not os.path.exists("backend/venv"):
        print("Creating virtual environment...")
        success, stdout, stderr = run_command("python -m venv venv", cwd="backend")
        if not success:
            print(f"❌ Failed to create virtual environment: {stderr}")
            return False
        print("✅ Virtual environment created")
    
    # Install dependencies
    print("Installing Python dependencies...")
    if platform.system() == "Windows":
        pip_cmd = "venv\\Scripts\\pip"
    else:
        pip_cmd = "venv/bin/pip"
    
    success, stdout, stderr = run_command(f"{pip_cmd} install -r requirements.txt", cwd="backend")
    if not success:
        print(f"❌ Failed to install dependencies: {stderr}")
        return False
    print("✅ Python dependencies installed")
    
    # Create .env file
    if not os.path.exists("backend/.env"):
        print("Creating .env file...")
        env_content = """# Database
DATABASE_URL=sqlite:///./ai_crm.db

# Security
SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# AI Models
HUGGINGFACE_CACHE_DIR=./models
MODEL_DEVICE=cpu
SENTENCE_TRANSFORMER_MODEL=sentence-transformers/all-MiniLM-L6-v2
SENTIMENT_MODEL=cardiffnlp/twitter-roberta-base-sentiment-latest
TEXT_GENERATION_MODEL=microsoft/DialoGPT-medium
NER_MODEL=dslim/bert-base-NER

# Application
DEBUG=true
APP_NAME=AI-Powered CRM
APP_VERSION=1.0.0
"""
        with open("backend/.env", "w") as f:
            f.write(env_content)
        print("✅ .env file created")
    
    return True

def setup_frontend():
    """Set up the frontend"""
    print("\n🔧 Setting up frontend...")
    
    # Install dependencies
    print("Installing Node.js dependencies...")
    success, stdout, stderr = run_command("npm install", cwd="frontend")
    if not success:
        print(f"❌ Failed to install dependencies: {stderr}")
        return False
    print("✅ Node.js dependencies installed")
    
    return True

def main():
    """Main setup function"""
    print("🚀 AI-Powered CRM Setup")
    print("=" * 50)
    
    # Check prerequisites
    print("\n📋 Checking prerequisites...")
    if not check_python_version():
        return False
    
    if not check_node_version():
        return False
    
    # Set up backend
    if not setup_backend():
        return False
    
    # Set up frontend
    if not setup_frontend():
        return False
    
    print("\n✅ Setup completed successfully!")
    print("\n🎉 You can now start the application:")
    print("\nBackend (Terminal 1):")
    print("  cd backend")
    if platform.system() == "Windows":
        print("  venv\\Scripts\\activate")
    else:
        print("  source venv/bin/activate")
    print("  uvicorn main:app --reload --host 0.0.0.0 --port 8000")
    
    print("\nFrontend (Terminal 2):")
    print("  cd frontend")
    print("  npm run dev")
    
    print("\n🌐 Access the application:")
    print("  Frontend: http://localhost:3000")
    print("  Backend API: http://localhost:8000")
    print("  API Docs: http://localhost:8000/docs")
    
    print("\n📝 Next steps:")
    print("  1. Start both backend and frontend servers")
    print("  2. Register a new user account")
    print("  3. Explore the AI features")
    print("  4. Customize the system for your needs")

if __name__ == "__main__":
    main() 