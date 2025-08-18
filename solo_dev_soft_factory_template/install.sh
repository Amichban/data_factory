#!/bin/bash

# Solo Software Factory - Installation Script
# Handles common dependency issues

set -e

echo "🚀 Solo Software Factory - Installation"
echo "========================================"
echo ""

# Detect OS
OS="Unknown"
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="Linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macOS"
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
    OS="Windows"
fi

echo "📍 Detected OS: $OS"
echo ""

# Check Python version
echo "🐍 Checking Python..."
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "❌ Python not found. Please install Python 3.9+"
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
echo "   Python version: $PYTHON_VERSION"

# Check Python version compatibility
if [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -ge 13 ]; then
    echo "   ⚠️  Python 3.13+ detected - using updated packages"
    PYTHON_313_COMPAT=true
else
    PYTHON_313_COMPAT=false
fi

# Check Node.js version
echo "📦 Checking Node.js..."
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo "   Node version: $NODE_VERSION"
else
    echo "❌ Node.js not found. Please install Node.js 18+"
    exit 1
fi

# Install Python dependencies
echo ""
echo "1️⃣ Installing Python dependencies..."
cd apps/api

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "   Creating virtual environment..."
    $PYTHON_CMD -m venv venv
fi

# Activate virtual environment
echo "   Activating virtual environment..."
if [[ "$OS" == "Windows" ]]; then
    source venv/Scripts/activate 2>/dev/null || venv\Scripts\activate
else
    source venv/bin/activate
fi

# Upgrade pip first
echo "   Upgrading pip..."
pip install --upgrade pip setuptools wheel

# For Python 3.13, ensure we have build tools
if [ "$PYTHON_313_COMPAT" = true ]; then
    echo "   Installing build tools for Python 3.13+..."
    pip install --upgrade build setuptools-rust
fi

# Install dependencies with fallback options
echo "   Installing requirements..."

# Choose the right requirements file based on Python version
if [ "$PYTHON_313_COMPAT" = true ]; then
    echo "   Using Python 3.13+ compatible requirements"
    REQUIREMENTS_FILE="requirements-python313.txt"
else
    REQUIREMENTS_FILE="requirements.txt"
fi

# Try normal installation first
if ! pip install -r $REQUIREMENTS_FILE; then
    echo "   ⚠️ Standard installation failed, trying alternative approach..."
    
    # Install problematic packages separately
    echo "   Installing build dependencies..."
    
    # For psycopg2-binary issues
    if [[ "$OS" == "macOS" ]]; then
        # On macOS, sometimes need to specify pg_config
        export LDFLAGS="-L/usr/local/opt/openssl/lib"
        export CPPFLAGS="-I/usr/local/opt/openssl/include"
    elif [[ "$OS" == "Linux" ]]; then
        # On Linux, might need postgresql dev packages
        echo "   Note: If psycopg2 fails, you may need to install:"
        echo "   Ubuntu/Debian: sudo apt-get install libpq-dev python3-dev"
        echo "   RHEL/CentOS: sudo yum install postgresql-devel python3-devel"
    fi
    
    # Handle Python 3.13+ compatibility
    if [ "$PYTHON_313_COMPAT" = true ]; then
        echo "   Using psycopg 3.x for Python 3.13+ compatibility"
        pip install "psycopg[binary]>=3.2.1"
    else
        # Try installing without binary packages for older Python
        pip install --no-binary :all: psycopg2==2.9.9 || pip install psycopg2-binary==2.9.9
    fi
    
    # For pydantic-core issues
    if [ "$PYTHON_313_COMPAT" = true ]; then
        # Use latest pydantic for Python 3.13
        pip install --only-binary :all: "pydantic>=2.10.4"
    else
        pip install --no-binary pydantic-core pydantic==2.6.3 || pip install pydantic==2.6.3
    fi
    
    # Install the rest
    pip install -r $REQUIREMENTS_FILE --no-deps
fi

echo "   ✅ Python dependencies installed"
cd ../..

# Install Node.js dependencies
echo ""
echo "2️⃣ Installing Node.js dependencies..."
cd apps/web

# Clear cache if needed
if [ -d "node_modules" ]; then
    echo "   Clearing old node_modules..."
    rm -rf node_modules package-lock.json
fi

echo "   Installing packages..."
npm install

echo "   ✅ Node.js dependencies installed"
cd ../..

# Setup environment file
echo ""
echo "3️⃣ Setting up environment..."
if [ ! -f .env ]; then
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "   ✅ Created .env from example"
    else
        echo "   ⚠️ No .env.example found"
    fi
else
    echo "   ✅ .env already exists"
fi

# Database setup reminder
echo ""
echo "4️⃣ Database setup..."
echo "   Make sure PostgreSQL and Redis are installed:"
echo ""
echo "   macOS:"
echo "     brew install postgresql redis"
echo "     brew services start postgresql"
echo "     brew services start redis"
echo ""
echo "   Linux:"
echo "     sudo apt-get install postgresql redis-server"
echo "     sudo systemctl start postgresql"
echo "     sudo systemctl start redis"
echo ""
echo "   Or use Docker:"
echo "     docker-compose up -d postgres redis"

# Final check
echo ""
echo "========================================"
echo "✅ Installation complete!"
echo "========================================"
echo ""
echo "Next steps:"
echo "  1. Ensure PostgreSQL and Redis are running"
echo "  2. Run: make dev"
echo "  3. Open: http://localhost:3000"
echo ""
echo "If you encounter issues:"
echo "  - Check TROUBLESHOOTING.md"
echo "  - Ensure Python 3.9+ and Node 18+"
echo "  - Try: pip install --upgrade pip"
echo ""