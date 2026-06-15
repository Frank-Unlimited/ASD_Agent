/**
 * 综合评估 Schema 定义
 * 基于专业孤独症评估报告格式
 */

export interface ComprehensiveAssessmentReport {
  // 基本信息
  reportId: string;
  childName: string;
  assessmentDate: string;
  reportingPeriod: string; // 例如："2024年1月-3月"
  
  // 1. 发育史摘要
  developmentalHistory: {
    earlyMilestones: string; // 早期里程碑
    languageDevelopment: string; // 语言发展
    socialDevelopment: string; // 社交发展
    motorDevelopment: string; // 运动发展
  };
  
  // 2. 当前功能水平评估
  currentFunctioning: {
    socialCommunication: {
      score: number; // 0-100
      description: string;
      strengths: string[];
      challenges: string[];
    };
    restrictedBehaviors: {
      score: number;
      description: string;
      patterns: string[];
    };
    sensoryProfile: {
      description: string;
      sensitivities: string[];
    };
    cognitiveAbilities: {
      score: number;
      description: string;
    };
  };
  
  // 3. 家庭干预记录
  homeInterventionSummary: {
    totalSessions: number; // 总游戏次数
    totalDuration: string; // 总时长
    interventionFrequency: string; // 干预频率
    
    // 游戏活动分析
    gameActivities: {
      mostEngaging: string[]; // 最吸引孩子的游戏
      leastEngaging: string[]; // 不太感兴趣的游戏
      emergingSkills: string[]; // 新出现的技能
    };
    
    // 行为观察
    behaviorObservations: {
      positiveChanges: string[]; // 积极变化
      persistentChallenges: string[]; // 持续挑战
      parentConcerns: string[]; // 家长关注点
    };
  };
  
  // 4. 兴趣档案分析
  interestProfile: {
    dominantInterests: Array<{
      dimension: string;
      intensity: number;
      examples: string[];
    }>;
    emergingInterests: string[];
    restrictedPatterns: string[];
    recommendations: string[];
  };
  
  // 5. 能力发展轨迹
  developmentalTrajectory: {
    socialEngagement: {
      baseline: number;
      current: number;
      trend: 'improving' | 'stable' | 'declining';
      notes: string;
    };
    communication: {
      baseline: number;
      current: number;
      trend: 'improving' | 'stable' | 'declining';
      notes: string;
    };
    playSkills: {
      baseline: number;
      current: number;
      trend: 'improving' | 'stable' | 'declining';
      notes: string;
    };
    emotionalRegulation: {
      baseline: number;
      current: number;
      trend: 'improving' | 'stable' | 'declining';
      notes: string;
    };
  };
  
  // 6. 临床建议
  clinicalRecommendations: {
    continuedStrengths: string[]; // 继续发挥的优势
    targetAreas: string[]; // 需要重点关注的领域
    suggestedInterventions: string[]; // 建议的干预方向
    parentGuidance: string[]; // 给家长的指导
    followUpPlan: string; // 随访计划
  };
  
  // 7. 附加信息
  additionalNotes: string;
  
  // 元数据
  generatedBy: string; // "AI辅助生成"
  reviewedBy?: string; // 可选：医生审核
}


/**
 * 综合评估报告 JSON Schema（用于 ReAct 模式）
 * 这个 schema 会被嵌入到系统提示词中，指导 LLM 生成正确格式的报告
 */
