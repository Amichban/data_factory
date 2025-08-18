# Troubleshooting Guide

## Common Installation Issues

### Python Dependency Build Errors

#### Error: "Failed building wheel for psycopg2-binary"

**Solution for macOS:**
```bash
# Install PostgreSQL first
brew install postgresql

# Then retry
pip install psycopg2-binary
```

**Solution for Linux:**
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install libpq-dev python3-dev

# RHEL/CentOS/Fedora
sudo yum install postgresql-devel python3-devel

# Then retry
pip install psycopg2-binary
```

**Alternative solution:**
```bash
# Use pre-built binary
pip install --only-binary :all: psycopg2-binary
```

---

#### Error: "Failed building wheel for pydantic-core"

**Solution:**
```bash
# Upgrade pip and setuptools first
pip install --upgrade pip setuptools wheel

# Install with no-binary flag
pip install --no-binary pydantic-core pydantic

# Or use older version
pip install pydantic==2.5.0
```

---

#### Error: "Microsoft Visual C++ 14.0 is required" (Windows)

**Solution:**
1. Download Visual Studio Build Tools: https://visualstudio.microsoft.com/downloads/
2. Install "Desktop development with C++"
3. Restart terminal and retry

---

### Port Conflicts

#### Error: "Port 3000/8000 already in use"

**Solution:**
```bash
# Find what's using the port
lsof -i :3000  # macOS/Linux
netstat -ano | findstr :3000  # Windows

# Kill the process or change ports in .env
WEB_PORT=3001
API_PORT=8001
```

---

### Database Connection Issues

#### Error: "could not connect to server: Connection refused"

**Solution:**
```bash
# Check if PostgreSQL is running
pg_isready  # Should return "accepting connections"

# Start PostgreSQL
# macOS
brew services start postgresql

# Linux
sudo systemctl start postgresql

# Docker
docker-compose up -d postgres
```

---

#### Error: "FATAL: password authentication failed"

**Solution:**
```bash
# Update .env with correct credentials
DATABASE_URL=postgresql://dev:devpass@localhost:5432/app_dev

# Or create the database and user
psql -U postgres
CREATE USER dev WITH PASSWORD 'devpass';
CREATE DATABASE app_dev OWNER dev;
\q
```

---

### Node.js Issues

#### Error: "npm ERR! code ERESOLVE"

**Solution:**
```bash
# Clear cache and reinstall
cd apps/web
rm -rf node_modules package-lock.json
npm cache clean --force
npm install --legacy-peer-deps
```

---

#### Error: "Module not found"

**Solution:**
```bash
# Reinstall dependencies
cd apps/web
npm install
npm run build
```

---

### Docker Issues

#### Error: "Cannot connect to Docker daemon"

**Solution:**
```bash
# Start Docker Desktop (macOS/Windows)
# Or on Linux:
sudo systemctl start docker

# Verify Docker is running
docker ps
```

---

#### Error: "docker-compose: command not found"

**Solution:**
```bash
# Install Docker Compose
# macOS
brew install docker-compose

# Linux
sudo apt-get install docker-compose

# Or use Docker Compose V2
docker compose up  # Note: no hyphen
```

---

### Git Issues

#### Error: "fatal: not a git repository"

**Solution:**
```bash
# Initialize git
git init
git add .
git commit -m "Initial commit"
```

---

#### Warning: "You are still connected to template repository"

**Solution:**
```bash
# Run the setup script
./setup-new-project.sh

# Or manually disconnect
git remote remove origin
git remote add origin YOUR_REPO_URL
```

---

### Claude Code Issues

#### Error: "Command not found: claude"

**Solution:**
```bash
# Install Claude Code CLI
# Visit: https://claude.ai/code
# Follow installation instructions for your OS
```

---

#### Error: "/user-story command not recognized"

**Solution:**
```bash
# Ensure you're in Claude Code interface
# Commands only work within Claude Code, not terminal
```

---

### General Python Issues

#### Error: "No module named 'venv'"

**Solution:**
```bash
# Install python venv
# Ubuntu/Debian
sudo apt-get install python3-venv

# RHEL/CentOS
sudo yum install python3-venv

# macOS (should be included)
# If not, reinstall Python from python.org
```

---

#### Error: "pip: command not found"

**Solution:**
```bash
# Install pip
# macOS
python3 -m ensurepip

# Linux
sudo apt-get install python3-pip

# Windows
python -m ensurepip
```

---

## Quick Fixes

### Complete Reset
```bash
# Nuclear option - start fresh
rm -rf apps/api/venv
rm -rf apps/web/node_modules
rm -rf apps/web/.next
rm -f apps/web/package-lock.json
./install.sh
```

### Update Everything
```bash
# Update Python packages
cd apps/api
source venv/bin/activate
pip install --upgrade -r requirements.txt

# Update Node packages
cd ../web
npm update
npm audit fix
```

### Check System Requirements
```bash
# Verify versions
python3 --version  # Should be 3.9+
node --version     # Should be 18+
npm --version      # Should be 8+
docker --version   # Should be 20+
pg_isready         # PostgreSQL should be running
redis-cli ping     # Should return PONG
```

---

## Still Having Issues?

1. **Check the logs:**
   ```bash
   docker-compose logs api
   docker-compose logs web
   ```

2. **Enable debug mode:**
   ```bash
   # In .env
   DEBUG=true
   LOG_LEVEL=debug
   ```

3. **Ask Claude:**
   ```
   claude
   /architect I'm getting [error message]. How do I fix it?
   ```

4. **Common solutions:**
   - Restart your terminal
   - Restart Docker Desktop
   - Clear all caches
   - Use the install script: `./install.sh`

---

## Platform-Specific Notes

### macOS
- Use Homebrew for system dependencies
- May need Xcode Command Line Tools: `xcode-select --install`
- PostgreSQL via Homebrew is recommended

### Linux
- Use system package manager for dependencies
- May need sudo for global installs
- Check SELinux/AppArmor permissions

### Windows
- Use WSL2 for best compatibility
- Or use Docker Desktop with WSL2 backend
- Git Bash recommended for scripts

### Docker (All Platforms)
- Simplest approach - everything containerized
- Just need Docker Desktop installed
- Use `docker-compose up` instead of local services