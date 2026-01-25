import dotenv from 'dotenv';
import path from 'path';

// Load environment variables from .env file
dotenv.config({
  path: path.resolve(__dirname, '../../.env')
});

export const env = {
  NODE_ENV: process.env.NODE_ENV || 'development',
  PORT: process.env.PORT ? parseInt(process.env.PORT, 10) : 3000,

  // JWT Configuration
  JWT_SECRET: process.env.JWT_SECRET || 'default-secret-key-change-in-production',
  JWT_EXPIRES_IN: process.env.JWT_EXPIRES_IN || '24h',

  // Authentication Configuration
  VERIFICATION_CODE_EXPIRE_MINUTES: process.env.VERIFICATION_CODE_EXPIRE_MINUTES ? parseInt(process.env.VERIFICATION_CODE_EXPIRE_MINUTES, 10) : 15,

  // Mock Verification Code (for MVP)
  MOCK_VERIFICATION_CODE: process.env.MOCK_VERIFICATION_CODE || '123456',

  // Database Configuration (for future use)
  DB_HOST: process.env.DB_HOST || 'localhost',
  DB_PORT: process.env.DB_PORT ? parseInt(process.env.DB_PORT, 10) : 5432,
  DB_NAME: process.env.DB_NAME || 'asd_intervention',
  DB_USER: process.env.DB_USER || 'postgres',
  DB_PASSWORD: process.env.DB_PASSWORD || 'password',

  // AI Configuration
  DEEPSEEK_API_KEY: process.env.DEEPSEEK_API_KEY || '',
  DEEPSEEK_BASE_URL: process.env.DEEPSEEK_BASE_URL || 'https://api.deepseek.com',
  OPENAI_API_KEY: process.env.OPENAI_API_KEY || '',
  AI_PROVIDER: process.env.AI_PROVIDER || 'deepseek' // 'deepseek' or 'openai'
};