export const COMPREHENSIVE_ASSESSMENT_REPORT_SCHEMA = {
  type: 'object',
  required: [
    'developmentalHistory',
    'currentFunctioning',
    'homeInterventionSummary',
    'interestProfile',
    'developmentalTrajectory',
    'clinicalRecommendations',
    'additionalNotes'
  ],
  properties: {
    developmentalHistory: {
      type: 'object',
      required: ['earlyMilestones', 'languageDevelopment', 'socialDevelopment', 'motorDevelopment'],
      properties: {
        earlyMilestones: { type: 'string', description: '早期里程碑（爬行、走路、说话等），100-200字' },
        languageDevelopment: { type: 'string', description: '语言发展轨迹，100-200字' },
        socialDevelopment: { type: 'string', description: '社交互动模式，100-200字' },
        motorDevelopment: { type: 'string', description: '运动能力发展，100-200字' }
      }
    },
    currentFunctioning: {
      type: 'object',
      required: ['socialCommunication', 'restrictedBehaviors', 'sensoryProfile', 'cognitiveAbilities'],
      properties: {
        socialCommunication: {
          type: 'object',
          required: ['score', 'description', 'strengths', 'challenges'],
          properties: {
            score: { type: 'number', minimum: 0, maximum: 100, description: '社交沟通评分' },
            description: { type: 'string', description: '详细描述，150-200字' },
            strengths: { type: 'array', items: { type: 'string' }, minItems: 2, maxItems: 5, description: '优势列表' },
            challenges: { type: 'array', items: { type: 'string' }, minItems: 2, maxItems: 5, description: '挑战列表' }
          }
        },
        restrictedBehaviors: {
          type: 'object',
          required: ['score', 'description', 'patterns'],
          properties: {
            score: { type: 'number', minimum: 0, maximum: 100, description: '限制性行为评分' },
            description: { type: 'string', description: '详细描述，150-200字' },
            patterns: { type: 'array', items: { type: 'string' }, minItems: 2, maxItems: 5, description: '观察到的模式' }
          }
        },
        sensoryProfile: {
          type: 'object',
          required: ['description', 'sensitivities'],
          properties: {
            description: { type: 'string', description: '感觉处理描述，150-200字' },
            sensitivities: { type: 'array', items: { type: 'string' }, minItems: 2, maxItems: 6, description: '感觉敏感性列表' }
          }
        },
        cognitiveAbilities: {
          type: 'object',
          required: ['score', 'description'],
          properties: {
            score: { type: 'number', minimum: 0, maximum: 100, description: '认知能力评分' },
            description: { type: 'string', description: '详细描述，150-200字' }
          }
        }
      }
    },
    homeInterventionSummary: {
      type: 'object',
      required: ['totalSessions', 'totalDuration', 'interventionFrequency', 'gameActivities', 'behaviorObservations'],
      properties: {
        totalSessions: { type: 'number', description: '总游戏次数' },
        totalDuration: { type: 'string', description: '总时长，如"50小时"' },
        interventionFrequency: { type: 'string', description: '干预频率，如"每周3-4次"' },
        gameActivities: {
          type: 'object',
          required: ['mostEngaging', 'leastEngaging', 'emergingSkills'],
          properties: {
            mostEngaging: { type: 'array', items: { type: 'string' }, minItems: 2, maxItems: 5 },
            leastEngaging: { type: 'array', items: { type: 'string' }, minItems: 1, maxItems: 3 },
            emergingSkills: { type: 'array', items: { type: 'string' }, minItems: 2, maxItems: 5 }
          }
        },
        behaviorObservations: {
          type: 'object',
          required: ['positiveChanges', 'persistentChallenges', 'parentConcerns'],
          properties: {
            positiveChanges: { type: 'array', items: { type: 'string' }, minItems: 2, maxItems: 5 },
            persistentChallenges: { type: 'array', items: { type: 'string' }, minItems: 1, maxItems: 5 },
            parentConcerns: { type: 'array', items: { type: 'string' }, minItems: 1, maxItems: 5 }
          }
        }
      }
    },
    interestProfile: {
      type: 'object',
      required: ['dominantInterests', 'emergingInterests', 'restrictedPatterns', 'recommendations'],
      properties: {
        dominantInterests: {
          type: 'array',
          minItems: 2,
          maxItems: 5,
          items: {
            type: 'object',
            required: ['dimension', 'intensity', 'examples'],
            properties: {
              dimension: { type: 'string', description: '兴趣维度名称' },
              intensity: { type: 'number', minimum: 0, maximum: 1, description: '强度 0-1' },
              examples: { type: 'array', items: { type: 'string' }, minItems: 2, maxItems: 4 }
            }
          }
        },
        emergingInterests: { type: 'array', items: { type: 'string' }, minItems: 1, maxItems: 3 },
        restrictedPatterns: { type: 'array', items: { type: 'string' }, minItems: 0, maxItems: 3 },
        recommendations: { type: 'array', items: { type: 'string' }, minItems: 2, maxItems: 5 }
      }
    },
    developmentalTrajectory: {
      type: 'object',
      required: ['socialEngagement', 'communication', 'playSkills', 'emotionalRegulation'],
      properties: {
        socialEngagement: {
          type: 'object',
          required: ['baseline', 'current', 'trend', 'notes'],
          properties: {
            baseline: { type: 'number', minimum: 0, maximum: 100 },
            current: { type: 'number', minimum: 0, maximum: 100 },
            trend: { type: 'string', enum: ['improving', 'stable', 'declining'] },
            notes: { type: 'string', description: '50-100字' }
          }
        },
        communication: {
          type: 'object',
          required: ['baseline', 'current', 'trend', 'notes'],
          properties: {
            baseline: { type: 'number', minimum: 0, maximum: 100 },
            current: { type: 'number', minimum: 0, maximum: 100 },
            trend: { type: 'string', enum: ['improving', 'stable', 'declining'] },
            notes: { type: 'string', description: '50-100字' }
          }
        },
        playSkills: {
          type: 'object',
          required: ['baseline', 'current', 'trend', 'notes'],
          properties: {
            baseline: { type: 'number', minimum: 0, maximum: 100 },
            current: { type: 'number', minimum: 0, maximum: 100 },
            trend: { type: 'string', enum: ['improving', 'stable', 'declining'] },
            notes: { type: 'string', description: '50-100字' }
          }
        },
        emotionalRegulation: {
          type: 'object',
          required: ['baseline', 'current', 'trend', 'notes'],
          properties: {
            baseline: { type: 'number', minimum: 0, maximum: 100 },
            current: { type: 'number', minimum: 0, maximum: 100 },
            trend: { type: 'string', enum: ['improving', 'stable', 'declining'] },
            notes: { type: 'string', description: '50-100字' }
          }
        }
      }
    },
    clinicalRecommendations: {
      type: 'object',
      required: ['continuedStrengths', 'targetAreas', 'suggestedInterventions', 'parentGuidance', 'followUpPlan'],
      properties: {
        continuedStrengths: { type: 'array', items: { type: 'string' }, minItems: 2, maxItems: 5 },
        targetAreas: { type: 'array', items: { type: 'string' }, minItems: 2, maxItems: 5 },
        suggestedInterventions: { type: 'array', items: { type: 'string' }, minItems: 3, maxItems: 6 },
        parentGuidance: { type: 'array', items: { type: 'string' }, minItems: 3, maxItems: 6 },
        followUpPlan: { type: 'string', description: '随访计划，100-150字' }
      }
    },
    additionalNotes: { type: 'string', description: '附加信息，可选，0-200字' }
  }
};
