/**
 * QueryService: Execute SQL files and transform results
 * 
 * Reads SQL files from sql/queries/ directory and executes them using Prisma.
 * Handles filter injection and type-safe result transformation.
 */

import { PrismaClient } from '@prisma/client';
import { readFileSync } from 'fs';
import { join } from 'path';
import { FilterBuilder } from '../utils/FilterBuilder';
import { FilterParams } from '@shared/types';

export class QueryService {
  constructor(private prisma: PrismaClient) {}

  /**
   * Read SQL file from sql/queries/ directory
   * 
   * Path resolution:
   * - In Docker: working dir is /app/app/api, so sql/queries is at ../../sql/queries
   * - Locally: working dir is app/api, so sql/queries is at ../../sql/queries
   */
  private readSqlFile(filePath: string): string {
    // From app/api, go up 2 levels to project root, then into sql/queries
    const fullPath = join(process.cwd(), '..', '..', 'sql', 'queries', filePath);
    return readFileSync(fullPath, 'utf-8');
  }

  /**
   * Inject filters into SQL query at the injection point
   */
  private injectFilters(sql: string, filters?: FilterParams): { sql: string; parameters: unknown[] } {
    if (!filters) {
      return { sql, parameters: [] };
    }

    const injectionMarker = '-- Filters are injected here dynamically';
    const { clause, parameters } = FilterBuilder.buildFromParams(filters);

    if (sql.includes(injectionMarker)) {
      const injectedSql = sql.replace(injectionMarker, `${injectionMarker}\n    ${clause}`);
      return { sql: injectedSql, parameters };
    }

    // If no injection point, append filters to WHERE clause
    // This is a fallback for queries without explicit injection points
    if (clause) {
      // Find the last WHERE clause and append
      const whereIndex = sql.lastIndexOf('WHERE');
      if (whereIndex !== -1) {
        const beforeWhere = sql.substring(0, whereIndex + 5);
        const afterWhere = sql.substring(whereIndex + 5);
        const injectedSql = `${beforeWhere}\n    ${clause.substring(4)} ${afterWhere}`;
        return { sql: injectedSql, parameters };
      }
    }

    return { sql, parameters };
  }

  /**
   * Execute SQL query with optional filters
   */
  async executeQuery<T>(
    sqlFilePath: string,
    filters?: FilterParams
  ): Promise<T[]> {
    let sql = this.readSqlFile(sqlFilePath);
    const { sql: finalSql, parameters } = this.injectFilters(sql, filters);

    // Execute using Prisma $queryRaw with parameterized query
    const result = await this.prisma.$queryRawUnsafe(finalSql, ...parameters);
    
    // Transform results to handle Date and Decimal types
    return this.transformResult<T>(result as unknown[]);
  }

  /**
   * Execute SQL query with custom parameters
   */
  async executeQueryWithParams<T>(
    sqlFilePath: string,
    params: Record<string, unknown>
  ): Promise<T[]> {
    let sql = this.readSqlFile(sqlFilePath);
    
    // Replace parameter placeholders (e.g., :periodType) with $1, $2, etc.
    const paramNames = Object.keys(params);
    const paramValues: unknown[] = [];
    let paramIndex = 1;

    paramNames.forEach((paramName) => {
      const placeholder = `:${paramName}`;
      if (sql.includes(placeholder)) {
        sql = sql.replace(new RegExp(`:${paramName}`, 'g'), `$${paramIndex}`);
        paramValues.push(params[paramName]);
        paramIndex++;
      }
    });

    const result = await this.prisma.$queryRawUnsafe(sql, ...paramValues);
    
    // Transform results to handle Date and Decimal types
    return this.transformResult<T>(result as unknown[]);
  }

  /**
   * Transform database result to match TypeScript interface
   * Handles date conversion and null values
   */
  transformResult<T>(result: unknown[]): T[] {
    return result.map((row) => {
      const transformed: Record<string, unknown> = {};
      for (const [key, value] of Object.entries(row as Record<string, unknown>)) {
        // Convert Date objects to ISO strings for JSON serialization
        if (value instanceof Date) {
          transformed[key] = value.toISOString();
        } else if (value !== null && typeof value === 'object' && 'toNumber' in value) {
          // Handle Prisma Decimal type
          transformed[key] = Number(value);
        } else if (typeof value === 'bigint') {
          // Handle BigInt (PostgreSQL bigint type)
          transformed[key] = Number(value);
        } else {
          transformed[key] = value;
        }
      }
      return transformed as T;
    });
  }
}

