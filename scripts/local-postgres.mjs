import EmbeddedPostgres from 'embedded-postgres';
import { existsSync, mkdirSync } from 'node:fs';
import path from 'node:path';

const directory = path.resolve('.runtime/postgres-data');
mkdirSync(path.dirname(directory), { recursive: true });
const postgres = new EmbeddedPostgres({
  databaseDir: directory,
  user: 'report',
  password: 'local-report-password',
  port: 55432,
  authMethod: 'scram-sha-256',
  persistent: true,
  createPostgresUser: false,
  postgresFlags: [
    '-h',
    '127.0.0.1',
    '-c',
    'log_statement=none',
    '-c',
    'log_min_error_statement=panic',
  ],
  onLog: () => {},
  onError: () => {},
});

if (!existsSync(path.join(directory, 'PG_VERSION')))
  await postgres.initialise();
await postgres.start();
const client = postgres.getPgClient('postgres', '127.0.0.1');
await client.connect();
for (const database of ['report_dev', 'report_test']) {
  const found = await client.query(
    'SELECT 1 FROM pg_database WHERE datname = $1',
    [database],
  );
  if (!found.rowCount) await postgres.createDatabase(database);
}
await client.end();
process.stdout.write('Local PostgreSQL ready on 127.0.0.1:55432.\n');
await new Promise((resolve) => {
  for (const signal of ['SIGINT', 'SIGTERM']) process.once(signal, resolve);
});
await postgres.stop();
