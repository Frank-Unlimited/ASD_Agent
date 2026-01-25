import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import path from 'path';
import authRoutes from './routes/auth';
import assessmentRoutes from './routes/assessments';

// Load environment variables
dotenv.config();

const app = express();
const PORT = process.env.PORT || 5000;

// Middleware
app.use(cors());
app.use(express.json());

// Serve static files from public directory
app.use(express.static(path.join(__dirname, '../public')));

// Test route
app.get('/api/health', (req, res) => {
  res.json({ status: 'OK', message: 'ASD Intervention System Backend is running' });
});

// Authentication routes
app.use('/api/auth', authRoutes);

// Assessment routes
app.use('/api/assessments', assessmentRoutes);

// Start server
app.listen(PORT, () => {
  console.log(`🚀 Server is running on port ${PORT}`);
  console.log(`📝 Test interface: http://localhost:${PORT}`);
});
