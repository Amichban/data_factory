#!/bin/bash

# Solo Software Factory - New Project Setup Script
# This script safely converts the template into your own project

set -e

echo "🚀 Solo Software Factory - Project Setup"
echo "========================================"
echo ""

# Get project name
read -p "Enter your project name (e.g., my-awesome-app): " PROJECT_NAME

if [ -z "$PROJECT_NAME" ]; then
    echo "❌ Project name is required!"
    exit 1
fi

echo ""
echo "📦 Setting up '$PROJECT_NAME'..."
echo ""

# Step 1: Remove template git history
echo "1️⃣ Removing template repository connection..."
if [ -d .git ]; then
    rm -rf .git
    echo "   ✅ Template git history removed"
else
    echo "   ℹ️ No git history found (already clean)"
fi

# Step 2: Remove template-specific files
echo ""
echo "2️⃣ Cleaning up template files..."
rm -f START_HERE.txt 2>/dev/null || true
rm -rf docs/archive 2>/dev/null || true
rm -f setup-new-project.sh 2>/dev/null || true  # Remove this script itself
echo "   ✅ Template files cleaned"

# Step 3: Initialize new git repository
echo ""
echo "3️⃣ Initializing your git repository..."
git init
echo "   ✅ Git initialized"

# Step 4: Update project files
echo ""
echo "4️⃣ Personalizing project files..."

# Update README.md
if [ -f README.md ]; then
    sed -i.bak "s/Solo Software Factory/$PROJECT_NAME/g" README.md && rm README.md.bak
    sed -i.bak "s/\[this-repo\]/[your-repo-url]/g" README.md && rm README.md.bak
    echo "   ✅ README.md updated"
fi

# Update package.json for web
if [ -f apps/web/package.json ]; then
    sed -i.bak "s/\"name\": \"web\"/\"name\": \"$PROJECT_NAME-web\"/g" apps/web/package.json && rm apps/web/package.json.bak
    echo "   ✅ Frontend package.json updated"
fi

# Update PROJECT_STATE.md
if [ -f .claude/PROJECT_STATE.md ]; then
    cat > .claude/PROJECT_STATE.md << EOF
# Project State - $PROJECT_NAME

## Overview
$PROJECT_NAME - Built with Solo Software Factory template

## Current Status
- **Phase**: Initial Setup
- **Stack**: FastAPI + Next.js + PostgreSQL + Redis
- **Created**: $(date +%Y-%m-%d)

## Active Work
- [ ] Project setup complete
- [ ] First feature planned

## Next Steps
1. Read HOW_TO_USE.md
2. Create first user story
3. Build first feature

## Sign-off
- Last Updated: $(date +%Y-%m-%d)
EOF
    echo "   ✅ PROJECT_STATE.md initialized"
fi

# Step 5: Create .env from example
echo ""
echo "5️⃣ Setting up environment..."
if [ -f .env.example ] && [ ! -f .env ]; then
    cp .env.example .env
    echo "   ✅ .env file created from example"
else
    echo "   ℹ️ .env already exists or no example found"
fi

# Step 6: Install dependencies (optional)
echo ""
echo "6️⃣ Dependencies..."
read -p "Install dependencies now? (y/n): " INSTALL_DEPS

if [[ $INSTALL_DEPS =~ ^[Yy]$ ]]; then
    echo "   Installing dependencies..."
    
    # Backend dependencies
    if [ -f apps/api/requirements.txt ]; then
        echo "   📦 Installing Python dependencies..."
        cd apps/api
        python3 -m venv venv 2>/dev/null || python -m venv venv
        source venv/bin/activate 2>/dev/null || venv\Scripts\activate
        pip install -r requirements.txt
        cd ../..
        echo "   ✅ Backend dependencies installed"
    fi
    
    # Frontend dependencies
    if [ -f apps/web/package.json ]; then
        echo "   📦 Installing Node dependencies..."
        cd apps/web
        npm install
        cd ../..
        echo "   ✅ Frontend dependencies installed"
    fi
else
    echo "   ℹ️ Skipping dependency installation"
    echo "   Run 'make install' later to install"
fi

# Step 7: Initial commit
echo ""
echo "7️⃣ Creating initial commit..."
git add .
git commit -m "🎉 Initial commit - $PROJECT_NAME from Solo Software Factory template"
echo "   ✅ Initial commit created"

# Step 8: Add remote (optional)
echo ""
echo "8️⃣ GitHub repository..."
echo ""
echo "To connect to GitHub:"
echo "  1. Create a new repository on GitHub (without README)"
echo "  2. Run these commands:"
echo ""
echo "     git remote add origin https://github.com/YOUR_USERNAME/$PROJECT_NAME.git"
echo "     git branch -M main"
echo "     git push -u origin main"
echo ""

# Step 9: Final instructions
echo "========================================="
echo "✅ Project '$PROJECT_NAME' is ready!"
echo "========================================="
echo ""
echo "📖 Next steps:"
echo "   1. Read HOW_TO_USE.md for complete guide"
echo "   2. Start development server: make dev"
echo "   3. Open Claude Code and build your first feature"
echo ""
echo "🎯 Quick commands:"
echo "   make dev        - Start development server"
echo "   make test       - Run tests"
echo "   make build      - Build for production"
echo ""
echo "Happy building! 🚀"