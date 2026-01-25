import { Router, Request, Response } from 'express';
import { assessmentController } from '../controllers/assessmentController';

const router = Router();

/**
 * Import assessment report
 * POST /api/assessments/import
 */
router.post('/import', async (req: Request, res: Response) => {
  await assessmentController.importAssessment(req, res);
});

/**
 * List user's children
 * GET /api/assessments/children
 */
router.get('/children', async (req: Request, res: Response) => {
  await assessmentController.getChildren(req, res);
});

/**
 * Get child profile
 * GET /api/assessments/children/:child_id
 */
router.get('/children/:child_id', async (req: Request, res: Response) => {
  await assessmentController.getChildProfile(req, res);
});

export default router;
