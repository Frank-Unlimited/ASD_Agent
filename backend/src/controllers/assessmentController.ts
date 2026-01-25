import { connectDB } from '../database/connection';
import { aiService } from '../services/ai';

class AssessmentController {
  /**
   * Import assessment report and create child profile
   * @param {any} req - Express request object
   * @param {any} res - Express response object
   */
  async importAssessment(req: any, res: any) {
    try {
      const { assessmentData, childInfo } = req.body;
      // 使用固定的测试用户ID（MVP阶段不需要认证）
      const userId = 1;

      // Validate input
      if (!assessmentData) {
        return res.status(400).json({
          success: false,
          message: 'Assessment data is required'
        });
      }

      if (!childInfo || !childInfo.name) {
        return res.status(400).json({
          success: false,
          message: 'Child information with name is required'
        });
      }

      // Analyze assessment using AI (DeepSeek or OpenAI)
      let analysisResult;
      try {
        console.log('📋 Starting assessment import for child:', childInfo.name);
        console.log('  Assessment data length:', JSON.stringify(assessmentData).length, 'characters');
        
        analysisResult = await aiService.analyzeAssessment(assessmentData);
        
        console.log('✅ AI analysis completed successfully');
        console.log('  Profile keys:', Object.keys(analysisResult.profile || {}));
      } catch (aiError: any) {
        // If AI fails, use a default analysis structure
        console.error('❌ AI analysis failed, using default structure');
        console.error('  Error:', aiError.message);
        console.error('  Stack:', aiError.stack);
        
        analysisResult = {
          profile: {
            interests: ['待观察'],
            strengths: ['待评估'],
            challenges: ['待评估']
          },
          analysis: '自动分析暂不可用，请根据评估报告手动填写。AI错误: ' + aiError.message
        };
      }

      // Create child profile in database
      const db = await connectDB();

      const result = await db.run(
        `INSERT INTO child_profiles (
          user_id,
          name,
          birth_date,
          gender,
          diagnosis,
          current_emotional_level,
          notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?)`,
        [
          userId,
          childInfo.name,
          childInfo.birthDate || null,
          childInfo.gender || null,
          childInfo.diagnosis || null,
          0, // Default emotional level
          childInfo.notes || null
        ]
      );

      const childId = result.lastID;

      // Create profile snapshot with assessment analysis
      await db.run(
        `INSERT INTO child_profile_snapshots (
          child_id,
          user_id,
          snapshot_date,
          emotional_level,
          custom_metrics,
          notes
        ) VALUES (?, ?, ?, ?, ?, ?)`,
        [
          childId,
          userId,
          new Date().toISOString(),
          0,
          JSON.stringify(analysisResult.profile),
          analysisResult.analysis
        ]
      );

      // Fetch the created child profile
      const childProfile = await db.get(
        `SELECT * FROM child_profiles WHERE id = ?`,
        [childId]
      );

      res.json({
        success: true,
        message: 'Assessment imported successfully',
        data: {
          childProfile,
          assessmentAnalysis: analysisResult
        }
      });
    } catch (error: any) {
      console.error('Error importing assessment:', error);
      res.status(500).json({
        success: false,
        message: error.message || 'Failed to import assessment'
      });
    }
  }

  /**
   * Get list of user's children
   * @param {any} req - Express request object
   * @param {any} res - Express response object
   */
  async getChildren(req: any, res: any) {
    try {
      // 使用固定的测试用户ID（MVP阶段不需要认证）
      const userId = 1;

      const db = await connectDB();
      const children = await db.all(
        `SELECT * FROM child_profiles WHERE user_id = ? ORDER BY created_at DESC`,
        [userId]
      );

      res.json({
        success: true,
        data: {
          children
        }
      });
    } catch (error: any) {
      console.error('Error getting children:', error);
      res.status(500).json({
        success: false,
        message: error.message || 'Failed to get children'
      });
    }
  }

  /**
   * Get child profile with assessment history
   * @param {any} req - Express request object
   * @param {any} res - Express response object
   */
  async getChildProfile(req: any, res: any) {
    try {
      // 使用固定的测试用户ID（MVP阶段不需要认证）
      const userId = 1;
      const { child_id } = req.params;

      const db = await connectDB();

      // Check if child belongs to user
      const childProfile = await db.get(
        `SELECT * FROM child_profiles WHERE id = ? AND user_id = ?`,
        [child_id, userId]
      );

      if (!childProfile) {
        return res.status(404).json({
          success: false,
          message: 'Child profile not found'
        });
      }

      // Get assessment snapshots
      const assessmentSnapshots = await db.all(
        `SELECT * FROM child_profile_snapshots
         WHERE child_id = ? AND user_id = ?
         ORDER BY snapshot_date DESC`,
        [child_id, userId]
      );

      res.json({
        success: true,
        data: {
          childProfile,
          assessmentSnapshots
        }
      });
    } catch (error: any) {
      console.error('Error getting child profile:', error);
      res.status(500).json({
        success: false,
        message: error.message || 'Failed to get child profile'
      });
    }
  }
}

export const assessmentController = new AssessmentController();
export { AssessmentController };
