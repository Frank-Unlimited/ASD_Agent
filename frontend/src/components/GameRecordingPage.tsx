import React, { useState, useEffect, useCallback, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Timer, Activity, BrainCircuit, ChevronLeft, Square } from 'lucide-react';
import {
  ButtonConfig,
  GameSessionConfig,
  AIInference,
  AIProbe,
  SessionSummary,
  startGameSession,
  recordBehaviorEvent,
  submitSnapshotResponse,
  completeGameSession,
  completeSessionWithSummary,
  getInferences,
  getCurrentProbe,
  confirmInference as apiConfirmInference,
  respondToProbe as apiRespondToProbe,
} from '../services/gameRecordingService';
import { GameStep } from '../types';
import { SnapshotCard } from './SnapshotCard';
import { DynamicButtonGroup } from './DynamicButtonGroup';
import InferenceTimeline from './InferenceTimeline';
import AIProbeCard from './AIProbeCard';
import SessionSummaryModal from './SessionSummaryModal';
import StepGuidePanel from './StepGuidePanel';

// ─── 类型 ────────────────────────────────────────────────────

interface GameRecordingPageProps {
  gameName?: string;
  gameType?: string;
  childId?: string;
  plannedDuration?: number;
  onBack: () => void;
  onComplete?: (sessionId: string) => void;
}

interface ToastMessage {
  id: number;
  text: string;
  eventId?: string;
  canUndo?: boolean;
}

// ─── 轮询间隔（毫秒）────────────────────────────────────────────
const INFERENCE_POLL_INTERVAL = 10_000;
const PROBE_POLL_INTERVAL = 15_000;

// ─── Mock 游戏步骤数据（后续可由 props/API 注入）───────────────
const MOCK_GAME_STEPS: GameStep[] = [
  {
    stepTitle: '面对面坐好',
    instruction: '和孩子面对面坐在地板上，确保能平视孩子的眼睛。把积木放在你们之间。',
    guidance: '位置是关键！确保你能自然地和孩子对视。如果孩子倾向低头，可以稍微降低你的位置。',
  },
  {
    stepTitle: '展示积木引起兴趣',
    instruction: "拿起一块彩色积木，在孩子视线范围内缓慢移动，说'看，漂亮的积木！'等待孩子注意。",
    guidance: '不要急于放下积木，给孩子时间去注意和反应。如果孩子看向积木，立即微笑回应。',
  },
  {
    stepTitle: '示范搭建',
    instruction: "把第一块积木放在地上，夸张地说'妈妈放一块！'然后看向孩子，递出第二块。",
    guidance: '关键动作：放积木→看孩子→递积木。这个三步循环建立轮流的期待感。',
  },
  {
    stepTitle: '轮流搭建',
    instruction: "和孩子轮流往上放积木。每次轮到你时说'妈妈放'，轮到孩子时说'宝宝放'。",
    guidance: "观察孩子是否主动等待轮到自己。如果孩子抢着放，温柔地说'等等，先妈妈'。",
  },
  {
    stepTitle: '庆祝与命名',
    instruction: "积木搭到3-4层时，兴奋地说'哇，好高的塔！'和孩子一起拍手庆祝。",
    guidance: '这是建立共同情感体验的关键时刻。观察孩子是否跟随你的情绪表达。',
  },
  {
    stepTitle: '自然收尾',
    instruction: "让积木塔自然倒塌或轻轻推倒，说'倒啦！再来一次？'观察孩子反应决定是否继续。",
    guidance: '如果孩子想继续，可以再玩1-2轮。如果注意力转移，顺势结束并给予肯定。',
  },
];

