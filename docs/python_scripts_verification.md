# Python Scripts Verification

This document verifies that all Python scripts in `scripts/` accept the `--execute` flag and return proper exit codes.

## Script Verification Status

### ✅ Scripts with `--execute` Flag

All scripts below support the `--execute` flag and return proper exit codes (0 for success, 1 for failure).

#### 1. `scripts/relationships/complete_quote_linkage.py`
- **Status:** ✅ Verified
- **`--execute` Flag:** ✅ Supported
- **Exit Codes:** ✅ Returns 0 on success, 1 on failure
- **Additional Flags:** `--force` (force execution even if already run)
- **Pattern:** Uses `argparse` with `--execute` flag, `dry_run = not args.execute`
- **Exit Pattern:** `sys.exit(main())` with `return 0` or `return 1`

#### 2. `scripts/relationships/link_badlead_to_leadstatus.py`
- **Status:** ✅ Verified
- **`--execute` Flag:** ✅ Supported
- **Exit Codes:** ✅ Returns 0 on success, 1 on failure
- **Additional Flags:** `--force` (force execution even if already run)
- **Pattern:** Uses `argparse` with `--execute` flag, `dry_run = not args.execute`
- **Exit Pattern:** `sys.exit(main())` with `return 0` or `return 1`

#### 3. `scripts/lookup/populate_lead_sources.py`
- **Status:** ✅ Verified
- **`--execute` Flag:** ✅ Supported
- **Exit Codes:** ✅ Returns 0 on success, 1 on failure
- **Additional Flags:** `--force` (force execution even if already run)
- **Pattern:** Uses `argparse` with `--execute` flag, `dry_run = not args.execute`
- **Exit Pattern:** `sys.exit(main())` with `return 0` or `return 1`

#### 4. `scripts/lookup/populate_branches.py`
- **Status:** ✅ Verified
- **`--execute` Flag:** ✅ Supported
- **Exit Codes:** ✅ Returns 0 on success, 1 on failure
- **Additional Flags:** `--force` (force execution even if already run)
- **Pattern:** Uses `argparse` with `--execute` flag, `dry_run = not args.execute`
- **Exit Pattern:** `sys.exit(main())` with `return 0` or `return 1`

#### 5. `scripts/timeline/populate_customer_timeline_fields.py`
- **Status:** ✅ Verified
- **`--execute` Flag:** ✅ Supported
- **Exit Codes:** ✅ Returns 0 on success, 1 on failure
- **Additional Flags:** `--force` (force execution even if already run)
- **Pattern:** Uses `argparse` with `--execute` flag, `dry_run = not args.execute`
- **Exit Pattern:** `sys.exit(main())` with `return 0` or `return 1`

#### 6. `scripts/timeline/link_orphaned_performance_records.py`
- **Status:** ✅ Verified
- **`--execute` Flag:** ✅ Supported
- **Exit Codes:** ✅ Returns 0 on success, 1 on failure
- **Additional Flags:** `--force` (force execution even if already run)
- **Pattern:** Uses `argparse` with `--execute` flag, `dry_run = not args.execute`
- **Exit Pattern:** `sys.exit(main())` with `return 0` or `return 1`

### ⚠️ Script Without `--execute` Flag

#### 7. `scripts/lookup/merge_sales_person_variations.py`
- **Status:** ⚠️ Does NOT support `--execute` flag
- **`--execute` Flag:** ❌ Not supported
- **Exit Codes:** ✅ Returns 0 on success, 1 on failure
- **Additional Flags:** `--force` (force execution even if already run)
- **Pattern:** Always executes (no dry-run mode)
- **Exit Pattern:** `sys.exit(main())` with `return 0` or `return 1`
- **Note:** This script always executes immediately and does not support dry-run mode. This may be intentional as it's a safe merge operation, but it's inconsistent with other scripts.

## Common Patterns

### Standard Script Structure

All scripts (except `merge_sales_person_variations.py`) follow this pattern:

```python
def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='...')
    parser.add_argument('--dry-run', action='store_true', default=True,
                       help='Run in dry-run mode (default: True)')
    parser.add_argument('--execute', action='store_true',
                       help='Execute the updates (overrides dry-run)')
    parser.add_argument('--force', action='store_true',
                       help='Force execution even if already run')
    
    args = parser.parse_args()
    dry_run = not args.execute
    
    if dry_run:
        logger.info("Running in DRY RUN mode. Use --execute to apply changes.")
    else:
        logger.info("EXECUTING updates to database.")
    
    conn = get_db_connection()
    try:
        # Check if script should run (idempotency check)
        if not dry_run and not check_and_log_execution(conn, SCRIPT_NAME, force=args.force,
                                                      notes="..."):
            return 0
        
        # ... script logic ...
        
        return 0
        
    except Exception as e:
        logger.error(f"Operation failed: {e}")
        logger.exception(e)
        conn.rollback()
        return 1
    finally:
        conn.close()

if __name__ == '__main__':
    sys.exit(main())
```

### Exit Code Standards

All scripts follow these exit code standards:
- **0:** Success (operation completed successfully or no work needed)
- **1:** Failure (error occurred during execution)

### Idempotency

All scripts use `check_and_log_execution()` from `scripts/utils/script_execution.py` to:
- Check if script has already been executed
- Log script execution to database
- Support `--force` flag to bypass idempotency check

## Recommendations

### For Agent 2 (Backend Specialist)

When implementing `ETLService.ts` to execute Python scripts:

1. **Always use `--execute` flag** when calling scripts (except `merge_sales_person_variations.py`)
2. **Check exit codes:**
   - Exit code 0 = success
   - Exit code 1 = failure
3. **Handle `merge_sales_person_variations.py` specially** - it doesn't need `--execute` flag
4. **Capture stdout/stderr** for logging and error reporting
5. **Set working directory** to project root when executing scripts
6. **Set environment variables** (DATABASE_URL, etc.) before execution

### Example ETLService Implementation Pattern

```typescript
async executeScript(scriptPath: string, force: boolean = false): Promise<ETLExecutionResult> {
  const scriptName = path.basename(scriptPath, '.py');
  const args = ['--execute'];
  
  if (force) {
    args.push('--force');
  }
  
  // Special case: merge_sales_person_variations.py doesn't use --execute
  if (scriptName === 'merge_sales_person_variations') {
    args.pop(); // Remove --execute
  }
  
  const result = await execFile('python3', [scriptPath, ...args], {
    cwd: process.cwd(),
    env: { ...process.env, DATABASE_URL: this.dbUrl },
  });
  
  return {
    success: result.exitCode === 0,
    exitCode: result.exitCode,
    logs: result.stdout.split('\n'),
    error: result.exitCode !== 0 ? result.stderr : undefined,
  };
}
```

## Summary

| Script | `--execute` Flag | Exit Codes | Status |
|--------|-----------------|------------|--------|
| `complete_quote_linkage.py` | ✅ | ✅ | Verified |
| `link_badlead_to_leadstatus.py` | ✅ | ✅ | Verified |
| `populate_lead_sources.py` | ✅ | ✅ | Verified |
| `populate_branches.py` | ✅ | ✅ | Verified |
| `populate_customer_timeline_fields.py` | ✅ | ✅ | Verified |
| `link_orphaned_performance_records.py` | ✅ | ✅ | Verified |
| `merge_sales_person_variations.py` | ❌ | ✅ | Verified (no dry-run) |

**Total:** 7 scripts verified
- 6 scripts support `--execute` flag ✅
- 1 script does not support `--execute` flag (always executes) ⚠️
- All 7 scripts return proper exit codes ✅

