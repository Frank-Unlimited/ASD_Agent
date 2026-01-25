import fs from 'fs';
import path from 'path';
import { connectDB } from './connection';

/**
 * Initialize the database by creating all tables and seeding initial data
 */
async function initializeDatabase() {
  try {
    console.log('🔄 Initializing database...');

    // Connect to database
    const db = await connectDB();

    // Read and execute schema.sql
    const schemaPath = path.join(__dirname, 'schema.sql');
    const schemaSQL = fs.readFileSync(schemaPath, 'utf8');
    await db.exec(schemaSQL);
    console.log('✅ Database schema created/updated successfully');

    // Seed initial games library data
    const sampleGames = [
      {
        name: 'Eye Contact Bingo',
        description: 'Interactive game to practice sustained eye contact',
        target_level: 1,
        icon: '👀',
        difficulty: 'beginner',
        category: 'attention'
      },
      {
        name: 'Emotion Charades',
        description: 'Act out emotions to build emotional recognition',
        target_level: 4,
        icon: '🎭',
        difficulty: 'intermediate',
        category: 'emotional'
      },
      {
        name: 'Joint Attention Blocks',
        description: 'Collaborative block building to develop shared attention',
        target_level: 2,
        icon: '🧱',
        difficulty: 'beginner',
        category: 'social'
      },
      {
        name: 'Conversation Starters',
        description: 'Practice turn-taking and reciprocal conversation',
        target_level: 3,
        icon: '💬',
        difficulty: 'intermediate',
        category: 'communication'
      },
      {
        name: 'Sensory Scavenger Hunt',
        description: 'Explore sensory experiences in the environment',
        target_level: 1,
        icon: '🔍',
        difficulty: 'beginner',
        category: 'sensory'
      },
      {
        name: 'Emotion Memory Match',
        description: 'Memory game with emotion cards to build recognition',
        target_level: 4,
        icon: '🎴',
        difficulty: 'intermediate',
        category: 'emotional'
      },
      {
        name: 'Collaborative Drawing',
        description: 'Work together to create a drawing',
        target_level: 2,
        icon: '🎨',
        difficulty: 'beginner',
        category: 'social'
      },
      {
        name: 'Problem Solving Puzzles',
        description: 'Solve puzzles to build logical thinking skills',
        target_level: 5,
        icon: '🧩',
        difficulty: 'advanced',
        category: 'cognitive'
      }
    ];

    // Insert sample games
    const insertGameStmt = await db.prepare(`
      INSERT OR IGNORE INTO games_library (name, description, target_level, icon, difficulty, category)
      VALUES (?, ?, ?, ?, ?, ?)
    `);

    for (const game of sampleGames) {
      await insertGameStmt.run([
        game.name,
        game.description,
        game.target_level,
        game.icon,
        game.difficulty,
        game.category
      ]);
    }

    await insertGameStmt.finalize();
    console.log('✅ Sample games data inserted successfully');

    // Insert test user for MVP (no authentication)
    await db.run(`
      INSERT OR IGNORE INTO users (id, username, password, role, name, email, phone)
      VALUES (1, 'test', 'test', 'therapist', 'Test User', 'test@example.com', '13800138000')
    `);
    console.log('✅ Test user created successfully');

    console.log('🎉 Database initialization complete!');
  } catch (error) {
    console.error('❌ Error initializing database:', error);
    process.exit(1);
  }
}

// Run initialization if script is called directly
if (require.main === module) {
  initializeDatabase();
}

export { initializeDatabase };
