#!/bin/bash

# Check Python compatibility for Solo Software Factory

echo "🐍 Python Compatibility Check"
echo "=============================="
echo ""

# Find Python command
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "❌ Python not found!"
    echo "Please install Python 3.9 or later"
    exit 1
fi

# Get version info
PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

echo "Python version: $PYTHON_VERSION"
echo ""

# Check compatibility
if [ "$PYTHON_MAJOR" -ne 3 ]; then
    echo "❌ Python 3.x required (you have Python $PYTHON_MAJOR)"
    exit 1
fi

if [ "$PYTHON_MINOR" -lt 9 ]; then
    echo "❌ Python 3.9+ required (you have Python $PYTHON_VERSION)"
    echo "Please upgrade Python"
    exit 1
elif [ "$PYTHON_MINOR" -ge 13 ]; then
    echo "✅ Python 3.13+ detected"
    echo ""
    echo "📋 Special requirements for Python 3.13+:"
    echo "  • Will use psycopg 3.x instead of psycopg2"
    echo "  • Will use pydantic 2.10+ with pre-built wheels"
    echo "  • Requirements file: requirements-python313.txt"
    echo ""
    echo "Run ./install.sh to install with correct dependencies"
elif [ "$PYTHON_MINOR" -ge 9 ] && [ "$PYTHON_MINOR" -le 12 ]; then
    echo "✅ Python $PYTHON_VERSION is fully compatible"
    echo ""
    echo "📋 Will use standard requirements:"
    echo "  • psycopg2-binary for PostgreSQL"
    echo "  • pydantic 2.6.3"
    echo "  • Requirements file: requirements.txt"
    echo ""
    echo "Run ./install.sh to install dependencies"
fi

echo ""
echo "=============================="
echo "Checking for pip..."

if $PYTHON_CMD -m pip --version &> /dev/null; then
    PIP_VERSION=$($PYTHON_CMD -m pip --version | awk '{print $2}')
    echo "✅ pip $PIP_VERSION found"
    
    # Check if pip needs upgrade
    LATEST_PIP=$($PYTHON_CMD -m pip list --outdated 2>/dev/null | grep "^pip " | awk '{print $3}')
    if [ -n "$LATEST_PIP" ]; then
        echo "   ℹ️ pip can be upgraded to $LATEST_PIP"
        echo "   Run: pip install --upgrade pip"
    fi
else
    echo "❌ pip not found"
    echo "Install pip with: $PYTHON_CMD -m ensurepip"
fi

echo ""
echo "=============================="
echo "Ready to proceed with ./install.sh"