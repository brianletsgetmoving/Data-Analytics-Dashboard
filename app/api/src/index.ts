/**
 * Express API Server
 * 
 * Main entry point for the Data Analytics API
 */

import express, { Request, Response, NextFunction } from 'express';
import cors from 'cors';
import { PrismaClient } from '@prisma/client';
import { QueryService } from './services/QueryService';
import { ETLService } from './services/ETLService';
import { createAnalyticsRouter } from './routes/analytics';
import { createAdminRouter } from './routes/admin';

const app = express();
const PORT = process.env.PORT || 3001;

// Initialize Prisma client
const prisma = new PrismaClient({
  log: process.env.NODE_ENV === 'development' ? ['query', 'error', 'warn'] : ['error'],
});

// Initialize services
const queryService = new QueryService(prisma);
const etlService = new ETLService();

// Middleware
app.use(cors({
  origin: process.env.FRONTEND_URL || 'http://localhost:5173',
  credentials: true,
}));

app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Health check endpoint
app.get('/health', (req: Request, res: Response) => {
  res.json({
    status: 'ok',
    timestamp: new Date().toISOString(),
    service: 'data-analytics-api',
  });
});

// API routes
app.use('/api/v1/analytics', createAnalyticsRouter(queryService));
app.use('/api/v1/admin', createAdminRouter(etlService));

// Error handling middleware
app.use((err: Error, req: Request, res: Response, next: NextFunction) => {
  console.error('Error:', err);
  res.status(500).json({
    error: err.message || 'Internal server error',
    timestamp: new Date().toISOString(),
  });
});

// 404 handler
app.use((req: Request, res: Response) => {
  res.status(404).json({
    error: 'Not found',
    path: req.path,
    timestamp: new Date().toISOString(),
  });
});

// Graceful shutdown
process.on('SIGTERM', async () => {
  console.log('SIGTERM received, shutting down gracefully...');
  await prisma.$disconnect();
  process.exit(0);
});

process.on('SIGINT', async () => {
  console.log('SIGINT received, shutting down gracefully...');
  await prisma.$disconnect();
  process.exit(0);
});

// Start server
app.listen(PORT, () => {
  console.log(`🚀 Server running on port ${PORT}`);
  console.log(`📊 Health check: http://localhost:${PORT}/health`);
  console.log(`🔍 Analytics API: http://localhost:${PORT}/api/v1/analytics`);
  console.log(`⚙️  Admin API: http://localhost:${PORT}/api/v1/admin`);
});

export default app;

