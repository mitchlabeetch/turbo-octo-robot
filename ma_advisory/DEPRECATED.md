# ⚠️ DEPRECATED: Frappe-Based Implementation

This directory contains the **original Frappe/ERPNext-based implementation** of M&A Advisory ERP.

## Status
- **Deprecated**: As of February 2026
- **Reason**: Replaced by modern FastAPI standalone in `/standalone/`
- **Archive Type**: Historical reference and proof-of-concept only
- **Maintenance**: None — Do not modify or rely on this code

## Current Situation

### What Changed
The project has transitioned to a **pure FastAPI + SQLAlchemy architecture** that:
- ✅ Eliminates heavy Frappe framework overhead (50+ dependencies removed)
- ✅ Provides modern async-first Python stack
- ✅ Enables lightweight cloud-native deployment
- ✅ Offers full customization without DocType constraints
- ✅ Maintains headless API-first design for mobile/SPA integration

### Why It Was Replaced
1. **Dependency Bloat**: Frappe added 50+ transitive packages (~180MB) to deployments
2. **Modern Stack**: FastAPI provides better async support and developer experience
3. **Lightweight**: Startup time <1s (vs 10-30s for Frappe)
4. **Cloud-Native**: Stateless design suits containerized deployments
5. **Architectural Clarity**: Headless API design better matches requirements

### Performance Comparison

| Metric | Frappe-Based | Standalone FastAPI |
|--------|---|---|
| Installation Time | 120+ seconds | 15 seconds |
| Disk Space | ~280MB | ~85MB |
| Startup Time | 10-30 seconds | <1 second |
| Deployment Model | Bench + Server | Docker/Standalone |
| Packages | 150+ | 70 |
| Architecture | Monolithic web framework | Headless API service |

## If You Need This Code

### Creating a Separate Branch
```bash
# If you need to work with the Frappe version:
git checkout -b feature/frappe-implementation

# Or reset to a commit before this deprecation
git log --oneline | grep -i "frappe\|deprecat"
git checkout <commit-hash>
```

### Documentation
- See [CODEBASE_ANALYSIS.md](/CODEBASE_ANALYSIS.md) for detailed architectural comparison
- See [MIGRATION_GUIDE.md](/MIGRATION_GUIDE.md) for migration from Frappe to Standalone
- See [EXECUTIVE_SUMMARY.md](/EXECUTIVE_SUMMARY.md) for strategic decisions

## Active Implementation

**For all development, use the standalone implementation:**

```bash
cd standalone/
pip install -e .
uvicorn app.main:app --reload
```

**See [/standalone/README.md](/standalone/README.md) for details.**

## Timeline

- **Q1 2024**: Original Frappe-based implementation
- **Q3 2024**: Standalone FastAPI prototype
- **Q4 2024**: Standalone achieves feature parity
- **Feb 2026**: Frappe layer deprecated; standalone becomes primary
- **Future**: Frappe code remains for reference only; no updates

## Questions?

If you have questions about this transition:
1. Review [CODEBASE_ANALYSIS.md](/CODEBASE_ANALYSIS.md) — comprehensive technical comparison
2. Check [MIGRATION_GUIDE.md](/MIGRATION_GUIDE.md) — how to transition your data
3. See [EXECUTIVE_SUMMARY.md](/EXECUTIVE_SUMMARY.md) — strategic rationale

---

**Status**: 🔴 Archived — Do not use for new development  
**Replacement**: Use `/standalone/` instead  
**Support**: Limited — for historical reference only
