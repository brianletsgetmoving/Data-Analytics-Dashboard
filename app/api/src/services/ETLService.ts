/**
 * ETLService: Execute Python scripts from Node.js
 * 
 * Executes Python ETL scripts from scripts/ directory with proper
 * working directory and environment variables.
 */

import { exec } from 'child_process';
import { promisify } from 'util';
import { join } from 'path';
import { ETLExecutionResult } from '@shared/types';

const execAsync = promisify(exec);

export class ETLService {
  private scriptsPath: string;

  constructor() {
    // Path to scripts directory
    // From app/api, go up 2 levels to project root, then into scripts
    this.scriptsPath = join(process.cwd(), '..', '..', 'scripts');
  }

  /**
   * Execute Python script with --execute flag
   */
  async executeScript(scriptPath: string): Promise<ETLExecutionResult> {
    const fullPath = join(this.scriptsPath, scriptPath);
    const command = `python3 ${fullPath} --execute`;

    try {
      const { stdout, stderr } = await execAsync(command, {
        cwd: this.scriptsPath,
        env: {
          ...process.env,
          PYTHONUNBUFFERED: '1', // Ensure Python output is not buffered
        },
        maxBuffer: 10 * 1024 * 1024, // 10MB buffer for large outputs
      });

      const logs = stdout.split('\n').filter((line) => line.trim().length > 0);
      const errorLogs = stderr.split('\n').filter((line) => line.trim().length > 0);

      return {
        success: true,
        exitCode: 0,
        logs: [...logs, ...errorLogs],
      };
    } catch (error: unknown) {
      const execError = error as { code?: number; stdout?: string; stderr?: string };
      const logs: string[] = [];
      
      if (execError.stdout) {
        logs.push(...execError.stdout.split('\n').filter((line) => line.trim().length > 0));
      }
      if (execError.stderr) {
        logs.push(...execError.stderr.split('\n').filter((line) => line.trim().length > 0));
      }

      return {
        success: false,
        exitCode: execError.code ?? 1,
        logs,
        error: execError.stderr || String(error),
      };
    }
  }

  /**
   * List available ETL scripts
   */
  async listScripts(): Promise<string[]> {
    // Return list of available scripts based on directory structure
    return [
      'relationships/complete_quote_linkage.py',
      'relationships/link_badlead_to_leadstatus.py',
      'lookup/populate_lead_sources.py',
      'lookup/populate_branches.py',
      'lookup/merge_sales_person_variations.py',
      'timeline/populate_customer_timeline_fields.py',
      'timeline/link_orphaned_performance_records.py',
    ];
  }
}

