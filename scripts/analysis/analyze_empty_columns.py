#!/usr/bin/env python3
"""
Analyze empty/NULL columns across all database models and map to available raw data sources.
"""

import sys
from pathlib import Path
import psycopg2
import logging
from typing import Dict, List, Tuple
import json
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.utils.database import get_db_connection

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Define all tables and their columns (excluding auto-generated fields)
TABLES_TO_ANALYZE = {
    'jobs': [
        'job_id', 'job_number', 'opportunity_status', 'job_date', 'sales_person_name',
        'sales_person_id', 'branch_name', 'branch_id', 'job_type', 'customer_name',
        'customer_email', 'customer_phone', 'referral_source', 'affiliate_name',
        'created_at_utc', 'booked_at_utc', 'hourly_rate_quoted', 'total_estimated_cost',
        'actual_number_crew', 'actual_number_trucks', 'hourly_rate_billed', 'total_actual_cost',
        'origin_address', 'origin_street', 'origin_city', 'origin_state', 'origin_zip',
        'origin_type', 'destination_address', 'destination_street', 'destination_city',
        'destination_state', 'destination_zip', 'destination_type', 'customer_id'
    ],
    'bad_leads': [
        'provider', 'customer_name', 'customer_email', 'customer_phone', 'move_date',
        'date_lead_received', 'lead_bad_reason', 'customer_id', 'lead_status_id', 'lead_source_id'
    ],
    'booked_opportunities': [
        'quote_number', 'status', 'customer_name', 'email', 'phone_number', 'branch_name',
        'branch_id', 'moving_from', 'moving_to', 'service_date', 'service_type',
        'hourly_rate', 'estimated_amount', 'invoiced_amount', 'referral_source',
        'sales_person_id', 'booked_date', 'customer_id'
    ],
    'lead_status': [
        'quote_number', 'booked_opportunity_id', 'branch_name', 'branch_id', 'status',
        'sales_person_id', 'time_to_contact', 'referral_source', 'lead_source_id'
    ],
    'lost_leads': [
        'quote_number', 'booked_opportunity_id', 'name', 'lost_date', 'move_date',
        'reason', 'date_received', 'time_to_first_contact', 'lead_source_id'
    ],
    'user_performance': [
        'name', 'sales_person_id', 'user_status', 'total_calls', 'avg_calls_per_day',
        'inbound_count', 'outbound_count', 'missed_percent', 'avg_handle_time'
    ],
    'sales_performance': [
        'name', 'sales_person_id', 'leads_received', 'bad', 'percent_bad', 'sent',
        'percent_sent', 'pending', 'percent_pending', 'booked', 'percent_booked',
        'lost', 'percent_lost', 'cancelled', 'percent_cancelled', 'booked_total',
        'average_booking'
    ],
    'customers': [
        'smartmoving_id', 'name', 'first_name', 'last_name', 'email', 'phone',
        'origin_city', 'origin_state', 'origin_zip', 'origin_address',
        'destination_city', 'destination_state', 'destination_zip', 'destination_address',
        'gender', 'gender_confidence', 'gender_method', 'first_lead_date', 'conversion_date'
    ],
    'sales_persons': [
        'name', 'normalized_name'
    ],
    'branches': [
        'name', 'normalized_name', 'city', 'state', 'is_active'
    ],
    'lead_sources': [
        'name', 'category', 'is_active'
    ]
}

