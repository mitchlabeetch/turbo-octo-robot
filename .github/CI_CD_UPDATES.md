# CI/CD Pipeline Updates

## Overview

This document describes the updated CI/CD pipeline introduced in v2.0.0 to support the standalone-first architecture.

## Workflows

### 1. Test Standalone FastAPI App (`test-standalone.yml`)

**Trigger**: Push/PR to `main|develop` when `standalone/**` changes

**Steps**:
- Lint with ruff (code style)
- Verify no Frappe/ERPNext imports
- Type checking via Pydantic
- Unit tests (pytest)
- Docker build validation

**Matrix**: Python 3.10, 3.11, 3.12

**Duration**: ~2-3 minutes

### 2. Verify Dependency Cleanup (`verify-dependencies.yml`)

**Trigger**: Changes to pyproject.toml, requirements.txt, version

**Checks**:
- ✅ No Frappe/ERPNext in root pyproject.toml
- ✅ requirements.txt documents architecture
- ✅ Standalone is self-contained
- ✅ Version >= 2.0.0 (breaking change marker)
- ✅ No Frappe imports in standalone/app
- ✅ Documentation files exist (MIGRATION_GUIDE, CODEBASE_ANALYSIS, DEPRECATED)
- 📦 Dependency audit (vulnerabilities)

**Duration**: ~1-2 minutes

### 3. Code Quality (`code-quality.yml`)

**Trigger**: Changes to standalone/app

**Checks**:
- 🔍 Ruff linting (code style)
- 📐 Format validation
- 🔐 Bandit security scan
- ✅ Pydantic model validation
- 🏷️ MyPy type checking

**Duration**: ~2 minutes

## Key Changes from Legacy

| Aspect | Before | After |
|--------|--------|-------|
| Test Directory | `/` (root + Frappe) | `/standalone` only |
| Dependencies Tracked | 150+ packages | 70 packages |
| Python Versions | Single (3.9) | 3.10, 3.11, 3.12 |
| Verification | Basic | Comprehensive (dependency, security, architecture) |
| Total CI Time | ~5 minutes | ~3-5 minutes |

## Configuration Files

### pyproject.toml (Root)

- No dependencies (meta-package only)
- Points to `/standalone/` for active app
- Version: 2.0.0+ (breaking change marker)

### standalone/pyproject.toml

- **Authoritative** dependency source
- 11 core packages (FastAPI, SQLAlchemy, Pydantic, etc.)
- Optional groups: `dev`, `watermarking`

## Running Workflows Locally

### Test Standalone
```bash
cd standalone/
pip install -e ".[dev]"
pytest
```

### Verify Dependencies
```bash
# Check for Frappe imports
grep -r "frappe\|erpnext" --include="*.py" standalone/app/

# Test standalone works alone
cd standalone/
python -c "from app.main import app; print('✅ Works')"
```

### Code Quality
```bash
cd standalone/
ruff check app/
pip install bandit
bandit -r app/ -ll
```

## Architecture Enforcement

The CI/CD pipeline enforces:

1. **Standalone Independence**: No Frappe/ERPNext imports
2. **Metadata Consistency**: Version >= 2.0.0, requirements.txt documentation
3. **Security**: Bandit scans for common vulnerabilities
4. **Code Style**: Ruff linting and formatting
5. **Type Safety**: Pydantic validation, MyPy checking

## Future Enhancements

Planned workflow additions:
- [ ] Integration tests with real database
- [ ] Performance benchmarking
- [ ] Docker image push to registry
- [ ] Changelog auto-generation from commits
- [ ] Release notes generation

## Troubleshooting

### Workflow fails on Python 3.10
```bash
# Update pyproject.toml requires-python
requires-python = ">=3.10"
```

### Too many Ruff warnings
```bash
# Fix format automatically
cd standalone/
ruff format app/
ruff check app/ --fix
```

### Dependency audit fails
```bash
# Review vulnerabilities
pip install pip-audit
cd standalone/
pip install -e .
pip-audit
```

## Rollback

If CI/CD causes issues:

```bash
# Remove problematic workflows
git rm .github/workflows/*.yml
git commit -m "Revert: CI/CD workflows"
git push

# Or revert entire Phase 4 commit
git revert <commit-hash>
```

## Contact

For questions about CI/CD pipeline:
- See DEPENDENCY_CLEANUP_PLAN.md Phase 4
- Review workflow files in `.github/workflows/`
- File an issue with CI/CD tag
