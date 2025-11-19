# Scripts Directory

This directory contains essential scripts for establishing and maintaining database relationships.

## Important Notes

**⚠️ Database Triggers**: Relationship linking scripts (`complete_quote_linkage.py` and `link_badlead_to_leadstatus.py`) are now largely replaced by database triggers. The triggers automatically link records on insert/update. These scripts are kept for backfilling existing NULL relationships.

**✅ Idempotent**: All scripts are now idempotent - they check if work has already been done and skip execution if no work is needed. Use `--force` to override this behavior.

## Organization

Scripts are organized by purpose:

### `relationships/`
Scripts that establish relationships between core models:
- `complete_quote_linkage.py` - Links LeadStatus and LostLead to BookedOpportunities via quote_number (now handled by triggers for new records)
- `link_badlead_to_leadstatus.py` - Links BadLead records to LeadStatus for complete lead tracking (now handled by triggers for new records)

### `lookup/`
Scripts that populate and maintain lookup tables:
- `populate_lead_sources.py` - Creates lead_sources lookup table and links records
- `populate_branches.py` - Creates branches lookup table and links records
- `merge_sales_person_variations.py` - Merges sales person name variations

### `timeline/`
Scripts that populate timeline and performance data:
- `populate_customer_timeline_fields.py` - Populates first_lead_date and conversion_date for customers
- `link_orphaned_performance_records.py` - Links orphaned UserPerformance and SalesPerformance records

## Usage

All scripts support `--dry-run` mode (default), `--execute` flag, and `--force` flag:

```bash
# Dry run (default) - shows what would be done
python scripts/relationships/complete_quote_linkage.py

# Execute changes (only if not already done)
python scripts/relationships/complete_quote_linkage.py --execute

# Force execution even if already run
python scripts/relationships/complete_quote_linkage.py --execute --force
```

### Idempotency

All scripts are idempotent by default:
- Scripts check if they've been executed before (via `script_execution_log` table)
- Scripts check if there's any work to do before executing
- If no work is needed, scripts exit early with a message
- Use `--force` to override idempotency checks

### Database Triggers

The following relationships are now automatically maintained by database triggers:
- **LeadStatus → BookedOpportunities**: Automatically linked via `quote_number` on insert/update
- **LostLead → BookedOpportunities**: Automatically linked via `quote_number` on insert/update
- **BadLead → LeadStatus**: Automatically linked via customer matching (email, phone, or customer_id) on insert/update

These triggers ensure new records are automatically linked without needing to run scripts.

## Execution Order

For initial setup, run scripts in this order:

1. **Apply database migration first** (creates triggers and execution log):
   ```bash
   # Run the migration file to create triggers
   psql -d data_analytics -f sql/migrations/20250101000000_relationship_triggers_and_execution_log.sql
   ```

2. **Lookup tables first**:
   ```bash
   python scripts/lookup/populate_lead_sources.py --execute
   python scripts/lookup/populate_branches.py --execute
   python scripts/lookup/merge_sales_person_variations.py --execute
   ```

3. **Then relationships** (for backfilling existing NULL relationships):
   ```bash
   python scripts/relationships/complete_quote_linkage.py --execute
   python scripts/relationships/link_badlead_to_leadstatus.py --execute
   ```
   Note: New records will be automatically linked by database triggers.

4. **Finally timeline**:
   ```bash
   python scripts/timeline/populate_customer_timeline_fields.py --execute
   python scripts/timeline/link_orphaned_performance_records.py --execute
   ```

## Running Scripts Multiple Times

All scripts are idempotent - you can run them multiple times safely:
- Scripts check if they've already been executed
- Scripts check if there's any work to do
- If no work is needed, scripts exit early

To force re-execution, use the `--force` flag:
```bash
python scripts/lookup/populate_lead_sources.py --execute --force
```