# Map raw data files to potential column matches
RAW_DATA_MAPPING = {
    'data/raw/RingCentral_PR_Users_Users_11_17_2025_3_24_34_PM.xlsx - Users.csv': {
        'target_tables': ['user_performance', 'sales_persons'],
        'columns': {
            'Name': 'name',
            'User Status': 'user_status',
            'Total Calls': 'total_calls',
            'Avg. Calls/Day': 'avg_calls_per_day',
            '# Inbound': 'inbound_count',
            '# Outbound': 'outbound_count',
            '% Missed (w/VM)': 'missed_percent',
            'Avg. Handle Time': 'avg_handle_time'
        }
    },
    'data/raw/sales-person-performance (1).xlsx - data (1).csv': {
        'target_tables': ['sales_performance', 'sales_persons'],
        'columns': {
            'Name': 'name',
            '# Leads Received': 'leads_received',
            'Bad': 'bad',
            '% Bad': 'percent_bad',
            'Sent': 'sent',
            '% Sent': 'percent_sent',
            'Pending': 'pending',
            '% Pending': 'percent_pending',
            'Booked': 'booked',
            '% Booked': 'percent_booked',
            'Lost': 'lost',
            '% Lost': 'percent_lost',
            'Cancelled': 'cancelled',
            '% Cancelled': 'percent_cancelled',
            'Booked Total': 'booked_total',
            'Average Booking': 'average_booking'
        }
    },
    'data/raw/lead-status.csv': {
        'target_tables': ['lead_status'],
        'columns': {
            'Quote #': 'quote_number',
            'Branch Name': 'branch_name',
            'Status': 'status',
            'Sales Person': 'sales_person_name',
            'Time to Contact': 'time_to_contact',
            'Referral Source': 'referral_source'
        }
    },
    'data/raw/bad-leads.xlsx - data.csv': {
        'target_tables': ['bad_leads'],
        'columns': {
            'Provider': 'provider',
            'Customer Name': 'customer_name',
            'Customer Email': 'customer_email',
            'Customer Phone': 'customer_phone',
            'Move Date': 'move_date',
            'Date Lead Received': 'date_lead_received',
            'Lead Bad Reason': 'lead_bad_reason'
        }
    },
    'data/raw/lost-leads-opportunities-details.xlsx - data.csv': {
        'target_tables': ['lost_leads'],
        'columns': {
            'Quote #': 'quote_number',
            'Name': 'name',
            'Lost Date': 'lost_date',
            'Move Date': 'move_date',
            'Reason': 'reason',
            'Date Received': 'date_received',
            'Time to First Contact': 'time_to_first_contact'
        }
    }
}


def analyze_table_columns(conn, table_name: str, columns: List[str]) -> Dict:
    """Analyze NULL/empty values for a table's columns."""
    cursor = conn.cursor()
    results = {'total_rows': 0, 'columns': {}}
    
    try:
        # Get total row count
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        total_rows = cursor.fetchone()[0]
        
        if total_rows == 0:
            logger.warning(f"Table {table_name} is empty")
            return {'total_rows': 0, 'columns': {}}
        
        results['total_rows'] = total_rows
        
        # Analyze each column
        for column in columns:
            try:
                # Count NULL values - use quote_ident to safely quote column names
                from psycopg2.extensions import quote_ident
                quoted_column = quote_ident(column, conn)
                quoted_table = quote_ident(table_name, conn)
                
                cursor.execute(f"""
                    SELECT 
                        COUNT(*) as total,
                        COUNT({quoted_column}) as non_null,
                        COUNT(*) - COUNT({quoted_column}) as null_count
                    FROM {quoted_table}
                """)
                
                total, non_null, null_count = cursor.fetchone()
                
                # Count empty strings (if text type)
                empty_count = 0
                try:
                    cursor.execute(f"""
                        SELECT COUNT(*) 
                        FROM {quoted_table} 
                        WHERE {quoted_column} = '' OR {quoted_column} = ' '
                    """)
                    empty_count = cursor.fetchone()[0]
                except:
                    pass  # Column might not be text type
                
                null_percentage = (null_count / total_rows * 100) if total_rows > 0 else 0
                empty_percentage = (empty_count / total_rows * 100) if total_rows > 0 else 0
                
                results['columns'][column] = {
                    'null_count': null_count,
                    'null_percentage': round(null_percentage, 2),
                    'empty_count': empty_count,
                    'empty_percentage': round(empty_percentage, 2),
                    'non_null_count': non_null,
                    'fillable': null_count > 0 or empty_count > 0
                }
                
            except Exception as e:
                # Rollback on error to continue with next column
                conn.rollback()
                logger.warning(f"Error analyzing column {table_name}.{column}: {e}")
                results['columns'][column] = {
                    'error': str(e)
                }
    
    finally:
        cursor.close()
    
    return results


