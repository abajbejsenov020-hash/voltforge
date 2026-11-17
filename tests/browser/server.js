import { startServer } from '../../apps/api/src/server.js';
import { readConfig } from '../../apps/api/src/config.js';

startServer({ ...readConfig(), port: 4173, databasePath: ':memory:' });
