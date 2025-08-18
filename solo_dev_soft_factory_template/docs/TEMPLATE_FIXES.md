# Template Fixes and Improvements

This document describes the fixes applied to resolve common setup issues with the Solo Software Factory template.

## Issues Fixed

### 1. ✅ Missing package.json in apps/web
**Problem:** Template may be missing the `package.json` file in the `apps/web` directory.

**Solution:** Added a complete Next.js `package.json` with:
- All required dependencies (React, Next.js, TypeScript)
- Configurable port support via environment variables
- Standard scripts (dev, build, test, lint)

### 2. ✅ Port Conflicts Resolution
**Problem:** Default ports (3000, 8000, 6379, 5432) often conflict with other services.

**Solution:** Made all ports configurable via environment variables:
- Updated `docker-compose.yml` to use `${PORT:-default}` syntax
- Modified `.env.example` with port configuration section
- Updated `package.json` to accept PORT environment variable

### 3. ✅ Docker Compose Version Warning
**Problem:** The `version: '3.8'` attribute is obsolete and shows warnings.

**Solution:** Removed the version attribute from `docker-compose.yml`.

### 4. ✅ Setup Validation Script
**Problem:** No way to check if the environment is properly configured before starting.

**Solution:** Created `scripts/validate-setup.sh` that checks:
- Required commands (Docker, Node.js, Python, etc.)
- Port availability
- Configuration files
- Dependencies installation status

### 5. ✅ Next.js App Structure
**Problem:** Missing basic Next.js app structure files.

**Solution:** Ensured the template includes:
- `apps/web/app/layout.tsx` - Basic layout component
- `apps/web/app/page.tsx` - Homepage component
- `apps/web/app/health/page.tsx` - Health check page
- `apps/web/app/api/health/route.ts` - Health API endpoint

## How to Use the Fixed Template

### Quick Start

```bash
# 1. Clone the template
git clone <your-repo-url>
cd <your-project>

# 2. Setup environment
cp .env.example .env

# 3. Validate setup
./scripts/validate-setup.sh

# 4. Fix any issues reported by validation script

# 5. Start development
make dev
```

### Handling Port Conflicts

If the validation script reports port conflicts, edit your `.env` file:

```env
# Custom port configuration
API_PORT=8007
WEB_PORT=3015
REDIS_PORT=6381
DB_PORT=5433
```

Then run `make dev` - the services will use your custom ports.

### Project-Specific Customization

After cloning the template for a new project:

1. Update `apps/web/package.json`:
   - Change `name`, `description`, `author`
   - Update `keywords` for your project

2. Update repository references:
   ```bash
   git remote remove origin
   git remote add origin <your-new-repo-url>
   ```

3. Update documentation:
   - Modify `README.md` with your project details
   - Update `CLAUDE.md` with project-specific instructions

## Validation Script Features

The `scripts/validate-setup.sh` script checks:

1. **Required Commands**
   - Docker and Docker Compose
   - Node.js and npm
   - Python 3
   - Git

2. **Configuration Files**
   - `.env` file existence
   - Frontend `package.json`
   - Backend `requirements.txt`

3. **Port Availability**
   - Checks all configured ports
   - Suggests environment variable changes if conflicts exist

4. **Dependencies**
   - Frontend node_modules
   - Python packages (basic check)

5. **Docker Status**
   - Ensures Docker daemon is running

## Common Issues and Solutions

### Issue: "Port already in use"
```bash
# Check what's using a port
lsof -i :3000

# Kill process using port (if safe)
kill -9 <PID>

# Or configure different port in .env
WEB_PORT=3015
```

### Issue: "Docker not running"
```bash
# macOS
open -a Docker

# Linux
sudo systemctl start docker

# WSL2
sudo service docker start
```

### Issue: "Dependencies not installed"
```bash
# Frontend
cd apps/web && npm install

# Backend
cd apps/api && pip install -r requirements.txt
```

## Template Improvements Applied

1. **Environment Variable Support**: All services now support environment-based configuration
2. **Validation Tooling**: Setup validation script ensures smooth onboarding
3. **Generic Naming**: Removed project-specific references (QuantX) from package.json
4. **Documentation**: Added comprehensive setup troubleshooting guide
5. **Port Flexibility**: Template works with any available ports

## Contributing Back

If you encounter additional issues or have improvements:

1. Document the issue clearly
2. Implement a fix that's generic enough for the template
3. Test with a fresh clone
4. Submit a pull request with:
   - Description of the issue
   - How the fix works
   - Any new dependencies or requirements