// ─── 每个步骤推荐的上下文感知按钮（体现AI根据游戏阶段智能推荐）───
const STEP_CONTEXT_BUTTONS: Record<number, Array<{id: string, label: string, icon: string, valence: number}>> = {
  0: [ // 面对面坐好
    { id: 'eye_contact_init', label: '对视建立', icon: '👁️', valence: 1 },
    { id: 'body_orient', label: '身体朝向', icon: '🧭', valence: 1 },
    { id: 'calm_state', label: '安静就坐', icon: '🪑', valence: 1 },
  ],
  1: [ // 展示积木引起兴趣
    { id: 'visual_track', label: '视觉追踪', icon: '👀', valence: 1 },
    { id: 'reach_out', label: '伸手触碰', icon: '🤚', valence: 1 },
    { id: 'vocal_response', label: '发声回应', icon: '🗣️', valence: 1 },
  ],
  2: [ // 示范搭建
    { id: 'imitation', label: '模仿动作', icon: '🪞', valence: 1 },
    { id: 'watch_demo', label: '注视示范', icon: '🎯', valence: 1 },
    { id: 'anticipation', label: '期待反应', icon: '✨', valence: 1 },
  ],
  3: [ // 轮流搭建
    { id: 'turn_taking', label: '等待轮流', icon: '🔄', valence: 1 },
    { id: 'hand_over', label: '递出积木', icon: '🤝', valence: 1 },
    { id: 'verbal_cue', label: '语言提示', icon: '💬', valence: 1 },
  ],
  4: [ // 庆祝与命名
    { id: 'shared_joy', label: '共享喜悦', icon: '🎉', valence: 1 },
    { id: 'clap_together', label: '一起拍手', icon: '👏', valence: 1 },
    { id: 'naming', label: '命名作品', icon: '🏷️', valence: 1 },
  ],
  5: [ // 自然收尾
    { id: 'farewell_gaze', label: '告别对视', icon: '👋', valence: 1 },
    { id: 'request_more', label: '请求再来', icon: '🔁', valence: 1 },
    { id: 'smooth_end', label: '平稳过渡', icon: '🌅', valence: 0 },
  ],
};

// ─── 组件 ────────────────────────────────────────────────────

