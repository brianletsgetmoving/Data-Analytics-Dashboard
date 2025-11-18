# Database Migration Guide

This guide walks through applying all the latest database schema updates and data migrations.

## Prerequisites

1. Ensure PostgreSQL 16 is running
2. Backup your database before running migrations
3. Review all scripts in dry-run mode first

## Step 1: Create Prisma Migration

```bash
cd prisma
prisma migrate dev --name complete_schema_updates
```

This will:
- Create `lead_sources` lookup table
- Create `branches` lookup table
- Add `lead_status_id` to BadLead
- Add `lead_source_id` to LeadStatus, BadLead, LostLead
- Add `branch_id` to Jobs, BookedOpportunities, LeadStatus
- Add `first_lead_date`, `conversion_date`, and `merge_history` to Customer
- Create composite indexes for performance

## Step 2: Analyze Orphaned Records

```bash
python3 scripts/analyze_orphaned_performance_records.py
```

Review the reports in `reports/orphaned_performance_analysis/` to see:
- Orphaned UserPerformance records
- Orphaned SalesPerformance records
- Potential matches for linking

## Step 3: Link Orphaned Performance Records

First, run in dry-run mode:
```bash
python3 scripts/link_orphaned_performance_records.py --dry-run
```

Review the output, then execute:
```bash
python3 scripts/link_orphaned_performance_records.py --execute
```

## Step 4: Complete Quote Number Linkage

```bash
python3 scripts/complete_quote_linkage.py --dry-run
python3 scripts/complete_quote_linkage.py --execute
```

This links LeadStatus and LostLead records to BookedOpportunities via quote_number.

## Step 5: Link BadLead to LeadStatus

```bash
python3 scripts/link_badlead_to_leadstatus.py --dry-run
python3 scripts/link_badlead_to_leadstatus.py --execute
```

This links BadLead records to LeadStatus via customer matching.

## Step 6: Populate Lead Sources

```bash
python3 scripts/populate_lead_sources.py --dry-run
python3 scripts/populate_lead_sources.py --execute
```

This creates the lead_sources lookup table and links records.

## Step 7: Populate Branches

```bash
python3 scripts/populate_branches.py --dry-run
python3 scripts/populate_branches.py --execute
```

This creates the branches lookup table and links records.

## Step 8: Populate Customer Timeline Fields

```bash
python3 scripts/populate_customer_timeline_fields.py --dry-run
python3 scripts/populate_customer_timeline_fields.py --execute
```

This populates `first_lead_date` and `conversion_date` for customers.

## Step 9: Set Up Integrity Monitoring

First, create the monitoring table:
```bash
python3 scripts/setup_integrity_monitoring.py --setup --execute
```

Then run the integrity checks:
```bash
python3 scripts/setup_integrity_monitoring.py --execute
```

## Step 10: Verify All Changes

Run integrity checks to verify everything is linked correctly:
```bash
python3 scripts/setup_integrity_monitoring.py --execute
```

Check the reports in `reports/integrity_checks/` for any issues.

## Automated Daily Checks

To set up automated daily integrity checks, add to your cron or scheduler:

```bash
# Run daily at 2 AM
0 2 * * * cd /path/to/project && python3 scripts/setup_integrity_monitoring.py --execute >> /var/log/integrity_checks.log 2>&1
```

## Rollback

If you need to rollback:

1. Restore from database backup
2. Or manually revert Prisma migration:
   ```bash
   cd prisma
   prisma migrate resolve --rolled-back <migration_name>
   ```

## Troubleshooting

### Orphaned Records Still Exist

If orphaned records remain after linking:
1. Review the analysis reports
2. Manually review unmatched records
3. Update name normalization rules if needed
4. Re-run linking scripts

### Linkage Rates Below Threshold

If linkage rates are below expected thresholds:
1. Check data quality in source tables
2. Review matching logic in scripts
3. Consider manual intervention for edge cases
4. Update matching algorithms if needed

### Migration Errors

If Prisma migration fails:
1. Check database connection
2. Verify all dependencies are installed
3. Review error messages carefully
4. Consider running migrations in smaller batches

## Success Criteria

After completing all migrations, verify:

- ✅ No orphaned UserPerformance or SalesPerformance records
- ✅ Job-Customer linkage rate ≥ 95%
- ✅ LeadStatus-BookedOpportunity linkage rate ≥ 80%
- ✅ BadLead-LeadStatus linkage rate ≥ 70%
- ✅ All branches normalized and linked
- ✅ All lead sources normalized and linked
- ✅ Customer timeline fields populated
- ✅ Integrity monitoring table created and populated

