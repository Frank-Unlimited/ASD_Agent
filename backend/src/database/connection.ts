import sqlite3 from 'sqlite3';
import { open, Database } from 'sqlite';
import path from 'path';
import fs from 'fs';

// Ensure data directory exists
const dataDir = path.join(process.cwd(), 'data');
if (!fs.existsSync(dataDir)) {
  fs.mkdirSync(dataDir, { recursive: true });
}

// Database connection
let db: Database<sqlite3.Database, sqlite3.Statement> | null = null;

/**
 * Connect to the SQLite database
 */
export async function connectDB(): Promise<Database<sqlite3.Database, sqlite3.Statement>> {
  if (db) {
    return db;
  }

  db = await open({
    filename: path.join(dataDir, 'intervention.db'),
    driver: sqlite3.Database
  });

  // Enable foreign key constraints
  await db.run('PRAGMA foreign_keys = ON');

  // Enable WAL mode for better performance
  await db.run('PRAGMA journal_mode = WAL');

  // Optimize performance
  await db.run('PRAGMA synchronous = NORMAL');
  await db.run('PRAGMA cache_size = -2000'); // 2000KB cache

  console.log('Connected to SQLite database');
  return db;
}

/**
 * Get the database connection (singleton)
 */
export async function getDB(): Promise<Database<sqlite3.Database, sqlite3.Statement>> {
  if (!db) {
    return await connectDB();
  }
  return db;
}

/**
 * Close the database connection
 */
export async function closeDB(): Promise<void> {
  if (db) {
    await db.close();
    db = null;
    console.log('Disconnected from SQLite database');
  }
}
