# Scripts Directory

This directory contains essential scripts for establishing and maintaining database relationships.

## Organization

Scripts are organized by purpose:

### `relationships/`
Scripts that establish relationships between core models:
- `complete_quote_linkage.py` - Links LeadStatus and LostLead to BookedOpportunities via quote_number
- `link_badlead_to_leadstatus.py` - Links BadLead records to LeadStatus for complete lead tracking

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

All scripts support `--dry-run` mode (default) and `--execute` flag:

```bash
# Dry run (default)
python scripts/relationships/complete_quote_linkage.py

# Execute changes
python scripts/relationships/complete_quote_linkage.py --execute
```

## Execution Order

For initial setup, run scripts in this order:

1. **Lookup tables first**:
   ```bash
   python scripts/lookup/populate_lead_sources.py --execute
   python scripts/lookup/populate_branches.py --execute
   python scripts/lookup/merge_sales_person_variations.py --execute
   ```

2. **Then relationships**:
   ```bash
   python scripts/relationships/complete_quote_linkage.py --execute
   python scripts/relationships/link_badlead_to_leadstatus.py --execute
   ```

3. **Finally timeline**:
   ```bash
   python scripts/timeline/populate_customer_timeline_fields.py --execute
   python scripts/timeline/link_orphaned_performance_records.py --execute
   ```