def map_to_raw_data(table_name: str, column_name: str) -> List[Dict]:
    """Map a table column to potential raw data sources."""
    mappings = []
    
    for raw_file, mapping_info in RAW_DATA_MAPPING.items():
        if table_name in mapping_info['target_tables']:
            if column_name in mapping_info['columns'].values():
                # Find the CSV column name
                csv_column = None
                for csv_col, db_col in mapping_info['columns'].items():
                    if db_col == column_name:
                        csv_column = csv_col
                        break
                
                if csv_column:
                    mappings.append({
                        'raw_file': raw_file,
                        'csv_column': csv_column,
                        'db_column': column_name,
                        'target_table': table_name
                    })
    
    return mappings


def generate_report(conn) -> Dict:
    """Generate comprehensive analysis report."""
    logger.info("Starting empty column analysis...")
    
    report = {
        'generated_at': datetime.now().isoformat(),
        'tables': {},
        'summary': {
            'total_tables': len(TABLES_TO_ANALYZE),
            'total_columns_analyzed': 0,
            'columns_with_nulls': 0,
            'fillable_columns': 0
        }
    }
    
    for table_name, columns in TABLES_TO_ANALYZE.items():
        logger.info(f"Analyzing table: {table_name}")
        
        try:
            analysis = analyze_table_columns(conn, table_name, columns)
            report['tables'][table_name] = analysis
            
            # Add raw data mappings for fillable columns
            if 'columns' in analysis:
                for column_name, column_data in analysis['columns'].items():
                    report['summary']['total_columns_analyzed'] += 1
                    
                    if column_data.get('fillable', False):
                        report['summary']['columns_with_nulls'] += 1
                        
                        # Check if we can fill from raw data
                        mappings = map_to_raw_data(table_name, column_name)
                        if mappings:
                            report['summary']['fillable_columns'] += 1
                            column_data['raw_data_sources'] = mappings
                    
                    if column_data.get('null_count', 0) > 0:
                        report['summary']['columns_with_nulls'] += 1
        
        except Exception as e:
            logger.error(f"Error analyzing table {table_name}: {e}")
            report['tables'][table_name] = {'error': str(e)}
    
    return report


def main():
    """Main execution function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Analyze empty columns across all database models')
    parser.add_argument('--output', '-o', type=str, default='empty_columns_analysis.json',
                       help='Output file for analysis report (default: empty_columns_analysis.json)')
    parser.add_argument('--dry-run', action='store_true', help='Dry run mode (no changes)')
    
    args = parser.parse_args()
    
    conn = get_db_connection()
    
    try:
        report = generate_report(conn)
        
        # Save report to file
        output_path = Path(__file__).parent.parent.parent / args.output
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"\n{'='*80}")
        logger.info("ANALYSIS SUMMARY")
        logger.info(f"{'='*80}")
        logger.info(f"Total tables analyzed: {report['summary']['total_tables']}")
        logger.info(f"Total columns analyzed: {report['summary']['total_columns_analyzed']}")
        logger.info(f"Columns with NULL/empty values: {report['summary']['columns_with_nulls']}")
        logger.info(f"Fillable columns (with raw data sources): {report['summary']['fillable_columns']}")
        logger.info(f"\nReport saved to: {output_path}")
        logger.info(f"{'='*80}\n")
        
        # Print top fillable columns
        logger.info("Top fillable columns by NULL percentage:")
        fillable_list = []
        for table_name, table_data in report['tables'].items():
            if 'columns' in table_data:
                for col_name, col_data in table_data['columns'].items():
                    if col_data.get('raw_data_sources'):
                        null_pct = col_data.get('null_percentage', 0)
                        fillable_list.append({
                            'table': table_name,
                            'column': col_name,
                            'null_percentage': null_pct,
                            'sources': len(col_data['raw_data_sources'])
                        })
        
        fillable_list.sort(key=lambda x: x['null_percentage'], reverse=True)
        for item in fillable_list[:20]:  # Top 20
            logger.info(f"  {item['table']}.{item['column']}: {item['null_percentage']}% NULL "
                       f"({item['sources']} source(s))")
    
    finally:
        conn.close()


if __name__ == '__main__':
    main()

