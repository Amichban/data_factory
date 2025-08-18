#!/bin/bash

# Check Repository Status - Verify you're not connected to template repo

echo "🔍 Checking Repository Status"
echo "=============================="
echo ""

# Check if git is initialized
if [ ! -d .git ]; then
    echo "✅ No git repository found - Ready for setup!"
    echo ""
    echo "Run: ./setup-new-project.sh to initialize your project"
    exit 0
fi

# Check remote origin
REMOTE_URL=$(git config --get remote.origin.url 2>/dev/null)

if [ -z "$REMOTE_URL" ]; then
    echo "✅ No remote repository configured"
    echo "   This is YOUR local repository"
    echo ""
    echo "To connect to GitHub:"
    echo "  1. Create a new repo on GitHub"
    echo "  2. git remote add origin YOUR_REPO_URL"
    echo "  3. git push -u origin main"
else
    echo "⚠️  Remote repository configured:"
    echo "   $REMOTE_URL"
    echo ""
    
    # Check if it's the template repo
    if [[ "$REMOTE_URL" == *"solo_soft_factory"* ]] || [[ "$REMOTE_URL" == *"solo-software-factory"* ]] || [[ "$REMOTE_URL" == *"template"* ]]; then
        echo "❌ WARNING: You're still connected to the template repository!"
        echo ""
        echo "To fix this:"
        echo "  Option 1: Run ./setup-new-project.sh (recommended)"
        echo "  Option 2: Manually change remote:"
        echo "    git remote remove origin"
        echo "    git remote add origin YOUR_NEW_REPO_URL"
        echo ""
        echo "DO NOT commit/push until you fix this!"
        exit 1
    else
        echo "✅ Connected to your own repository"
        echo "   Safe to commit and push"
    fi
fi

echo ""
echo "Current branch: $(git branch --show-current)"
echo "Last commit: $(git log -1 --oneline 2>/dev/null || echo 'No commits yet')"
echo ""

# Check for uncommitted changes
if [ -n "$(git status --porcelain 2>/dev/null)" ]; then
    echo "📝 You have uncommitted changes:"
    git status --short
else
    echo "✨ Working directory clean"
fi

echo ""
echo "=============================="
echo "Status check complete!"