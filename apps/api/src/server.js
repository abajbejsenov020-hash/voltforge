import { createServer } from 'node:http';
import { pathToFileURL } from 'node:url';
import { CATALOG, CATEGORIES } from '@voltforge/shared/catalog';
import { findVehicles, VEHICLE_INDEX } from '@voltforge/shared/vehicles';
import { estimatePerformance } from '@voltforge/shared/performance';
import { createApp } from './app.js';
import { readConfig } from './config.js';

export function startServer(config = readConfig()) {
  const app = createApp({
    ...config,
    catalog: CATALOG,
    categories: CATEGORIES,
    findVehicles,
    vehicleIndex: VEHICLE_INDEX,
    estimatePerformance,
  });
  const server = createServer(app.handler);
  server.requestTimeout = 30_000;
  server.headersTimeout = 15_000;
  server.keepAliveTimeout = 5_000;
  server.once('close', () => app.close());
  server.once('error', () => app.close());
  server.listen(config.port, config.host, () => {
    console.log(`Voltforge API listening on http://${config.host}:${server.address().port}`);
  });
  return server;
}

export function run() {
  const server = startServer();
  let stopping = false;
  const stop = () => {
    if (stopping) return;
    stopping = true;
    server.close((error) => {
      if (error) {
        console.error(error);
        process.exitCode = 1;
      }
    });
  };
  process.once('SIGINT', stop);
  process.once('SIGTERM', stop);
  server.on('error', (error) => {
    console.error(`API startup failed: ${error.message}`);
    process.exitCode = 1;
  });
  return server;
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  run();
}
