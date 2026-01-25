import { Request, Response, NextFunction } from 'express';
import jwt from 'jsonwebtoken';
import { env } from '../config/env';

// Interface for JWT payload
interface JwtPayload {
  userId: string;
  phoneNumber: string;
}

// Interface for authenticated user request
interface AuthenticatedRequest extends Request {
  user?: JwtPayload;
}

// Generate JWT token
export const generateToken = (userId: string, phoneNumber: string): string => {
  return jwt.sign(
    { userId, phoneNumber },
    env.JWT_SECRET as any,
    { expiresIn: env.JWT_EXPIRES_IN as any }
  );
};

// JWT authentication middleware
export const authenticateToken = (
  req: AuthenticatedRequest,
  res: Response,
  next: NextFunction
): void => {
  // Get token from Authorization header
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1]; // Bearer <token>

  if (!token) {
    res.status(401).json({
      success: false,
      message: 'Access token required'
    });
    return;
  }

  try {
    // Verify token
    const decoded = jwt.verify(token, env.JWT_SECRET as jwt.Secret) as JwtPayload;
    req.user = decoded;
    next();
  } catch (error: any) {
    console.error('Token verification error:', error.message);
    if (error.name === 'TokenExpiredError') {
      res.status(401).json({
        success: false,
        message: 'Token expired'
      });
    } else {
      res.status(403).json({
        success: false,
        message: 'Invalid token',
        error: error.message
      });
    }
  }
};

// Extract user from token (for optional authentication)
export const extractUserFromToken = (
  req: AuthenticatedRequest,
  res: Response,
  next: NextFunction
): void => {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1];

  if (token) {
    try {
      const decoded = jwt.verify(token, env.JWT_SECRET) as JwtPayload;
      req.user = decoded;
    } catch (error) {
      // Token is invalid or expired, continue without user
    }
  }

  next();
};
