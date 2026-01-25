import { Router, Request, Response } from 'express';
import { generateToken, authenticateToken } from '../middleware/auth';
import { env } from '../config/env';

const router = Router();

// In-memory storage for verification codes (for MVP)
const verificationCodes = new Map<string, { code: string; expiresAt: Date }>();

// In-memory storage for users (for MVP)
const users = new Map<string, { id: string; phoneNumber: string; createdAt: Date }>();

// Generate random user ID
const generateUserId = (): string => {
  return `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
};

/**
 * Send verification code to phone number
 * POST /api/auth/send-code
 */
router.post('/send-code', (req: Request, res: Response) => {
  const { phoneNumber } = req.body;

  // Validate phone number (simple validation for MVP)
  if (!phoneNumber || typeof phoneNumber !== 'string') {
    return res.status(400).json({
      success: false,
      message: 'Phone number is required'
    });
  }

  // Clean phone number
  const cleanPhoneNumber = phoneNumber.replace(/[^0-9]/g, '');

  // Validate phone number format (should be 10+ digits)
  if (cleanPhoneNumber.length < 10) {
    return res.status(400).json({
      success: false,
      message: 'Invalid phone number format'
    });
  }

  // In MVP, use mock verification code
  const verificationCode = env.MOCK_VERIFICATION_CODE;
  const expiresAt = new Date(Date.now() + (env.VERIFICATION_CODE_EXPIRE_MINUTES * 60 * 1000));

  // Store verification code
  verificationCodes.set(cleanPhoneNumber, {
    code: verificationCode,
    expiresAt
  });

  console.log(`Verification code for ${cleanPhoneNumber}: ${verificationCode}`);

  res.json({
    success: true,
    message: 'Verification code sent successfully',
    phoneNumber: cleanPhoneNumber,
    expiresInMinutes: env.VERIFICATION_CODE_EXPIRE_MINUTES
  });
});

/**
 * Verify code and login/register user
 * POST /api/auth/verify-login
 */
router.post('/verify-login', (req: Request, res: Response) => {
  const { phoneNumber, code } = req.body;

  // Validate input
  if (!phoneNumber || !code) {
    return res.status(400).json({
      success: false,
      message: 'Phone number and code are required'
    });
  }

  // Clean phone number
  const cleanPhoneNumber = phoneNumber.replace(/[^0-9]/g, '');

  // Check if code exists
  const storedCodeData = verificationCodes.get(cleanPhoneNumber);
  if (!storedCodeData) {
    return res.status(400).json({
      success: false,
      message: 'Verification code not found. Please request a new code.'
    });
  }

  // Check if code is expired
  if (Date.now() > storedCodeData.expiresAt.getTime()) {
    verificationCodes.delete(cleanPhoneNumber);
    return res.status(400).json({
      success: false,
      message: 'Verification code expired. Please request a new code.'
    });
  }

  // Check if code matches
  if (storedCodeData.code !== code) {
    return res.status(400).json({
      success: false,
      message: 'Invalid verification code'
    });
  }

  // Find or create user
  let user = users.get(cleanPhoneNumber);
  if (!user) {
    user = {
      id: generateUserId(),
      phoneNumber: cleanPhoneNumber,
      createdAt: new Date()
    };
    users.set(cleanPhoneNumber, user);
  }

  // Clear verification code
  verificationCodes.delete(cleanPhoneNumber);

  // Generate JWT token
  const token = generateToken(user.id, user.phoneNumber);

  res.json({
    success: true,
    message: 'Login successful',
    data: {
      user: {
        id: user.id,
        phoneNumber: user.phoneNumber,
        createdAt: user.createdAt
      },
      token
    }
  });
});

/**
 * Get current user information
 * GET /api/auth/me
 */
router.get('/me', authenticateToken, (req: any, res: Response) => {
  const { userId, phoneNumber } = req.user;

  // Find user in storage
  const user = users.get(phoneNumber);
  if (!user) {
    return res.status(404).json({
      success: false,
      message: 'User not found'
    });
  }

  res.json({
    success: true,
    data: {
      user: {
        id: user.id,
        phoneNumber: user.phoneNumber,
        createdAt: user.createdAt
      }
    }
  });
});

export default router;
