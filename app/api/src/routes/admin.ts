/**
 * Admin API Routes
 * 
 * Endpoints for administrative tasks:
 * - ETL script execution
 * - Script listing
 */

import { Router, Request, Response } from 'express';
import { z } from 'zod';
import { ETLService } from '../services/ETLService';
import { ETLExecutionResult } from '../../../shared/types';

const router = Router();

const scriptPathSchema = z.string().regex(/^[a-z_/]+\.py$/);

export function createAdminRouter(etlService: ETLService): Router {
  /**
   * GET /api/v1/admin/scripts
   * List available ETL scripts
   */
  router.get('/scripts', async (req: Request, res: Response<{ scripts: string[]; error?: string }>) => {
    try {
      const scripts = await etlService.listScripts();
      res.json({ scripts });
    } catch (error) {
      res.status(500).json({
        scripts: [],
        error: error instanceof Error ? error.message : 'Unknown error',
      });
    }
  });

  /**
   * POST /api/v1/admin/scripts/execute
   * Execute an ETL script
   * 
   * Request body: { scriptPath: string }
   */
  router.post('/scripts/execute', async (req: Request, res: Response<ETLExecutionResult>) => {
    try {
      const { scriptPath } = z.object({
        scriptPath: scriptPathSchema,
      }).parse(req.body);

      const result = await etlService.executeScript(scriptPath);
      res.json(result);
    } catch (error) {
      if (error instanceof z.ZodError) {
        res.status(400).json({
          success: false,
          exitCode: 1,
          logs: [],
          error: `Validation error: ${error.errors.map((e) => e.message).join(', ')}`,
        });
        return;
      }
      res.status(500).json({
        success: false,
        exitCode: 1,
        logs: [],
        error: error instanceof Error ? error.message : 'Unknown error',
      });
    }
  });

  return router;
}

