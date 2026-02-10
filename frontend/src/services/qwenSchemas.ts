/**
 * Qwen JSON Schema 定义
 * 用于强制结构化输出
 */

export const GameRecommendationSchema = {
  name: 'game_recommendation',
  description: '游戏推荐结果',
  schema: {
    type: 'object',
    properties: {
      id: {
        type: 'string',
        description: '游戏ID'
      },
      title: {
        type: 'string',
        description: '游戏名称'
      },
      reason: {
        type: 'string',
        description: '推荐理由'
      }
    },
    required: ['id', 'title', 'reason'],
    additionalProperties: false
  }
};

export const SessionEvaluationSchema = {
  name: 'session_evaluation',
  description: '会话评估结果',
  schema: {
    type: 'object',
    properties: {
      feedbackScore: {
        type: 'number',
        description: '反馈得分 (0-100)',
        minimum: 0,
        maximum: 100
      },
      explorationScore: {
        type: 'number',
        description: '探索度得分 (0-100)',
        minimum: 0,
        maximum: 100
      },
      score: {
        type: 'number',
        description: '综合得分 (0-100)',
        minimum: 0,
        maximum: 100
      },
      summary: {
        type: 'string',
        description: '总结'
      },
      suggestion: {
        type: 'string',
        description: '建议'
      }
    },
    required: ['feedbackScore', 'explorationScore', 'score', 'summary', 'suggestion'],
    additionalProperties: false
  }
};

export const BehaviorAnalysisSchema = {
  name: 'behavior_analysis',
  description: '行为分析结果',
  schema: {
    type: 'object',
    properties: {
      behavior: {
        type: 'string',
        description: '行为描述'
      },
      matches: {
        type: 'array',
        description: '匹配的兴趣维度',
        items: {
          type: 'object',
          properties: {
            dimension: {
              type: 'string',
              enum: ['Visual', 'Auditory', 'Tactile', 'Motor', 'Construction', 'Order', 'Cognitive', 'Social'],
              description: '兴趣维度'
            },
            weight: {
              type: 'number',
              description: '权重 (0-1)',
              minimum: 0,
              maximum: 1
            },
            reasoning: {
              type: 'string',
              description: '推理说明'
            }
          },
          required: ['dimension', 'weight', 'reasoning']
        }
      }
    },
    required: ['behavior', 'matches'],
    additionalProperties: false
  }
};

export const BehaviorAnalysisListSchema = {
  name: 'behavior_analysis_list',
  description: '行为分析列表',
  schema: {
    type: 'object',
    properties: {
      analyses: {
        type: 'array',
        items: BehaviorAnalysisSchema.schema
      }
    },
    required: ['analyses'],
    additionalProperties: false
  }
};

export const ProfileUpdateSchema = {
  name: 'profile_update',
  description: '档案更新',
  schema: {
    type: 'object',
    properties: {
      interestUpdates: {
        type: 'array',
        description: '兴趣维度更新',
        items: {
          type: 'object',
          properties: {
            behavior: {
              type: 'string',
              description: '行为描述'
            },
            matches: {
              type: 'array',
              items: {
                type: 'object',
                properties: {
                  dimension: {
                    type: 'string',
                    enum: ['Visual', 'Auditory', 'Tactile', 'Motor', 'Construction', 'Order', 'Cognitive', 'Social']
                  },
                  weight: {
                    type: 'number',
                    minimum: 0,
                    maximum: 1
                  }
                },
                required: ['dimension', 'weight']
              }
            }
          },
          required: ['behavior', 'matches']
        }
      },
      abilityUpdates: {
        type: 'array',
        description: '能力维度更新',
        items: {
          type: 'object',
          properties: {
            dimension: {
              type: 'string',
              enum: ['自我调节', '亲密感', '双向沟通', '复杂沟通', '情绪思考', '逻辑思维']
            },
            scoreChange: {
              type: 'number',
              description: '分数变化'
            },
            reason: {
              type: 'string',
              description: '变化原因'
            }
          },
          required: ['dimension', 'scoreChange', 'reason']
        }
      }
    },
    required: ['interestUpdates', 'abilityUpdates'],
    additionalProperties: false
  }
};

// Function Call 工具定义
export const RecommendGameTool = {
  type: 'function' as const,
  function: {
    name: 'recommend_game',
    description: '根据儿童档案推荐适合的游戏',
    parameters: {
      type: 'object',
      properties: {
        id: {
          type: 'string',
          description: '游戏ID'
        },
        title: {
          type: 'string',
          description: '游戏名称'
        },
        reason: {
          type: 'string',
          description: '推荐理由，需要基于儿童的兴趣点和能力短板'
        }
      },
      required: ['id', 'title', 'reason']
    }
  }
};

export const LogBehaviorTool = {
  type: 'function' as const,
  function: {
    name: 'log_behavior',
    description: '记录儿童的具体行为并关联兴趣维度。当家长描述孩子正在做什么、玩什么、表现出什么行为时，必须立即调用此工具。例如："孩子正在玩积木"、"他一直看着旋转的东西"、"她在排列玩具"等任何行为描述都应该记录。',
    parameters: {
      type: 'object',
      properties: {
        behavior: {
          type: 'string',
          description: '精简的行为描述，例如："正在玩积木"、"盯着旋转物体"、"排列玩具成一排"'
        },
        tags: {
          type: 'array',
          items: {
            type: 'string',
            enum: ['Visual', 'Auditory', 'Tactile', 'Motor', 'Construction', 'Order', 'Cognitive', 'Social']
          },
          description: '相关的兴趣维度标签（可多选）'
        },
        analysis: {
          type: 'string',
          description: '一句话分析其发展意义，例如："显示出对建构活动的兴趣，有助于精细动作发展"'
        }
      },
      required: ['behavior', 'tags', 'analysis']
    }
  }
};

export const CreateWeeklyPlanTool = {
  type: 'function' as const,
  function: {
    name: 'create_weekly_plan',
    description: '生成本周训练计划',
    parameters: {
      type: 'object',
      properties: {
        focus: {
          type: 'string',
          description: '本周核心目标'
        },
        schedule: {
          type: 'array',
          items: {
            type: 'object',
            properties: {
              day: {
                type: 'string',
                description: '星期几'
              },
              task: {
                type: 'string',
                description: '活动名称'
              }
            },
            required: ['day', 'task']
          },
          description: '周计划安排'
        }
      },
      required: ['focus', 'schedule']
    }
  }
};

export const NavigatePageTool = {
  type: 'function' as const,
  function: {
    name: 'navigate_page',
    description: '跳转到其他页面',
    parameters: {
      type: 'object',
      properties: {
        page: {
          type: 'string',
          enum: ['PROFILE', 'CALENDAR', 'GAMES', 'REPORTS'],
          description: '目标页面'
        },
        title: {
          type: 'string',
          description: '跳转标题'
        },
        reason: {
          type: 'string',
          description: '跳转理由'
        }
      },
      required: ['page', 'title', 'reason']
    }
  }
};

// 所有对话工具
export const ChatTools = [
  RecommendGameTool,
  LogBehaviorTool,
  CreateWeeklyPlanTool,
  NavigatePageTool
];
