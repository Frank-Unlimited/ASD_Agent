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
              description: '关联度 (0.1-1.0)。表示该行为与该兴趣维度的关联程度（只能是正值）：1.0=强关联（行为直接体现该维度，如"玩积木"与Construction），0.7=中等关联（行为部分体现该维度，如"玩积木"与Visual），0.4=弱关联（行为间接涉及该维度）。请根据行为的实际特征区分主次',
              minimum: 0.1,
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
                    description: '关联度 (0.1-1.0)：1.0=强关联，0.7=中等关联，0.4=弱关联。根据行为实际特征区分主次',
                    minimum: 0.1,
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
    description: '记录儿童的新的、当前的具体行为并关联兴趣维度。只有当家长正在报告孩子此刻或最近发生的具体行为事件时才调用此工具。例如："孩子正在玩积木"、"他现在一直看着旋转的东西"、"她刚才在排列玩具"。注意：如果家长是在询问历史数据（如"他有什么爱玩的？"、"根据他最近的行为..."）或讨论总结，则不要调用此工具。',
    parameters: {
      type: 'object',
      properties: {
        behavior: {
          type: 'string',
          description: '精简的行为描述，例如："正在玩积木"、"盯着旋转物体"、"排列玩具成一排"'
        },
        dimensions: {
          type: 'array',
          description: '相关的兴趣维度、关联度及强度。每个维度需要指定两个独立的值：1) weight(关联度)：该行为与该兴趣维度的关联程度，只能是0.1-1.0的正值；2) intensity(强度)：孩子对该维度的喜欢/讨厌程度，范围是-1.0到1.0（正值表示喜欢，负值表示讨厌，0表示中性）',
          items: {
            type: 'object',
            properties: {
              dimension: {
                type: 'string',
                enum: ['Visual', 'Auditory', 'Tactile', 'Motor', 'Construction', 'Order', 'Cognitive', 'Social'],
                description: '兴趣维度名称'
              },
              weight: {
                type: 'number',
                description: '关联度 (0.1-1.0，只能是正值)：1.0=强关联（行为直接体现该维度），0.7=中等关联，0.4=弱关联。例如："玩积木"与Construction是1.0，与Visual是0.7，与Motor是0.6',
                minimum: 0.1,
                maximum: 1.0
              },
              intensity: {
                type: 'number',
                description: '强度 (-1.0 到 1.0)：表示孩子对该维度的情绪态度。1.0=非常喜欢（兴奋、主动、不愿停止），0.5=比较喜欢，0=中性，-0.5=比较抗拒，-1.0=非常讨厌（哭闹、逃避、拒绝）。根据孩子的情绪反应和参与度判断',
                minimum: -1.0,
                maximum: 1.0
              },
              reasoning: {
                type: 'string',
                description: '推理说明：解释关联度（为什么相关）和强度（孩子的情绪态度）。例如："需要手眼协调（关联度高），孩子表现出专注和兴奋（强度为正）"'
              }
            },
            required: ['dimension', 'weight', 'intensity', 'reasoning']
          }
        },
        analysis: {
          type: 'string',
          description: '一句话分析其发展意义，例如："显示出对建构活动的兴趣，有助于精细动作发展"'
        }
      },
      required: ['behavior', 'dimensions', 'analysis']
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

export const GenerateAssessmentTool = {
  type: 'function' as const,
  function: {
    name: 'generate_assessment',
    description: '生成孩子的综合评估报告。当家长询问以下内容时必须调用此工具：1) 孩子的评估报告 2) 孩子的发展情况 3) 孩子的当前状态 4) 孩子的进步情况 5) 孩子的综合评估 6) 查看评估 7) 生成报告。这个工具会基于历史数据生成正式的、结构化的评估报告。',
    parameters: {
      type: 'object',
      properties: {
        reason: {
          type: 'string',
          description: '为什么需要生成评估报告，例如：家长询问孩子的发展情况'
        }
      },
      required: ['reason']
    }
  }
};

// 新增：游戏方向建议工具
export const SuggestGameDirectionsTool = {
  type: 'function' as const,
  function: {
    name: 'suggest_game_directions',
    description: `基于孩子档案生成3个游戏方向建议。这是游戏推荐的第一阶段：需求探讨。

🚨 **关键调用场景（必须调用此工具）**：
1. 首次推荐游戏：已经通过对话收集到完整的 userPreferences
2. 用户要求"换一批"、"再推荐"、"不喜欢这些"、"推荐一个完全不同的"等 → **立即调用此工具，不要先询问原因**
3. 用户明确表示不需要探讨，直接推荐（如"随便推荐"、"你决定就好"、"快点推荐"）
4. 已经与用户探讨了3轮对话，但用户仍未明确所有偏好（此时使用已收集的信息和默认值）

⚠️ 首次推荐时的探讨流程：
如果是首次推荐游戏，且不满足上述条件2-4，应该先与用户探讨需求：
- 询问环境偏好：室内还是户外？
- 询问时长偏好：短时间（10分钟内）、中等（10-20分钟）还是长时间（20分钟以上）？
- 询问材料限制：有没有不方便使用的材料？
- 询问其他要求：有什么特殊需求吗？

⚠️ "换一批"场景的处理：
- 当用户说"换一批"、"再推荐"、"不喜欢这些"时，**立即调用此工具**
- 如果用户明确了新要求（如"要更简单的"、"不要光影的"），在 userPreferences 中更新
- 如果用户没有明确新要求，使用原有 userPreferences
- **绝对不能**直接用自然语言推荐游戏方向，必须调用工具

⚠️ 严格流程要求：
- 此工具是游戏推荐三阶段流程的第一步
- 调用此工具后，必须等待家长选择方向，不能直接调用后续工具
- 下一步必须调用 search_candidate_games，不能跳过`,
    parameters: {
      type: 'object',
      properties: {
        userPreferences: {
          type: 'object',
          description: '用户的偏好和要求（必须提供，如果用户没有明确说明则使用默认值）',
          properties: {
            environment: {
              type: 'string',
              enum: ['indoor', 'outdoor', 'both', 'any'],
              description: '环境偏好：indoor(室内)、outdoor(户外)、both(都可以)、any(无要求，默认值)'
            },
            duration: {
              type: 'string',
              enum: ['short', 'medium', 'long', 'any'],
              description: '时长偏好：short(短时间10分钟内)、medium(中等10-20分钟)、long(长时间20分钟以上)、any(无要求，默认值)'
            },
            avoidMaterials: {
              type: 'array',
              items: { type: 'string' },
              description: '需要避免的材料（如：积木、水、颜料等），如果用户说"没有XX"或"不要XX"。如果没有则为空数组'
            },
            preferMaterials: {
              type: 'array',
              items: { type: 'string' },
              description: '偏好使用的材料（如果用户明确提到）。如果没有则为空数组'
            },
            otherRequirements: {
              type: 'string',
              description: '其他特殊要求（如：安静的、不需要跑动的、适合两个人玩的等）。如果没有则为空字符串'
            }
          },
          required: ['environment', 'duration', 'avoidMaterials', 'preferMaterials', 'otherRequirements']
        },
        conversationHistory: {
          type: 'string',
          description: '最近的对话历史（最多5轮），帮助理解上下文。格式：用户: xxx\\nAI: xxx'
        },
        discussionRounds: {
          type: 'number',
          description: '已经探讨的轮数（用于判断是否达到最大轮数3轮）',
          default: 0
        }
      },
      required: ['userPreferences', 'conversationHistory']
    }
  }
};

// 新增：检索候选游戏工具
export const SearchCandidateGamesTool = {
  type: 'function' as const,
  function: {
    name: 'search_candidate_games',
    description: `根据家长选定的游戏方向，检索并返回3个候选游戏的概要信息。这是游戏推荐的第二阶段：方案细化。

⚠️ 调用前提：
- 必须已经调用过 suggest_game_directions 工具
- 家长已经明确选择了某个游戏方向（可能说"第一个"、"视觉建构"、"户外的那个"等）
- 如果家长还没选择方向，应该先询问家长的选择

⚠️ 返回内容：
- 此阶段只返回游戏概要（玩法概要、关键要点、材料、时长）
- 不包含详细步骤，详细步骤会在第三阶段生成
- 返回3个候选游戏供家长选择

⚠️ 严格流程要求：
- 此工具是游戏推荐三阶段流程的第二步
- 调用此工具后，必须等待家长选择具体游戏，不能直接调用 recommend_game_final
- 下一步必须调用 recommend_game_final，不能跳过`,
    parameters: {
      type: 'object',
      properties: {
        directionName: {
          type: 'string',
          description: '家长选择的游戏方向名称（从 suggest_game_directions 返回的方向中选择）'
        },
        count: {
          type: 'number',
          description: '候选游戏数量，固定为3',
          default: 3
        },
        additionalRequirements: {
          type: 'string',
          description: '家长在选择方向后提出的额外要求（如："不要太复杂"、"材料简单一点"等）。如果没有则为空字符串',
          default: ''
        },
        conversationHistory: {
          type: 'string',
          description: '最近的对话历史（最多5轮），帮助理解上下文。格式：用户: xxx\\nAI: xxx'
        }
      },
      required: ['directionName', 'conversationHistory']
    }
  }
};

// 修改：推荐游戏工具（仅在最终确认后调用）
export const RecommendGameFinalTool = {
  type: 'function' as const,
  function: {
    name: 'recommend_game_final',
    description: `基于家长选定的游戏概要，深度细化游戏步骤，生成完整的实施方案并显示游戏卡片。这是游戏推荐的第三阶段：实施确认。

⚠️ 调用前提：
- 必须已经调用过 search_candidate_games 工具
- 家长已经明确选择了某个具体游戏（可能说"第二个"、"积木游戏"、"1"等）
- 如果家长还没选择游戏，应该先询问家长的选择

⚠️ 功能说明：
- 此工具会将游戏概要（关键要点）细化为详细的、可直接执行的步骤
- 结合孩子的具体情况进行个性化调整
- 生成完整的实施方案：详细步骤、家长指导、预期效果、问题应对
- 显示游戏卡片供家长查看和确认

⚠️ 严格流程要求：
- 此工具是游戏推荐三阶段流程的第三步（最后一步）
- 这是唯一会显示游戏卡片的工具
- 调用此工具后，游戏推荐流程完成`,
    parameters: {
      type: 'object',
      properties: {
        gameId: {
          type: 'string',
          description: '家长选定的游戏ID、游戏名称或序号（如"影子模仿游戏"、"第一个"、"1"）。从 search_candidate_games 返回的候选游戏中选择'
        },
        customizations: {
          type: 'array',
          items: { type: 'string' },
          description: '家长要求的调整（可选）。如果家长提出了特殊要求（如"简化一点"、"增加难度"），在这里列出。如果没有则为空数组',
          default: []
        },
        conversationHistory: {
          type: 'string',
          description: '最近的对话历史（最多5轮），帮助理解上下文。格式：用户: xxx\\nAI: xxx'
        }
      },
      required: ['gameId', 'conversationHistory']
    }
  }
};

// 所有对话工具
export const ChatTools = [
  SuggestGameDirectionsTool,
  SearchCandidateGamesTool,
  RecommendGameFinalTool,
  LogBehaviorTool,
  CreateWeeklyPlanTool,
  NavigatePageTool,
  GenerateAssessmentTool
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
      expectedOutcome: {
        type: 'string',
        description: '预期效果，100字左右，具体可观察的改善'
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
      'expectedOutcome',
      'parentGuidance',
      'adaptationSuggestions'
    ],
    additionalProperties: false
  }
};