export const GameRecordingPage: React.FC<GameRecordingPageProps> = ({
  gameName = '地板游戏',
  gameType = 'floor_time',
  childId = 'default_child',
  plannedDuration = 20,
  onBack,
  onComplete,
}) => {
  // 会话状态
  const [sessionConfig, setSessionConfig] = useState<GameSessionConfig | null>(null);
  const [isSessionActive, setIsSessionActive] = useState(false);
  const [elapsedSeconds, setElapsedSeconds] = useState(0);
  const [eventCount, setEventCount] = useState(0);

  // 按钮状态
  const [dynamicButtons, setDynamicButtons] = useState<ButtonConfig[]>([]);
  const [fixedButtons, setFixedButtons] = useState<ButtonConfig[]>([]);

  // 长按二级菜单
  const [longPressMenu, setLongPressMenu] = useState<{ button: ButtonConfig; x: number; y: number } | null>(null);
  const longPressTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const longPressTriggeredRef = useRef(false);

  // 快照
  const [snapshotVisible, setSnapshotVisible] = useState(false);
  const [currentSnapshotId, setCurrentSnapshotId] = useState('');
  const snapshotIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // Toast
  const [toasts, setToasts] = useState<ToastMessage[]>([]);
  const toastIdRef = useRef(0);

  // 结束确认
  const [showEndConfirm, setShowEndConfirm] = useState(false);

  // ─── AI 推断 / 探测 / 摘要 ────────────────────────
  const [inferences, setInferences] = useState<AIInference[]>([]);
  const [currentProbe, setCurrentProbe] = useState<AIProbe | null>(null);
  const [sessionSummary, setSessionSummary] = useState<SessionSummary | null>(null);
  const [showSummary, setShowSummary] = useState(false);
  const [isInferenceExpanded, setIsInferenceExpanded] = useState(true);
  const inferencePollRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const probePollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // ─── 步骤引导（双栏布局）────────────────────────
  const [currentStep, setCurrentStep] = useState(0);
  const [gameSteps] = useState<GameStep[]>(MOCK_GAME_STEPS);
  const [isWideScreen, setIsWideScreen] = useState(
    typeof window !== 'undefined' ? window.innerWidth >= 768 : false,
  );

  // ─── 初始化会话 ──────────────────────────────────

  useEffect(() => {
    const initSession = async () => {
      const config = await startGameSession({
        child_id: childId,
        game_type: gameType,
        game_name: gameName,
        planned_duration_minutes: plannedDuration,
      });
      setSessionConfig(config);
      setFixedButtons(config.fixed_buttons);
      setDynamicButtons(config.dynamic_buttons);
      setIsSessionActive(true);
    };
    initSession();

    return () => {
      if (snapshotIntervalRef.current) clearInterval(snapshotIntervalRef.current);
      if (inferencePollRef.current) clearInterval(inferencePollRef.current);
      if (probePollRef.current) clearInterval(probePollRef.current);
    };
  }, [childId, gameType, gameName, plannedDuration]);

  // ─── 监听窗口尺寸切换单/双栏 ─────────────────────

  useEffect(() => {
    const handleResize = () => setIsWideScreen(window.innerWidth >= 768);
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // ─── 计时器 ──────────────────────────────────────

  useEffect(() => {
    if (!isSessionActive) return;
    const timer = setInterval(() => setElapsedSeconds(s => s + 1), 1000);
    return () => clearInterval(timer);
  }, [isSessionActive]);

  // ─── 定时快照触发 ─────────────────────────────────

  useEffect(() => {
    if (!isSessionActive || !sessionConfig) return;

    // 每3分钟弹出一次快照卡片
    const SNAPSHOT_INTERVAL_MS = 3 * 60 * 1000;
    snapshotIntervalRef.current = setInterval(() => {
      if (!snapshotVisible) {
        setCurrentSnapshotId(`snap_${Date.now()}`);
        setSnapshotVisible(true);
      }
    }, SNAPSHOT_INTERVAL_MS);

    return () => {
      if (snapshotIntervalRef.current) clearInterval(snapshotIntervalRef.current);
    };
  }, [isSessionActive, sessionConfig, snapshotVisible]);

  // ─── AI 推断轮询（每 10s）─────────────────────────

  useEffect(() => {
    if (!isSessionActive || !sessionConfig) return;

    const fetchInferences = async () => {
      const list = await getInferences(sessionConfig.session_id);
      setInferences(list);
    };

    fetchInferences();
    inferencePollRef.current = setInterval(fetchInferences, INFERENCE_POLL_INTERVAL);

    return () => {
      if (inferencePollRef.current) clearInterval(inferencePollRef.current);
    };
  }, [isSessionActive, sessionConfig]);

  // ─── AI 探测轮询（每 15s）─────────────────────────

  useEffect(() => {
    if (!isSessionActive || !sessionConfig) return;

    const fetchProbe = async () => {
      // 已有展示中的 probe 时，不主动覆盖（避免打断用户思考）
      if (currentProbe) return;
      const probe = await getCurrentProbe(sessionConfig.session_id);
      if (probe) setCurrentProbe(probe);
    };

    fetchProbe();
    probePollRef.current = setInterval(fetchProbe, PROBE_POLL_INTERVAL);

    return () => {
      if (probePollRef.current) clearInterval(probePollRef.current);
    };
  }, [isSessionActive, sessionConfig, currentProbe]);

  // ─── Toast 管理 ───────────────────────────────────

  const showToast = useCallback((text: string, canUndo = false) => {
    const id = ++toastIdRef.current;
    setToasts(prev => [...prev, { id, text, canUndo }]);
    setTimeout(() => {
      setToasts(prev => prev.filter(t => t.id !== id));
    }, canUndo ? 3000 : 1500);
  }, []);

  // ─── 行为记录 ─────────────────────────────────────

  const handleRecordBehavior = useCallback(async (button: ButtonConfig, detail?: string) => {
    if (!sessionConfig) return;

    if (navigator.vibrate) navigator.vibrate(50);

    const event = {
      session_id: sessionConfig.session_id,
      game_type: sessionConfig.game_type,
      event_type: button.id,
      detail: detail || button.label,
      valence: button.valence,
      source: 'parent_click' as const,
    };

    await recordBehaviorEvent(event);
    setEventCount(c => c + 1);
    showToast(`✓ 已记录：${detail || button.label}`, true);

    setLongPressMenu(null);
  }, [sessionConfig, showToast]);

  // ─── 长按逻辑 ─────────────────────────────────────

  const handlePointerDown = useCallback((button: ButtonConfig, e: React.PointerEvent) => {
    longPressTriggeredRef.current = false;
    if (button.sub_options && button.sub_options.length > 0) {
      longPressTimerRef.current = setTimeout(() => {
        longPressTriggeredRef.current = true;
        if (navigator.vibrate) navigator.vibrate(30);
        const rect = (e.target as HTMLElement).getBoundingClientRect();
        setLongPressMenu({ button, x: rect.left, y: rect.top });
      }, 500);
    }
  }, []);

  const handlePointerUp = useCallback((button: ButtonConfig) => {
    if (longPressTimerRef.current) {
      clearTimeout(longPressTimerRef.current);
      longPressTimerRef.current = null;
    }
    if (!longPressTriggeredRef.current) {
      handleRecordBehavior(button);
    }
  }, [handleRecordBehavior]);

  const handlePointerLeave = useCallback(() => {
    if (longPressTimerRef.current) {
      clearTimeout(longPressTimerRef.current);
      longPressTimerRef.current = null;
    }
  }, []);

  // ─── 快照回调 ─────────────────────────────────────

  const handleSnapshotRespond = useCallback(async (snapshotId: string, response: string) => {
    if (!sessionConfig) return;
    setSnapshotVisible(false);
    await submitSnapshotResponse({
      session_id: sessionConfig.session_id,
      snapshot_id: snapshotId,
      response,
    });
    setEventCount(c => c + 1);
    showToast(`✓ 快照已记录`);
  }, [sessionConfig, showToast]);

  const handleSnapshotSkip = useCallback((_snapshotId: string) => {
    setSnapshotVisible(false);
  }, []);

  const handleSnapshotTimeout = useCallback((_snapshotId: string) => {
    setSnapshotVisible(false);
  }, []);

  // ─── 添加自定义按钮 ───────────────────────────────

  const handleAddCustomButton = useCallback((label: string) => {
    const newBtn: ButtonConfig = {
      id: `custom_${Date.now()}`,
      label,
      icon: '🏷️',
      valence: 0.5,
    };
    setDynamicButtons(prev => [...prev, newBtn]);
    showToast(`✓ 已添加按钮：${label}`);
  }, [showToast]);

  // ─── AI 推断确认 / 否定 ────────────────────────────

  const handleConfirmInference = useCallback(async (id: string, confirmed: boolean) => {
    // 乐观更新
    setInferences(prev =>
      prev.map(inf => (inf.id === id ? { ...inf, is_confirmed: confirmed } : inf)),
    );
    await apiConfirmInference(id, confirmed);
    showToast(confirmed ? '✓ 已确认推断' : '✗ 已否定推断');
  }, [showToast]);

  // ─── AI 探测响应 ──────────────────────────────────

  const handleRespondProbe = useCallback(async (probeId: string, option: string) => {
    // 立即关闭卡片，避免家长重复点击
    setCurrentProbe(null);
    if (option === '__skip__') {
      // 仅前端关闭，不上报
      return;
    }
    await apiRespondToProbe(probeId, option);
    setEventCount(c => c + 1);
    showToast(`✓ 已回应：${option}`);
  }, [showToast]);

  const handleDismissProbe = useCallback(() => {
    setCurrentProbe(null);
  }, []);

  // ─── 结束会话 → 拉取摘要 → 显示 modal ───────────────

  const handleRequestEnd = useCallback(async () => {
    if (!sessionConfig) return;
    setShowEndConfirm(false);
    setIsSessionActive(false);

    const summary = await completeSessionWithSummary(sessionConfig.session_id);
    setSessionSummary(summary);
    setShowSummary(true);
  }, [sessionConfig]);

  const handleSummarySave = useCallback(async (notes: string) => {
    if (!sessionConfig) return;
    // 触发后端落库 / 写记忆（兼容旧版接口）
    if (notes && notes.trim()) {
      // 把家长备注作为一条特殊事件附加（非阻塞）
      await recordBehaviorEvent({
        session_id: sessionConfig.session_id,
        game_type: sessionConfig.game_type,
        event_type: 'parent_note',
        detail: notes.trim(),
        valence: 0,
        source: 'parent_click',
      });
    }
    await completeGameSession(sessionConfig.session_id);
    setShowSummary(false);
    onComplete?.(sessionConfig.session_id);
  }, [sessionConfig, onComplete]);

  const handleSummaryContinue = useCallback(() => {
    // "继续记录" → 关闭 modal，恢复会话
    setShowSummary(false);
    setIsSessionActive(true);
  }, []);

  // ─── 格式化时间 ───────────────────────────────────

  const formatElapsed = (seconds: number) => {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  };

  const aiInferCount = inferences.length;
  const unconfirmedInferences = inferences.filter(i => i.is_confirmed === null);

  // ─── 公共子区块（单/双栏共享）─────────────────────

  // 记录区核心内容：快照、AI 探测、推断时间线、空态占位
  const recordingContent = (
    <>
      {/* 快照卡片（顶部浮层）*/}
      <SnapshotCard
        visible={snapshotVisible}
        snapshotId={currentSnapshotId}
        countdownSeconds={15}
        onRespond={handleSnapshotRespond}
        onSkip={handleSnapshotSkip}
        onTimeout={handleSnapshotTimeout}
      />

      {/* AI 探测卡片 — 当前有问题待回答时显示 */}
      <AnimatePresence>
        {currentProbe && (
          <motion.div
            key={currentProbe.id}
            initial={{ opacity: 0, y: -8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
          >
            <AIProbeCard
              probe={currentProbe}
              onRespond={handleRespondProbe}
              onDismiss={handleDismissProbe}
            />
          </motion.div>
        )}
      </AnimatePresence>

      {/* AI 推断时间线 — 折叠面板，置于快照之上、按钮区之上 */}
      {sessionConfig && (
        <InferenceTimeline
          sessionId={sessionConfig.session_id}
          inferences={inferences}
          onConfirm={handleConfirmInference}
          isExpanded={isInferenceExpanded}
          onToggle={() => setIsInferenceExpanded(v => !v)}
        />
      )}

      {/* 占位说明 — 仅在尚无任何 AI 输出时显示，避免空白 */}
      {inferences.length === 0 && !currentProbe && (
        <div className="text-center py-10 text-gray-300">
          <BrainCircuit className="w-10 h-10 mx-auto mb-2 opacity-30" />
          <p className="text-xs font-medium">AI 正在留意孩子的细微反应…</p>
          <p className="text-[10px] mt-1">每记录一次行为，AI 会更接近真实模式</p>
        </div>
      )}
    </>
  );

  // 双栏模式下，动态按钮来自步骤映射
  const contextButtons = isWideScreen && gameSteps.length > 0
    ? (STEP_CONTEXT_BUTTONS[currentStep] || []) as ButtonConfig[]
    : dynamicButtons;

  // 底部按钮区：动态按钮 + 常驻按钮
  const buttonsBar = (
    <div className="bg-white/95 backdrop-blur-xl border-t border-gray-100 pb-safe">
      {/* 动态按钮区 */}
      <div className="pt-3 pb-2 border-b border-gray-50">
        <div className="flex items-center px-4 mb-2">
          {isWideScreen && gameSteps.length > 0 ? (
            <span style={{ fontSize: '12px', color: '#6b7280', display: 'flex', alignItems: 'center', gap: '4px' }}>
              <span>🧠</span>
              <span>基于「{gameSteps[currentStep]?.stepTitle}」智能推荐</span>
            </span>
          ) : (
            <span className="text-[10px] font-bold text-gray-400 tracking-wider uppercase">上下文按钮</span>
          )}
        </div>
        <DynamicButtonGroup
          buttons={contextButtons}
          onButtonClick={handleRecordBehavior}
          onAddCustomButton={handleAddCustomButton}
        />
      </div>

      {/* 常驻按钮区 */}
      <div className="px-4 py-4">
        <div className="flex justify-around items-center">
          {fixedButtons.map((btn) => (
            <motion.button
              key={btn.id}
              whileTap={{ scale: 0.9 }}
              onPointerDown={(e) => handlePointerDown(btn, e)}
              onPointerUp={() => handlePointerUp(btn)}
              onPointerLeave={handlePointerLeave}
              className="flex flex-col items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-gray-50 to-gray-100 border border-gray-200 shadow-sm active:shadow-inner transition-all select-none touch-none"
            >
              <span className="text-2xl leading-none">{btn.icon}</span>
              <span className="text-[10px] font-bold text-gray-600 mt-1 leading-none">{btn.label}</span>
            </motion.button>
          ))}
        </div>
      </div>
    </div>
  );

  // 浮层集合：长按二级菜单、Toast、结束确认、会话摘要 Modal
  const overlays = (
    <>
      {/* 长按二级选项弹出 */}
      <AnimatePresence>
        {longPressMenu && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9, y: 10 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.9, y: 10 }}
            transition={{ duration: 0.15 }}
            className="fixed inset-0 z-50"
            onClick={() => setLongPressMenu(null)}
          >
            <div className="absolute inset-0 bg-black/20" />
            <div
              className="absolute bottom-32 left-4 right-4 bg-white rounded-3xl shadow-2xl p-5 border border-gray-100"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex items-center space-x-2 mb-4">
                <span className="text-xl">{longPressMenu.button.icon}</span>
                <span className="font-bold text-gray-800">{longPressMenu.button.label}</span>
                <span className="text-xs text-gray-400 ml-auto">选择具体行为</span>
              </div>
              <div className="grid grid-cols-1 gap-2">
                {longPressMenu.button.sub_options?.map((option, idx) => (
                  <motion.button
                    key={idx}
                    whileTap={{ scale: 0.97 }}
                    onClick={() => handleRecordBehavior(longPressMenu.button, option)}
                    className="w-full text-left px-4 py-3 rounded-xl bg-gray-50 hover:bg-primary/5 border border-gray-100 hover:border-primary/20 text-sm font-medium text-gray-700 transition-all min-h-[48px]"
                  >
                    {option}
                  </motion.button>
                ))}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Toast 区域 */}
      <div className="fixed top-16 right-4 z-50 space-y-2 pointer-events-none">
        <AnimatePresence>
          {toasts.map((toast) => (
            <motion.div
              key={toast.id}
              initial={{ opacity: 0, x: 40, scale: 0.9 }}
              animate={{ opacity: 1, x: 0, scale: 1 }}
              exit={{ opacity: 0, x: 40, scale: 0.9 }}
              className="bg-gray-900/90 backdrop-blur-md text-white text-xs font-medium px-4 py-2.5 rounded-xl shadow-lg pointer-events-auto"
            >
              {toast.text}
            </motion.div>
          ))}
        </AnimatePresence>
      </div>

      {/* 结束确认弹窗（轻量二次确认）*/}
      <AnimatePresence>
        {showEndConfirm && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 flex items-center justify-center px-6"
          >
            <div className="absolute inset-0 bg-black/40" onClick={() => setShowEndConfirm(false)} />
            <motion.div
              initial={{ scale: 0.9, y: 20 }}
              animate={{ scale: 1, y: 0 }}
              exit={{ scale: 0.9, y: 20 }}
              className="relative bg-white rounded-3xl p-6 shadow-2xl w-full max-w-sm"
            >
              <h3 className="text-lg font-bold text-gray-800 mb-2">结束本次记录？</h3>
              <p className="text-sm text-gray-500 mb-6">
                已记录 {eventCount} 个行为事件，游戏时长 {formatElapsed(elapsedSeconds)}
              </p>
              <div className="flex space-x-3">
                <button
                  onClick={() => setShowEndConfirm(false)}
                  className="flex-1 py-3 rounded-xl bg-gray-100 text-gray-700 font-bold text-sm hover:bg-gray-200 transition"
                >
                  继续记录
                </button>
                <button
                  onClick={handleRequestEnd}
                  className="flex-1 py-3 rounded-xl bg-red-500 text-white font-bold text-sm hover:bg-red-600 transition"
                >
                  结束并查看摘要
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* 会话摘要 Modal — 结束后展示，包含 AI 推断待确认 */}
      {sessionConfig && (
        <SessionSummaryModal
          isOpen={showSummary}
          sessionId={sessionConfig.session_id}
          summary={sessionSummary}
          unconfirmedInferences={unconfirmedInferences}
          onConfirmInference={handleConfirmInference}
          onSave={handleSummarySave}
          onContinue={handleSummaryContinue}
        />
      )}
    </>
  );

  // ─── 渲染：双栏模式（≥768px 且有步骤）────────────

  if (isWideScreen && gameSteps.length > 0) {
    return (
      <div
        style={{
          display: 'flex',
          flexDirection: 'row',
          height: '100vh',
          width: '100vw',
          maxWidth: 'none',
          background: '#f9fafb',
          // 使用 fixed + inset:0 突破 App 根容器的 max-w-md (448px) 限制
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          zIndex: 40,
        }}
      >
        {/* 左栏 40% — 游戏步骤引导 */}
        <div
          style={{
            width: '40%',
            borderRight: '1px solid #e5e7eb',
            height: '100%',
            display: 'flex',
            flexDirection: 'column',
            minWidth: 0,
          }}
        >
          <StepGuidePanel
            steps={gameSteps}
            currentStep={currentStep}
            onStepChange={setCurrentStep}
            gameTitle="积木高塔轮流堆"
            elapsedTime={formatElapsed(elapsedSeconds)}
            totalEvents={eventCount}
          />
        </div>

        {/* 右栏 60% — 行为记录区 */}
        <div
          style={{
            width: '60%',
            height: '100%',
            display: 'flex',
            flexDirection: 'column',
            minWidth: 0,
            background: '#f9fafb',
          }}
        >
          {/* 右栏顶部：返回 + AI 计数 + 结束按钮（标题/计时已移至左栏） */}
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              padding: '10px 16px',
              borderBottom: '1px solid #e5e7eb',
              background: 'rgba(255,255,255,0.92)',
              backdropFilter: 'blur(12px)',
              flexShrink: 0,
              zIndex: 10,
            }}
          >
            <div className="flex items-center space-x-3">
              <button
                onClick={onBack}
                className="p-1 rounded-lg hover:bg-gray-100 transition"
                aria-label="返回"
              >
                <ChevronLeft className="w-5 h-5 text-gray-600" />
              </button>
              <span className="flex items-center text-xs text-purple-500 font-semibold">
                <BrainCircuit className="w-3.5 h-3.5 mr-1" />
                {aiInferCount} AI 推断
              </span>
              <span className="flex items-center text-xs text-gray-500">
                <Activity className="w-3.5 h-3.5 mr-1" />
                {eventCount} 事件
              </span>
            </div>
            <button
              onClick={() => setShowEndConfirm(true)}
              className="flex items-center space-x-1 px-3 py-1.5 rounded-full bg-red-50 text-red-600 text-xs font-bold hover:bg-red-100 transition min-h-[36px]"
            >
              <Square className="w-3 h-3" />
              <span>结束</span>
            </button>
          </div>

          {/* 右栏中部：可滚动的记录内容 */}
          <div
            style={{
              flex: 1,
              overflowY: 'auto',
              padding: '16px',
              display: 'flex',
              flexDirection: 'column',
              gap: 12,
              minHeight: 0,
            }}
            className="no-scrollbar"
          >
            {recordingContent}
          </div>

          {/* 右栏底部：动态 + 常驻按钮区 */}
          {buttonsBar}
        </div>

        {/* 共享浮层 */}
        {overlays}
      </div>
    );
  }

  // ─── 渲染：窄屏单栏模式（保留原有完整布局）────────

  return (
    <div className="h-full flex flex-col bg-gray-50 relative overflow-hidden">
      {/* 顶部信息栏 */}
      <div className="bg-white/90 backdrop-blur-md border-b border-gray-100 px-4 py-3 flex items-center justify-between z-30 sticky top-0">
        <div className="flex items-center space-x-3">
          <button onClick={onBack} className="p-1 rounded-lg hover:bg-gray-100 transition">
            <ChevronLeft className="w-5 h-5 text-gray-600" />
          </button>
          <div>
            <h1 className="text-sm font-bold text-gray-800 leading-tight">{gameName}</h1>
            <div className="flex items-center space-x-3 mt-0.5">
              <span className="flex items-center text-xs text-primary font-bold">
                <Timer className="w-3 h-3 mr-0.5" />
                {formatElapsed(elapsedSeconds)}
              </span>
              <span className="flex items-center text-xs text-gray-500">
                <Activity className="w-3 h-3 mr-0.5" />
                {eventCount} 事件
              </span>
              <span className="flex items-center text-xs text-purple-500">
                <BrainCircuit className="w-3 h-3 mr-0.5" />
                {aiInferCount} AI
              </span>
            </div>
          </div>
        </div>
        <button
          onClick={() => setShowEndConfirm(true)}
          className="flex items-center space-x-1 px-3 py-1.5 rounded-full bg-red-50 text-red-600 text-xs font-bold hover:bg-red-100 transition min-h-[36px]"
        >
          <Square className="w-3 h-3" />
          <span>结束</span>
        </button>
      </div>

      {/* 中部内容区 */}
      <div className="flex-1 relative overflow-y-auto no-scrollbar px-4 py-4 space-y-3">
        {recordingContent}
      </div>

      {/* 底部操作区 */}
      {buttonsBar}

      {/* 共享浮层 */}
      {overlays}
    </div>
  );
};

export default GameRecordingPage;
