/**
 * Qwen JSON Schema 定义
 * 用于强制结构化输出
 */

import type { ToolDefinition } from './qwenStreamClient';

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
        description: '行为描述，简洁明了地描述观察到的行为'
      },
      matches: {
        type: 'array',
        description: '匹配的兴趣维度列表。为每个相关维度指定准确的关联度和强度，不要给所有维度设置相同的值',
        items: {
          type: 'object',
          properties: {
            dimension: {
              type: 'string',
              enum: ['Visual', 'Auditory', 'Tactile', 'Motor', 'Construction', 'Order', 'Cognitive', 'Social'],
              description: '兴趣维度类型：Visual(视觉)、Auditory(听觉)、Tactile(触觉)、Motor(运动)、Construction(建构)、Order(秩序)、Cognitive(认知)、Social(社交)'
            },
            weight: {
              type: 'number',
              description: '关联度 (0.4-1.0)。表示该行为与该兴趣维度的关联程度（只能是正值）：1.0=强关联（行为直接体现该维度，如"玩积木"与Construction），0.7=中等关联（行为部分体现该维度，如"玩积木"与Visual），0.4=弱关联（行为间接涉及该维度）。请根据行为的实际特征区分主次',
              minimum: 0.4,
              maximum: 1.0
            },
            intensity: {
              type: 'number',
              description: '强度 (-1.0 到 1.0)。表示孩子对该维度的喜欢/讨厌程度：1.0=非常喜欢（如"兴奋地玩"、"主动寻求"、"不愿停止"），0.5=比较喜欢，0=中性/无明显偏好，-0.5=比较抗拒，-1.0=非常讨厌（如"哭闹"、"逃避"、"强烈拒绝"）。根据孩子的情绪反应和参与度判断',
              minimum: -1.0,
              maximum: 1.0
            },
            reasoning: {
              type: 'string',
              description: '推理说明：解释为什么这个行为与该维度相关（关联度），以及孩子表现出的情绪态度（强度）。例如："需要手眼协调和空间感知能力（关联度高），孩子表现出专注和兴奋（强度为正）"'
            }
          },
          required: ['dimension', 'weight', 'intensity', 'reasoning']
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

// --- Universal Pipeline: Behavior Extraction Schema ---

export const BehaviorExtractionSchema = {
  name: 'behavior_extraction',
  description: '从互动记录中提取原子行为证据片段',
  schema: {
    type: 'object',
    properties: {
      evidences: {
        type: 'array',
        description: '提取到的行为证据列表。每条证据应该是一个独立的、可观察的行为事实，不包含推测或评价',
        items: {
          type: 'object',
          properties: {
            behavior: {
              type: 'string',
              description: '行为描述：简洁客观地描述孩子做了什么（20-50字）。例如："孩子主动抓取蓝色积木并尝试堆叠了3层"'
            },
            context: {
              type: 'string',
              description: '发生背景：行为发生时的环境或活动阶段（10-30字）。例如："自由搭建环节，家长在旁观察"'
            },
            source: {
              type: 'string',
              enum: ['LOG', 'VIDEO', 'PARENT'],
              description: '证据来源：LOG=聊天/互动日志，VIDEO=视频摘要观察，PARENT=家长口头反馈'
            },
            relatedDimensions: {
              type: 'array',
              description: '该行为可能关联的兴趣维度（预判，供下游专家参考）',
              items: {
                type: 'string',
                enum: ['Visual', 'Auditory', 'Tactile', 'Motor', 'Construction', 'Order', 'Cognitive', 'Social']
              }
            }
          },
          required: ['behavior', 'context', 'source', 'relatedDimensions'],
          additionalProperties: false
        },
        minItems: 1,
        maxItems: 15
      }
    },
    required: ['evidences'],
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
        description: '兴趣维度更新列表',
        items: {
          type: 'object',
          properties: {
            behavior: {
              type: 'string',
              description: '行为描述'
            },
            matches: {
              type: 'array',
              description: '关联的兴趣维度、关联度及强度',
              items: {
                type: 'object',
                properties: {
                  dimension: {
                    type: 'string',
                    enum: ['Visual', 'Auditory', 'Tactile', 'Motor', 'Construction', 'Order', 'Cognitive', 'Social'],
                    description: '兴趣维度类型'
                  },
                  weight: {
                    type: 'number',
                    description: '关联度 (0.4-1.0)：1.0=强关联，0.7=中等关联，0.4=弱关联。根据行为实际特征区分主次',
                    minimum: 0.4,
                    maximum: 1.0
                  },
                  intensity: {
                    type: 'number',
                    description: '强度 (-1.0 到 1.0)：表示孩子对该维度的喜欢/讨厌程度。1.0=非常喜欢，0=中性，-1.0=非常讨厌',
                    minimum: -1.0,
                    maximum: 1.0
                  },
                  reasoning: {
                    type: 'string',
                    description: '推理说明：解释为什么这个行为与该维度相关，以及孩子的情绪态度'
                  }
                },
                required: ['dimension', 'weight', 'intensity', 'reasoning']
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
              enum: ['自我调节', '亲密感', '双向沟通', '复杂沟通', '情绪思考', '逻辑思维'],
              description: 'DIR 六大能力维度'
            },
            scoreChange: {
              type: 'number',
              description: '分数变化（可正可负）'
            },
            reason: {
              type: 'string',
              description: '变化原因说明'
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

export const LogBehaviorTool = {
  type: 'function' as const,
  function: {
    name: 'log_behavior',
    description: '记录儿童的新的、当前的具体行为。只有当家长正在报告孩子此刻或最近发生的具体行为事件时才调用此工具。例如："孩子正在玩积木"、"他现在一直看着旋转的东西"、"她刚才在排列玩具"。注意：如果家长是在询问历史数据（如"他有什么爱玩的？"、"根据他最近的行为..."）或讨论总结，则不要调用此工具。工具会自动调用专门的行为分析Agent来解析行为并关联兴趣维度。',
    parameters: {
      type: 'object',
      properties: {
        behaviorDescription: {
          type: 'string',
          description: '家长描述的完整行为内容，保留原始描述的细节和上下文。例如："孩子正在玩积木，很专注地搭建高塔，看起来很兴奋"、"他现在一直盯着旋转的风扇，眼睛都不眨"、"她刚才在排列玩具，把所有小汽车排成一排"'
        }
      },
      required: ['behaviorDescription']
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

export const GenerateAssessmentTool = {
  type: 'function' as const,
  function: {
    name: 'generate_assessment',
    description: '生成孩子的正式综合评估报告（PDF格式的专业报告）。只有当家长明确要求生成正式报告时才调用此工具，例如：1) "生成评估报告" 2) "我要一份评估报告" 3) "给我一份正式的评估" 4) "导出评估报告"。注意：如果家长只是询问孩子的情况、想推荐游戏、或日常咨询，不要调用此工具。',
    parameters: {
      type: 'object',
      properties: {
        reason: {
          type: 'string',
          description: '为什么需要生成评估报告，例如：家长明确要求生成正式评估报告'
        }
      },
      required: ['reason']
    }
  }
};

// 兴趣分析工具
export const AnalyzeInterestTool = {
  type: 'function' as const,
  function: {
    name: 'analyze_interest',
    description: `分析孩子的兴趣维度，生成8个维度的强度/探索度分析、分类建议和干预建议。这是游戏推荐的第一步。

🚨 **调用场景**：
1. 家长说"推荐游戏"、"今天玩什么"、"根据孩子最近的情况推荐游戏" → 调用此工具进行兴趣分析
2. 家长说"重新分析"、"再看看兴趣" → 重新调用此工具
3. 家长说"换一批"且想重新分析 → 调用此工具
4. 家长询问"孩子最近的情况"并且想要游戏推荐 → 调用此工具

⚠️ 调用后流程：
- 展示分析结果（维度强度/探索度、分类、干预建议）
- 与家长讨论，确定干预维度和策略
- 家长确认后调用 plan_floor_game 生成游戏方案`,
    parameters: {
      type: 'object',
      properties: {
        reason: {
          type: 'string',
          description: '调用原因，如"家长请求推荐游戏"、"家长要求重新分析"、"家长询问最近情况并想要游戏推荐"'
        },
        parentContext: {
          type: 'string',
          description: '家长提供的上下文信息（如特殊需求、关注点等）。如果没有则为空字符串'
        }
      },
      required: ['reason']
    }
  }
};

// 地板游戏计划工具
export const PlanFloorGameTool = {
  type: 'function' as const,
  function: {
    name: 'plan_floor_game',
    description: `基于确定的干预维度和策略，设计完整的地板游戏实施方案。这是游戏推荐的第二步。

⚠️ 调用前提：
- 必须已经调用过 analyze_interest 工具
- 家长已经与你讨论并确认了干预维度和策略
- 如果家长还没确认，应该先讨论

⚠️ 调用场景：
1. 家长确认了干预维度（如"我想从视觉和触觉入手"）→ 调用此工具
2. 家长说"换一批游戏"但不需要重新分析 → 重新调用此工具
3. 家长说"快点推荐"、"随便推荐" → 使用 leverage 维度调用此工具

🚨 **核心原则 - 必须调用工具**：
- 任何涉及生成游戏方案的请求，都必须调用此工具
- 绝对不能直接用自然语言描述游戏内容或提供游戏步骤`,
    parameters: {
      type: 'object',
      properties: {
        targetDimensions: {
          type: 'array',
          items: {
            type: 'string',
            enum: ['Visual', 'Auditory', 'Tactile', 'Motor', 'Construction', 'Order', 'Cognitive', 'Social']
          },
          description: '目标干预维度（1-3个），从兴趣分析结果中确定'
        },
        strategy: {
          type: 'string',
          enum: ['leverage', 'explore', 'mixed'],
          description: '干预策略：leverage（利用已有兴趣）、explore（探索新维度）、mixed（混合策略）'
        },
        parentPreferences: {
          type: 'object',
          description: '家长偏好（可选）',
          properties: {
            environment: {
              type: 'string',
              enum: ['indoor', 'outdoor', 'both', 'any'],
              description: '环境偏好'
            },
            duration: {
              type: 'string',
              enum: ['short', 'medium', 'long', 'any'],
              description: '时长偏好'
            },
            otherRequirements: {
              type: 'string',
              description: '其他要求'
            }
          }
        },
        conversationHistory: {
          type: 'string',
          description: '最近的对话历史（最多5轮），帮助理解上下文'
        }
      },
      required: ['targetDimensions', 'strategy', 'conversationHistory']
    }
  }
};

// 查询工具

export const QueryChildProfileTool = {
  type: 'function' as const,
  function: {
    name: 'query_child_profile',
    description: '查询当前孩子的基础信息（姓名、性别、年龄、诊断画像等）。当家长询问孩子的基本资料、个人信息、档案信息时调用。',
    parameters: {
      type: 'object',
      properties: {},
      required: []
    }
  }
};

export const QueryRecentAssessmentsTool = {
  type: 'function' as const,
  function: {
    name: 'query_recent_assessments',
    description: '查询最近的综合评估报告。当家长询问"之前的评估结果"、"上次评估怎么样"、"最近的报告"等时调用。',
    parameters: {
      type: 'object',
      properties: {
        count: {
          type: 'number',
          description: '查询数量，默认3条'
        }
      },
      required: []
    }
  }
};

export const QueryRecentBehaviorsTool = {
  type: 'function' as const,
  function: {
    name: 'query_recent_behaviors',
    description: '查询最近记录的行为数据。当家长询问"最近记录了什么行为"、"孩子最近的表现"、"之前记录的行为"等时调用。',
    parameters: {
      type: 'object',
      properties: {
        count: {
          type: 'number',
          description: '查询数量，默认10条'
        }
      },
      required: []
    }
  }
};

export const QueryFloorGamesTool = {
  type: 'function' as const,
  function: {
    name: 'query_floor_games',
    description: '查询数据库中已保存的地板游戏记录。当家长询问"之前玩过什么游戏"、"最近的游戏"、"游戏记录"、"做过哪些游戏"等时调用。',
    parameters: {
      type: 'object',
      properties: {
        count: {
          type: 'number',
          description: '查询数量，默认5条'
        }
      },
      required: []
    }
  }
};

// 所有对话工具
export const ChatTools = [
  AnalyzeInterestTool,
  PlanFloorGameTool,
  LogBehaviorTool,
  NavigatePageTool,
  GenerateAssessmentTool,
  QueryChildProfileTool,
  QueryRecentAssessmentsTool,
  QueryRecentBehaviorsTool,
  QueryFloorGamesTool
];

// --- Comprehensive Assessment Schema ---

export const ComprehensiveAssessmentSchema = {
  name: 'comprehensive_assessment',
  description: '综合评估结果',
  schema: {
    type: 'object',
    properties: {
      summary: {
        type: 'string',
        description: '评估摘要，一句话概括孩子当前状态和主要特点，50字以内'
      },
      currentProfile: {
        type: 'string',
        description: '当前孩子的详细画像，200-300字，包括性格特点、兴趣偏好、能力水平、社交表现、发展特点'
      },
      nextStepSuggestion: {
        type: 'string',
        description: '下一步干预建议，150-200字，具体可操作，基于孩子的兴趣点设计活动，针对需要提升的能力'
      }
    },
    required: [
      'summary',
      'currentProfile',
      'nextStepSuggestion'
    ],
    additionalProperties: false
  }
};

// --- Game Recommendation Schema ---

export const GameRecommendationDetailedSchema = {
  name: 'game_recommendation_detailed',
  description: '详细游戏推荐结果',
  schema: {
    type: 'object',
    properties: {
      game: {
        type: 'object',
        description: '推荐的游戏完整信息',
        properties: {
          id: { type: 'string', description: '游戏ID' },
          title: { type: 'string', description: '游戏名称' },
          target: { type: 'string', description: '训练目标' },
          duration: { type: 'string', description: '游戏时长' },
          isVR: { type: 'boolean', description: '是否为VR游戏' },
          steps: {
            type: 'array',
            description: '游戏步骤',
            items: {
              type: 'object',
              properties: {
                instruction: { type: 'string', description: '步骤说明' },
                guidance: { type: 'string', description: '引导要点' }
              },
              required: ['instruction', 'guidance']
            }
          }
        },
        required: ['id', 'title', 'target', 'duration', 'steps']
      },
      reason: {
        type: 'string',
        description: '详细推荐理由，150-200字，说明为什么这个游戏最适合'
      },
      parentGuidance: {
        type: 'string',
        description: '家长指导要点，150字左右，如何引导、注意事项'
      },
      adaptationSuggestions: {
        type: 'array',
        description: '3-5条适应性调整建议',
        items: {
          type: 'string',
          description: '每条30-50字，应对不同情况的调整方法'
        },
        minItems: 3,
        maxItems: 5
      }
    },
    required: [
      'game',
      'reason',
      'parentGuidance',
      'adaptationSuggestions'
    ],
    additionalProperties: false
  }
};

// --- Game Review Schema ---

export const GameReviewSchema = {
  name: 'game_review',
  description: '游戏复盘结果',
  schema: {
    type: 'object',
    properties: {
      reviewSummary: {
        type: 'string',
        description: '游戏过程总结与复盘，200-400字，从 DIR/Floortime 视角回顾本次游戏互动过程、孩子表现、亲子互动质量'
      },
      scores: {
        type: 'object',
        description: '多维度打分，每个维度 0-100',
        properties: {
          childEngagement: { type: 'number', description: '孩子参与度/配合度', minimum: 0, maximum: 100 },
          gameCompletion: { type: 'number', description: '游戏完成度', minimum: 0, maximum: 100 },
          emotionalConnection: { type: 'number', description: '情感连接质量', minimum: 0, maximum: 100 },
          communicationLevel: { type: 'number', description: '沟通互动水平', minimum: 0, maximum: 100 },
          skillProgress: { type: 'number', description: '目标能力进步', minimum: 0, maximum: 100 },
          parentExecution: { type: 'number', description: '家长执行质量', minimum: 0, maximum: 100 },
          feedbackScore: { type: 'number', description: '反馈质量 (单次回应及时性与情感连结)', minimum: 0, maximum: 100 },
          explorationScore: { type: 'number', description: '探索广度 (尝试新事物意愿与行为多样性)', minimum: 0, maximum: 100 }
        },
        required: ['childEngagement', 'gameCompletion', 'emotionalConnection', 'communicationLevel', 'skillProgress', 'parentExecution', 'feedbackScore', 'explorationScore'],
        additionalProperties: false
      },
      recommendation: {
        type: 'string',
        enum: ['continue', 'adjust', 'avoid'],
        description: '建议：continue(继续此类游戏)、adjust(调整后再玩)、avoid(避免此类游戏)'
      },
      nextStepSuggestion: {
        type: 'string',
        description: '下一步建议，200-300字，包含：是否继续此类游戏的理由、需要改进的方面、未来干预方向'
      }
    },
    required: ['reviewSummary', 'scores', 'recommendation', 'nextStepSuggestion'],
    additionalProperties: false
  }
};

// --- Interest Analysis Schema ---

export const InterestAnalysisSchema = {
  name: 'interest_analysis',
  description: '兴趣维度分析结果',
  schema: {
    type: 'object',
    properties: {
      summary: {
        type: 'string',
        description: '总体分析，100-150字，概括孩子的兴趣特点和发展状况'
      },
      dimensions: {
        type: 'array',
        description: '8个兴趣维度的详细分析',
        items: {
          type: 'object',
          properties: {
            dimension: {
              type: 'string',
              enum: ['Visual', 'Auditory', 'Tactile', 'Motor', 'Construction', 'Order', 'Cognitive', 'Social'],
              description: '兴趣维度名称'
            },
            strength: {
              type: 'number',
              description: '强度 0-100，表示孩子对该维度的兴趣程度',
              minimum: 0,
              maximum: 100
            },
            exploration: {
              type: 'number',
              description: '探索度 0-100，表示孩子在该维度的探索广度和深度',
              minimum: 0,
              maximum: 100
            },
            category: {
              type: 'string',
              enum: ['leverage', 'explore', 'avoid', 'neutral'],
              description: '分类：leverage(可利用的优势)、explore(可探索的潜力)、avoid(应避免的敏感点)、neutral(中性)'
            },
            specificObjects: {
              type: 'array',
              description: '从行为中提取的具体对象，如"积木"、"音乐"、"绒布"等',
              items: {
                type: 'string'
              }
            },
            reasoning: {
              type: 'string',
              description: '推理说明，50-80字，解释为什么这样分类'
            }
          },
          required: ['dimension', 'strength', 'exploration', 'category', 'specificObjects', 'reasoning'],
          additionalProperties: false
        },
        minItems: 8,
        maxItems: 8
      },
      leverageDimensions: {
        type: 'array',
        description: '可利用的维度列表（优势维度）',
        items: {
          type: 'string',
          enum: ['Visual', 'Auditory', 'Tactile', 'Motor', 'Construction', 'Order', 'Cognitive', 'Social']
        }
      },
      exploreDimensions: {
        type: 'array',
        description: '可探索的维度列表（潜力维度）',
        items: {
          type: 'string',
          enum: ['Visual', 'Auditory', 'Tactile', 'Motor', 'Construction', 'Order', 'Cognitive', 'Social']
        }
      },
      avoidDimensions: {
        type: 'array',
        description: '应避免的维度列表（敏感维度）',
        items: {
          type: 'string',
          enum: ['Visual', 'Auditory', 'Tactile', 'Motor', 'Construction', 'Order', 'Cognitive', 'Social']
        }
      },
      interventionSuggestions: {
        type: 'array',
        description: '3-5条干预建议',
        items: {
          type: 'object',
          properties: {
            targetDimension: {
              type: 'string',
              enum: ['Visual', 'Auditory', 'Tactile', 'Motor', 'Construction', 'Order', 'Cognitive', 'Social'],
              description: '目标维度'
            },
            strategy: {
              type: 'string',
              enum: ['leverage', 'explore'],
              description: '策略：leverage(利用)或explore(探索)'
            },
            suggestion: {
              type: 'string',
              description: '建议内容，50-80字'
            },
            rationale: {
              type: 'string',
              description: '理由说明，30-50字'
            },
            exampleActivities: {
              type: 'array',
              description: '2-3个示例活动',
              items: {
                type: 'string'
              },
              minItems: 2,
              maxItems: 3
            }
          },
          required: ['targetDimension', 'strategy', 'suggestion', 'rationale', 'exampleActivities'],
          additionalProperties: false
        },
        minItems: 3,
        maxItems: 5
      }
    },
    required: ['summary', 'dimensions', 'leverageDimensions', 'exploreDimensions', 'avoidDimensions', 'interventionSuggestions'],
    additionalProperties: false
  }
};

// --- Game Implementation Plan Schema ---

export const GameImplementationPlanSchema = {
  name: 'game_implementation_plan',
  description: '游戏实施方案',
  schema: {
    type: 'object',
    properties: {
      gameId: {
        type: 'string',
        description: '游戏ID，格式：floor_game_时间戳'
      },
      gameTitle: {
        type: 'string',
        description: '游戏名称，简洁有吸引力，10-20字'
      },
      summary: {
        type: 'string',
        description: '游戏概要，2-3句话描述游戏的核心玩法，80-120字'
      },
      goal: {
        type: 'string',
        description: '游戏目标，明确的训练目标，30-50字'
      },
      steps: {
        type: 'array',
        description: '游戏步骤，3-6个步骤。地板游戏是以孩子为主导的游戏，家长跟随孩子的兴趣和节奏，不设定每步的预期效果',
        items: {
          type: 'object',
          properties: {
            stepTitle: {
              type: 'string',
              description: '步骤标题，如"第一步：准备材料"、"第二步：观察并跟随"'
            },
            instruction: {
              type: 'string',
              description: '详细指令，家长应该如何跟随孩子、如何回应孩子的行为，50-100字。强调跟随而非引导'
            },
            guidance: {
              type: 'string',
              description: '互动要点和注意事项，20-50字，帮助家长把握时机和细节'
            }
          },
          required: ['stepTitle', 'instruction', 'guidance'],
          additionalProperties: false
        },
        minItems: 3,
        maxItems: 6
      },
      materials: {
        type: 'array',
        description: '所需材料清单',
        items: {
          type: 'string'
        }
      },
      _analysis: {
        type: 'string',
        description: 'LLM 分析总结（可选），用于显示设计思路'
      }
    },
    required: ['gameId', 'gameTitle', 'summary', 'goal', 'steps'],
    additionalProperties: false
  }
};

// --- Game Selection Schema (recommendGame) ---

export const GameSelectionSchema = {
  name: 'game_selection',
  description: '从候选列表中选择最适合的游戏序号',
  schema: {
    type: 'object',
    properties: {
      id: {
        type: 'string',
        description: '选中游戏的序号，如 "1"、"2"、"3"'
      }
    },
    required: ['id'],
    additionalProperties: false
  }
};

// --- Online Search Game List Schema ---

export const OnlineSearchGameListSchema = {
  name: 'online_search_game_list',
  description: '从搜索结果中提取的地板游戏列表',
  schema: {
    type: 'object',
    properties: {
      games: {
        type: 'array',
        description: '提取到的地板游戏列表，3-5个',
        items: {
          type: 'object',
          properties: {
            title: { type: 'string', description: '游戏名称' },
            target: { type: 'string', description: '训练目标' },
            duration: { type: 'string', description: '游戏时长' },
            reason: { type: 'string', description: '适合自闭症儿童的理由' },
            summary: { type: 'string', description: '游戏玩法概要，2-3句话' },
            materials: {
              type: 'array',
              description: '所需材料',
              items: { type: 'string' }
            },
            keyPoints: {
              type: 'array',
              description: '3-5个关键要点',
              items: { type: 'string' },
              minItems: 3,
              maxItems: 5
            }
          },
          required: ['title', 'target', 'duration', 'summary', 'materials', 'keyPoints'],
          additionalProperties: false
        },
        minItems: 1,
        maxItems: 5
      }
    },
    required: ['games'],
    additionalProperties: false
  }
};

// ─── ReAct Agent 内部工具定义 ────────────────────────────────────────────────
// 仅供游戏推荐 Agent 的 ReAct 循环使用，不暴露给外部对话

export const ReActFetchMemoryTool: ToolDefinition = {
  type: 'function',
  function: {
    name: 'fetchMemory',
    description:
      '从记忆层搜索与儿童相关的历史事实，包括行为偏好、维度变化、游戏历史、对活动的正负向反应等。' +
      '使用自然语言语义查询，返回 graphiti 提炼的结构化事实和待处理的原始观察。',
    parameters: {
      type: 'object',
      properties: {
        query: {
          type: 'string',
          description: '语义搜索查询，描述你想了解的信息，例如"孩子对视觉刺激和色彩的历史反应"'
        }
      },
      required: ['query']
    }
  }
};

export const ReActFetchKnowledgeTool: ToolDefinition = {
  type: 'function',
  function: {
    name: 'fetchKnowledge',
    description:
      '通过互联网搜索 DIR/Floortime 游戏资料、自闭症儿童干预方法、感统游戏案例等专业知识。' +
      '当需要参考外部游戏设计资料或寻找具体活动案例时使用。' +
      '返回格式化的搜索摘要文本。\n' +
      '// TODO: 未来版本将同时并行查询本地 RAG 知识库（已验证干预案例），与网络搜索结果合并返回。',
    parameters: {
      type: 'object',
      properties: {
        query: {
          type: 'string',
          description: '搜索关键词，例如"自闭症儿童视觉感统游戏 DIR Floortime 室内活动"'
        }
      },
      required: ['query']
    }
  }
};

// 兴趣分析阶段只需要记忆搜索，不需要联网搜索
export const ReActInterestAnalysisTools: ToolDefinition[] = [ReActFetchMemoryTool];

// 游戏计划阶段同时使用记忆搜索和知识搜索
export const ReActGamePlanTools: ToolDefinition[] = [ReActFetchMemoryTool, ReActFetchKnowledgeTool];
