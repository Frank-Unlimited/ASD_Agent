import React, { useState } from 'react';
import {
  CalendarIcon,
  ChevronLeft,
  ChevronRight,
  ChevronUp,
  ChevronDown,
  Package,
  Gamepad2,
  Activity,
  X
} from 'lucide-react';
import { BehaviorAnalysis, FloorGame, Page } from '../types';
import { behaviorStorageService } from '../services/behaviorStorage';
import { floorGameStorageService } from '../services/floorGameStorage';
import { getDimensionConfig } from '../utils/helpers';

// 自定义滚动条样式
const scrollbarStyles = `
  .custom-scrollbar::-webkit-scrollbar {
    width: 8px;
  }
  
  .custom-scrollbar::-webkit-scrollbar-track {
    background: linear-gradient(to bottom, #f3f4f6, #e5e7eb);
    border-radius: 10px;
  }
  
  .custom-scrollbar::-webkit-scrollbar-thumb {
    background: linear-gradient(to bottom, #3b82f6, #8b5cf6);
    border-radius: 10px;
    transition: all 0.3s ease;
  }
  
  .custom-scrollbar::-webkit-scrollbar-thumb:hover {
    background: linear-gradient(to bottom, #2563eb, #7c3aed);
    box-shadow: 0 0 6px rgba(59, 130, 246, 0.5);
  }
  
  /* Firefox */
  .custom-scrollbar {
    scrollbar-width: thin;
    scrollbar-color: #3b82f6 #f3f4f6;
  }
`;

export const PageCalendar = ({ navigateTo, onStartGame }: { 
  navigateTo: (p: Page) => void, 
  onStartGame: (gameId: string) => void 
}) => {
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [expandedMonth, setExpandedMonth] = useState(false);
  const [selectedBehavior, setSelectedBehavior] = useState<BehaviorAnalysis | null>(null);
  const [showBehaviorDetail, setShowBehaviorDetail] = useState(false);
  
  // 滑动相关的 state
  const [touchStart, setTouchStart] = useState<number | null>(null);
  const [touchEnd, setTouchEnd] = useState<number | null>(null);
  const [isSwipeAnimating, setIsSwipeAnimating] = useState(false);
  const [swipeDirection, setSwipeDirection] = useState<'left' | 'right' | null>(null);
  const [dragOffset, setDragOffset] = useState(0); // 实时拖拽偏移量
  const [nextWeekDates, setNextWeekDates] = useState<Date[]>([]); // 下一周的日期
  const [prevWeekDates, setPrevWeekDates] = useState<Date[]>([]); // 上一周的日期
  const [showNextWeek, setShowNextWeek] = useState(false); // 是否显示下一周
  const [showPrevWeek, setShowPrevWeek] = useState(false); // 是否显示上一周
  
  // 时间轴容器的引用
  const timelineRef = React.useRef<HTMLDivElement>(null);
  
  // 最小滑动距离（像素）
  const minSwipeDistance = 50;
  
  // 触摸开始
  const onTouchStart = (e: React.TouchEvent) => {
    setTouchEnd(null);
    setTouchStart(e.targetTouches[0].clientX);
    setDragOffset(0);
    setShowNextWeek(false);
    setShowPrevWeek(false);
  };
  
  // 触摸移动
  const onTouchMove = (e: React.TouchEvent) => {
    if (touchStart === null) return;
    const currentTouch = e.targetTouches[0].clientX;
    setTouchEnd(currentTouch);
    // 实时更新拖拽偏移量，添加阻尼效果
    const offset = (currentTouch - touchStart) * 0.3;
    setDragOffset(offset);
    
    // 根据拖拽方向显示对应的周
    if (offset < 0) {
      setShowNextWeek(true);
      setShowPrevWeek(false);
    } else if (offset > 0) {
      setShowPrevWeek(true);
      setShowNextWeek(false);
    }
  };
  
  // 触摸结束
  const onTouchEnd = () => {
    if (!touchStart || !touchEnd) {
      setDragOffset(0);
      setShowNextWeek(false);
      setShowPrevWeek(false);
      setTouchStart(null);
      setTouchEnd(null);
      return;
    }
    
    const distance = touchStart - touchEnd;
    const isLeftSwipe = distance > minSwipeDistance;
    const isRightSwipe = distance < -minSwipeDistance;
    
    if (isLeftSwipe) {
      // 向左滑动 - 下一周
      setSwipeDirection('left');
      setIsSwipeAnimating(true);
      setTimeout(() => {
        const newDate = new Date(selectedDate);
        newDate.setDate(newDate.getDate() + 7);
        setSelectedDate(newDate);
        setIsSwipeAnimating(false);
        setSwipeDirection(null);
        setDragOffset(0);
        setShowNextWeek(false);
        setShowPrevWeek(false);
      }, 300);
    } else if (isRightSwipe) {
      // 向右滑动 - 上一周
      setSwipeDirection('right');
      setIsSwipeAnimating(true);
      setTimeout(() => {
        const newDate = new Date(selectedDate);
        newDate.setDate(newDate.getDate() - 7);
        setSelectedDate(newDate);
        setIsSwipeAnimating(false);
        setSwipeDirection(null);
        setDragOffset(0);
        setShowNextWeek(false);
        setShowPrevWeek(false);
      }, 300);
    } else {
      // 回弹 - 重置偏移量，但保持显示状态直到动画结束
      setDragOffset(0);
      setTimeout(() => {
        setShowNextWeek(false);
        setShowPrevWeek(false);
      }, 300);
    }
    
    setTouchStart(null);
    setTouchEnd(null);
  };
  
  // 鼠标拖拽开始
  const onMouseDown = (e: React.MouseEvent) => {
    setTouchEnd(null);
    setTouchStart(e.clientX);
    setDragOffset(0);
    setShowNextWeek(false);
    setShowPrevWeek(false);
  };
  
  // 鼠标拖拽移动
  const onMouseMove = (e: React.MouseEvent) => {
    if (touchStart === null) return;
    const currentX = e.clientX;
    setTouchEnd(currentX);
    // 实时更新拖拽偏移量，添加阻尼效果
    const offset = (currentX - touchStart) * 0.3;
    setDragOffset(offset);
    
    // 根据拖拽方向显示对应的周
    if (offset < 0) {
      setShowNextWeek(true);
      setShowPrevWeek(false);
    } else if (offset > 0) {
      setShowPrevWeek(true);
      setShowNextWeek(false);
    }
  };
  
  // 鼠标拖拽结束
  const onMouseUp = () => {
    if (!touchStart || !touchEnd) {
      setDragOffset(0);
      setShowNextWeek(false);
      setShowPrevWeek(false);
      setTouchStart(null);
      setTouchEnd(null);
      return;
    }
    
    const distance = touchStart - touchEnd;
    const isLeftSwipe = distance > minSwipeDistance;
    const isRightSwipe = distance < -minSwipeDistance;
    
    if (isLeftSwipe) {
      // 向左滑动 - 下一周
      setSwipeDirection('left');
      setIsSwipeAnimating(true);
      setTimeout(() => {
        const newDate = new Date(selectedDate);
        newDate.setDate(newDate.getDate() + 7);
        setSelectedDate(newDate);
        setIsSwipeAnimating(false);
        setSwipeDirection(null);
        setDragOffset(0);
        setShowNextWeek(false);
        setShowPrevWeek(false);
      }, 300);
    } else if (isRightSwipe) {
      // 向右滑动 - 上一周
      setSwipeDirection('right');
      setIsSwipeAnimating(true);
      setTimeout(() => {
        const newDate = new Date(selectedDate);
        newDate.setDate(newDate.getDate() - 7);
        setSelectedDate(newDate);
        setIsSwipeAnimating(false);
        setSwipeDirection(null);
        setDragOffset(0);
        setShowNextWeek(false);
        setShowPrevWeek(false);
      }, 300);
    } else {
      // 回弹 - 重置偏移量，但保持显示状态直到动画结束
      setDragOffset(0);
      setTimeout(() => {
        setShowNextWeek(false);
        setShowPrevWeek(false);
      }, 300);
    }
    
    setTouchStart(null);
    setTouchEnd(null);
  };
  
  // 加载真实数据
  const behaviors = behaviorStorageService.getAllBehaviors();
  const games = floorGameStorageService.getAllGames();
  
  // 当选中日期改变时，滚动到顶部
  React.useEffect(() => {
    if (timelineRef.current) {
      timelineRef.current.scrollTop = 0;
    }
  }, [selectedDate]);
  
  // 工具函数：判断是否是同一天
  const isSameDay = (date1: Date, date2: Date) => {
    return date1.getFullYear() === date2.getFullYear() &&
           date1.getMonth() === date2.getMonth() &&
           date1.getDate() === date2.getDate();
  };
  
  // 工具函数：获取本周日期（周日到周六）
  const getWeekDates = (date: Date) => {
    const day = date.getDay();
    const diff = date.getDate() - day;
    const sunday = new Date(date.setDate(diff));
    const weekDates = [];
    for (let i = 0; i < 7; i++) {
      const d = new Date(sunday);
      d.setDate(sunday.getDate() + i);
      weekDates.push(d);
    }
    return weekDates;
  };
  
  // 工具函数：获取当月所有日期
  const getMonthDates = (date: Date) => {
    const year = date.getFullYear();
    const month = date.getMonth();
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const dates = [];
    
    // 补充上月末尾的日期
    const firstDayOfWeek = firstDay.getDay();
    for (let i = firstDayOfWeek - 1; i >= 0; i--) {
      const d = new Date(firstDay);
      d.setDate(firstDay.getDate() - i - 1);
      dates.push(d);
    }
    
    // 当月日期
    for (let i = 1; i <= lastDay.getDate(); i++) {
      dates.push(new Date(year, month, i));
    }
    
    // 补充下月开头的日期
    const remaining = 42 - dates.length;
    for (let i = 1; i <= remaining; i++) {
      dates.push(new Date(year, month + 1, i));
    }
    
    return dates;
  };
  
  // 获取选中日期的事件
  const getDailyEvents = () => {
    const events: any[] = [];
    
    // 筛选当天的行为记录
    behaviors.forEach(behavior => {
      if (behavior.timestamp && isSameDay(new Date(behavior.timestamp), selectedDate)) {
        events.push({
          id: behavior.id || `behavior_${Date.now()}`,
          type: 'behavior',
          time: new Date(behavior.timestamp),
          data: behavior
        });
      }
    });
    
    // 筛选当天已完成的游戏
    games.forEach(game => {
      if (game.status === 'completed' && game.dtstart) {
        const gameDate = new Date(game.dtstart);
        if (isSameDay(gameDate, selectedDate)) {
          events.push({
            id: game.id,
            type: 'game',
            time: gameDate,
            endTime: game.dtend ? new Date(game.dtend) : null,
            data: game
          });
        }
      }
    });
    
    // 按时间排序
    return events.sort((a, b) => a.time.getTime() - b.time.getTime());
  };
  
  // 检查某天是否有事件
  const hasEventsOnDate = (date: Date) => {
    const hasBehavior = behaviors.some(b => 
      b.timestamp && isSameDay(new Date(b.timestamp), date)
    );
    const hasGame = games.some(g => 
      g.status === 'completed' && g.dtstart && isSameDay(new Date(g.dtstart), date)
    );
    return hasBehavior || hasGame;
  };
  
  const today = new Date();
  const weekDates = getWeekDates(new Date(selectedDate));
  const monthDates = getMonthDates(new Date(selectedDate));
  const dailyEvents = getDailyEvents();
  
  // 计算上一周和下一周的日期
  React.useEffect(() => {
    const nextWeekDate = new Date(selectedDate);
    nextWeekDate.setDate(nextWeekDate.getDate() + 7);
    setNextWeekDates(getWeekDates(nextWeekDate));
    
    const prevWeekDate = new Date(selectedDate);
    prevWeekDate.setDate(prevWeekDate.getDate() - 7);
    setPrevWeekDates(getWeekDates(prevWeekDate));
  }, [selectedDate]);
  
  // 格式化日期显示
  const formatDateHeader = (date: Date) => {
    const year = date.getFullYear();
    const month = date.getMonth() + 1;
    const day = date.getDate();
    const weekdays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六'];
    const weekday = weekdays[date.getDay()];
    return { year, month, day, weekday };
  };
  
  const headerInfo = formatDateHeader(selectedDate);
  
  return (
    <>
      {/* 注入自定义滚动条样式 */}
      <style>{scrollbarStyles}</style>
      
      <div className="h-full flex flex-col bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* 顶部日期栏 - 紧凑设计 */}
      <div className="sticky top-0 bg-white/80 backdrop-blur-lg z-10 px-4 py-3 border-b border-gray-200/50 shadow-sm">
        <div className="flex justify-between items-center">
          <div>
            <h2 className="text-2xl font-black text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600">
              {isSameDay(selectedDate, today) ? '今天' : `${headerInfo.month}月${headerInfo.day}日`}
            </h2>
            <p className="text-xs text-gray-500 font-medium mt-0.5">
              {headerInfo.year}年{headerInfo.month}月{headerInfo.day}日 {headerInfo.weekday}
            </p>
          </div>
          <div className="flex gap-2">
            {!isSameDay(selectedDate, today) && (
              <button 
                onClick={() => setSelectedDate(new Date())}
                className="px-3 py-1.5 text-xs font-bold text-white bg-gradient-to-r from-blue-500 to-blue-600 rounded-lg hover:from-blue-600 hover:to-blue-700 transition shadow-md hover:shadow-lg transform hover:scale-105"
              >
                回到今天
              </button>
            )}
            <button 
              onClick={() => setExpandedMonth(!expandedMonth)}
              className="p-2 rounded-lg hover:bg-gray-100 transition transform hover:scale-105 bg-white shadow-sm"
            >
              <Package className={`w-5 h-5 text-gray-600 transition-transform ${expandedMonth ? 'rotate-180' : ''}`} />
            </button>
          </div>
        </div>
      </div>
      
      {/* 周视图 - 简洁美化版 */}
      <div 
        className="bg-white/90 backdrop-blur-sm border-b border-gray-200/50 px-4 py-4 shadow-sm cursor-grab active:cursor-grabbing select-none overflow-hidden relative"
        onTouchStart={onTouchStart}
        onTouchMove={onTouchMove}
        onTouchEnd={onTouchEnd}
        onMouseDown={onMouseDown}
        onMouseMove={onMouseMove}
        onMouseUp={onMouseUp}
        onMouseLeave={onMouseUp}
      >
        <div 
          className={`${
            isSwipeAnimating 
              ? 'transition-all duration-400 ease-out' 
              : dragOffset !== 0
              ? 'transition-none'
              : 'transition-all duration-300 ease-out'
          }`}
          style={{
            transform: isSwipeAnimating
              ? swipeDirection === 'left'
                ? 'translateX(-120%) scale(0.9)'
                : swipeDirection === 'right'
                ? 'translateX(120%) scale(0.9)'
                : `translateX(${dragOffset}px) scale(${Math.max(0.95, 1 - Math.abs(dragOffset) / 800)})`
              : `translateX(${dragOffset}px) scale(${Math.max(0.95, 1 - Math.abs(dragOffset) / 800)})`,
            opacity: isSwipeAnimating 
              ? swipeDirection ? 0 : 1
              : Math.max(0.6, 1 - Math.abs(dragOffset) / 250)
          }}
        >
          <div className="grid grid-cols-7 gap-3">
            {['日', '一', '二', '三', '四', '五', '六'].map((day, i) => (
              <div key={i} className="text-center text-xs text-gray-500 font-bold mb-2 uppercase tracking-wider">
                {day}
              </div>
            ))}
            {weekDates.map((date, i) => {
              const isToday = isSameDay(date, today);
              const isSelected = isSameDay(date, selectedDate);
              const hasEvents = hasEventsOnDate(date);
              
              return (
                <div key={i} className="flex flex-col items-center">
                  <button
                    onClick={() => setSelectedDate(new Date(date))}
                    className={`w-10 h-10 rounded-xl flex items-center justify-center text-sm font-bold transition-all transform ${
                      isSelected 
                        ? 'bg-gradient-to-br from-blue-500 to-purple-600 text-white shadow-lg scale-110' 
                        : isToday
                        ? 'bg-blue-50 text-blue-600 ring-2 ring-blue-300'
                        : 'text-gray-700 hover:bg-gray-100 hover:scale-105'
                    }`}
                  >
                    {date.getDate()}
                  </button>
                  {isToday && !isSelected && (
                    <div className="w-7 h-1 rounded-full bg-gradient-to-r from-red-400 via-pink-500 to-red-400 mt-1.5 shadow-sm animate-pulse"></div>
                  )}
                  {hasEvents && !isToday && !isSelected && (
                    <div className="flex gap-1 mt-1.5">
                      <div className="w-1.5 h-1.5 rounded-full bg-gradient-to-br from-green-400 to-emerald-500 shadow-sm"></div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
        
        {/* 拖拽方向提示 */}
        {dragOffset !== 0 && !isSwipeAnimating && Math.abs(dragOffset) > 20 && (
          <div className={`absolute top-1/2 transform -translate-y-1/2 transition-all ${
            dragOffset < 0 ? 'right-4' : 'left-4'
          }`}>
            <div className={`w-10 h-10 rounded-full bg-gradient-to-br ${
              dragOffset < 0 
                ? 'from-blue-400 to-purple-500' 
                : 'from-purple-400 to-blue-500'
            } flex items-center justify-center shadow-lg animate-pulse`}>
              <ChevronRight className={`w-6 h-6 text-white ${
                dragOffset > 0 ? 'rotate-180' : ''
              }`} />
            </div>
          </div>
        )}
      </div>
      
      {/* 月历展开视图 - 紧凑设计 */}
      {expandedMonth && (
        <div className="bg-gradient-to-br from-gray-50 to-blue-50/30 border-b border-gray-200/50 px-4 py-3 animate-in slide-in-from-top shadow-inner">
          <div className="flex justify-between items-center mb-3">
            <div className="flex items-center gap-3">
              <h3 className="font-black text-base text-transparent bg-clip-text bg-gradient-to-r from-gray-700 to-gray-900">
                {selectedDate.getFullYear()}年 {selectedDate.getMonth() + 1}月
              </h3>
              {/* 年份切换按钮 - 紧凑设计 */}
              <div className="flex flex-col gap-0.5">
                <button
                  onClick={() => {
                    const newDate = new Date(selectedDate);
                    newDate.setFullYear(newDate.getFullYear() + 1);
                    setSelectedDate(newDate);
                  }}
                  className="group p-1 rounded-md bg-gradient-to-br from-blue-50 to-purple-50 hover:from-blue-100 hover:to-purple-100 transition-all shadow-sm hover:shadow-md transform hover:scale-110 border border-blue-100/50"
                  title="下一年"
                >
                  <ChevronUp className="w-3 h-3 text-blue-600 group-hover:text-purple-600 transition" />
                </button>
                <button
                  onClick={() => {
                    const newDate = new Date(selectedDate);
                    newDate.setFullYear(newDate.getFullYear() - 1);
                    setSelectedDate(newDate);
                  }}
                  className="group p-1 rounded-md bg-gradient-to-br from-blue-50 to-purple-50 hover:from-blue-100 hover:to-purple-100 transition-all shadow-sm hover:shadow-md transform hover:scale-110 border border-blue-100/50"
                  title="上一年"
                >
                  <ChevronDown className="w-3 h-3 text-blue-600 group-hover:text-purple-600 transition" />
                </button>
              </div>
            </div>
            {/* 月份切换按钮 - 紧凑设计 */}
            <div className="flex gap-1.5">
              <button
                onClick={() => {
                  const newDate = new Date(selectedDate);
                  newDate.setMonth(newDate.getMonth() - 1);
                  setSelectedDate(newDate);
                }}
                className="group p-2 rounded-lg bg-gradient-to-br from-white to-blue-50 hover:from-blue-50 hover:to-purple-50 transition-all shadow-md hover:shadow-lg transform hover:scale-110 border border-gray-200/50"
                title="上个月"
              >
                <ChevronLeft className="w-4 h-4 text-gray-600 group-hover:text-blue-600 transition" />
              </button>
              <button
                onClick={() => {
                  const newDate = new Date(selectedDate);
                  newDate.setMonth(newDate.getMonth() + 1);
                  setSelectedDate(newDate);
                }}
                className="group p-2 rounded-lg bg-gradient-to-br from-white to-blue-50 hover:from-blue-50 hover:to-purple-50 transition-all shadow-md hover:shadow-lg transform hover:scale-110 border border-gray-200/50"
                title="下个月"
              >
                <ChevronRight className="w-4 h-4 text-gray-600 group-hover:text-blue-600 transition" />
              </button>
            </div>
          </div>
          <div className="grid grid-cols-7 gap-1.5">
            {['日', '一', '二', '三', '四', '五', '六'].map((day, i) => (
              <div key={i} className="text-center text-xs text-gray-400 font-bold py-1.5 uppercase tracking-wider">
                {day}
              </div>
            ))}
            {monthDates.map((date, i) => {
              const isCurrentMonth = date.getMonth() === selectedDate.getMonth();
              const isToday = isSameDay(date, today);
              const isSelected = isSameDay(date, selectedDate);
              const hasEvents = hasEventsOnDate(date);
              
              return (
                <button
                  key={i}
                  onClick={() => {
                    setSelectedDate(new Date(date));
                    setExpandedMonth(false);
                  }}
                  className={`aspect-square rounded-lg flex flex-col items-center justify-center text-xs transition-all transform ${
                    isSelected
                      ? 'bg-gradient-to-br from-blue-500 to-purple-600 text-white font-bold shadow-lg scale-105'
                      : isToday
                      ? 'bg-gradient-to-br from-blue-50 to-purple-50 text-blue-600 font-bold ring-2 ring-blue-200'
                      : isCurrentMonth
                      ? 'text-gray-700 hover:bg-white/80 hover:shadow-md hover:scale-105 bg-white/40'
                      : 'text-gray-300 bg-white/20'
                  }`}
                >
                  <span>{date.getDate()}</span>
                  {hasEvents && (
                    <div className={`w-1 h-1 rounded-full mt-0.5 ${
                      isSelected ? 'bg-white' : 'bg-green-500 shadow-sm'
                    }`}></div>
                  )}
                </button>
              );
            })}
          </div>
        </div>
      )}
      
      {/* 时间轴视图 - 紧凑设计 */}
      <div ref={timelineRef} className="flex-1 overflow-y-auto custom-scrollbar">
        <div className="relative px-2 py-2">
          {Array.from({ length: 24 }).map((_, hour) => {
            const hourEvents = dailyEvents.filter(event => 
              event.time.getHours() === hour
            );
            
            return (
              <div key={hour} className="flex border-t border-gray-100/50 min-h-[48px] hover:bg-gray-50/30 transition">
                <div className="w-14 text-xs text-gray-400 font-bold p-2 flex-shrink-0">
                  {hour.toString().padStart(2, '0')}:00
                </div>
                <div className="flex-1 p-1.5 relative">
                  {hourEvents.length === 0 ? (
                    <div className="h-full flex items-center text-xs text-gray-300">
                      {/* 空时段 */}
                    </div>
                  ) : (
                    hourEvents.map(event => {
                      if (event.type === 'game') {
                        const game = event.data as FloorGame;
                        const duration = event.endTime 
                          ? Math.round((event.endTime.getTime() - event.time.getTime()) / (1000 * 60))
                          : 15;
                        
                        return (
                          <div
                            key={event.id}
                            onClick={() => onStartGame(game.id)}
                            className="mb-2 p-3 rounded-xl border-l-3 border-blue-500 bg-gradient-to-r from-blue-50 to-blue-50/50 cursor-pointer hover:from-blue-100 hover:to-blue-100/50 transition-all shadow-sm hover:shadow-md transform hover:scale-[1.01]"
                          >
                            <div className="flex justify-between items-start gap-2">
                              <div className="flex-1 min-w-0">
                                <div className="flex items-center flex-wrap gap-2 mb-1.5">
                                  <div className="flex items-center min-w-0">
                                    <div className="p-1 rounded-lg bg-blue-100 mr-1.5 flex-shrink-0">
                                      <Gamepad2 className="w-3.5 h-3.5 text-blue-600" />
                                    </div>
                                    <span className="font-bold text-sm text-blue-900 break-words">{game.gameTitle}</span>
                                  </div>
                                  <span className="text-xs font-bold text-blue-600 bg-blue-100 px-2 py-0.5 rounded-full flex-shrink-0">
                                    {duration}分钟
                                  </span>
                                </div>
                                <div className="text-xs text-gray-600 flex items-start">
                                  <span className="mr-1 flex-shrink-0">🎯</span>
                                  <span className="break-words">{game.goal}</span>
                                </div>
                                {game.evaluation && (
                                  <div className="flex items-center gap-2 mt-1.5">
                                    <div className="text-xs font-bold text-yellow-600 bg-yellow-50 px-2 py-0.5 rounded-full flex items-center">
                                      ⭐ {game.evaluation.score}分
                                    </div>
                                  </div>
                                )}
                              </div>
                              <div className="text-xs font-bold text-gray-500 whitespace-nowrap bg-white px-1.5 py-0.5 rounded-lg flex-shrink-0">
                                {event.time.getHours().toString().padStart(2, '0')}:
                                {event.time.getMinutes().toString().padStart(2, '0')}
                              </div>
                            </div>
                          </div>
                        );
                      } else {
                        const behavior = event.data as BehaviorAnalysis;
                        return (
                          <div
                            key={event.id}
                            onClick={() => {
                              setSelectedBehavior(behavior);
                              setShowBehaviorDetail(true);
                            }}
                            className="mb-1.5 p-2 rounded-lg border-l-2 border-green-500 bg-gradient-to-r from-green-50 to-green-50/30 cursor-pointer hover:from-green-100 hover:to-green-100/30 transition-all shadow-sm hover:shadow-md transform hover:scale-[1.01]"
                          >
                            <div className="flex justify-between items-center gap-2">
                              <div className="flex items-center flex-1 min-w-0">
                                <div className="p-0.5 rounded bg-green-100 mr-1.5 flex-shrink-0">
                                  <Activity className="w-3 h-3 text-green-600" />
                                </div>
                                <span className="text-xs font-medium text-green-900 truncate">{behavior.behavior}</span>
                              </div>
                              <div className="text-xs font-bold text-gray-500 whitespace-nowrap bg-white px-1.5 py-0.5 rounded">
                                {event.time.getHours().toString().padStart(2, '0')}:
                                {event.time.getMinutes().toString().padStart(2, '0')}
                              </div>
                            </div>
                          </div>
                        );
                      }
                    })
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>
      
      {/* 行为详情模态框 - 紧凑设计 */}
      {showBehaviorDetail && selectedBehavior && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4 animate-in fade-in">
          <div className="bg-white rounded-2xl max-w-md w-full max-h-[80vh] overflow-hidden shadow-2xl animate-in slide-in-from-bottom-4">
            <div className="sticky top-0 bg-gradient-to-r from-blue-500 to-purple-600 p-4 rounded-t-2xl z-10">
              <div className="flex justify-between items-center">
                <h3 className="text-lg font-black text-white">行为详情</h3>
                <button 
                  onClick={() => setShowBehaviorDetail(false)}
                  className="p-1.5 rounded-lg bg-white/20 hover:bg-white/30 transition backdrop-blur-sm"
                >
                  <X className="w-4 h-4 text-white" />
                </button>
              </div>
            </div>
            <div className="p-4 overflow-y-auto max-h-[calc(80vh-72px)] custom-scrollbar">
              
              {/* 行为描述 */}
              <div className="mb-4 p-3 bg-gradient-to-br from-blue-50 to-purple-50 rounded-xl border border-blue-100 shadow-sm">
                <div className="flex items-start mb-2">
                  <div className="p-1.5 rounded-lg bg-blue-100 mr-2">
                    <Activity className="w-4 h-4 text-blue-600" />
                  </div>
                  <h4 className="text-xs font-black text-blue-800 mt-1">行为描述</h4>
                </div>
                <p className="text-sm text-gray-800 leading-relaxed font-medium">{selectedBehavior.behavior}</p>
              </div>
              
              {/* 兴趣维度分析 */}
              <div className="mb-4 p-3 bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl border border-green-100 shadow-sm">
                <div className="flex items-center mb-3">
                  <div className="p-1.5 rounded-lg bg-green-100 mr-2">
                    <Package className="w-4 h-4 text-green-600" />
                  </div>
                  <h4 className="text-xs font-black text-green-800">兴趣维度分析</h4>
                </div>
                <div className="space-y-3">
                  {selectedBehavior.matches?.map((match, index) => {
                    const config = getDimensionConfig(match.dimension);
                    return (
                      <div key={index} className="bg-white p-3 rounded-lg border border-gray-100 shadow-sm hover:shadow-md transition">
                        <div className="flex items-center mb-3">
                          <div className={`p-1.5 rounded-lg ${config.color} shadow-sm`}>
                            <config.icon className="w-4 h-4" />
                          </div>
                          <span className="font-black text-gray-800 ml-2 text-sm">{config.label}</span>
                        </div>
                        
                        {/* 关联度 */}
                        <div className="mb-3">
                          <div className="flex justify-between items-center mb-1.5">
                            <span className="text-xs font-bold text-gray-600">关联度</span>
                            <span className="text-xs font-black text-purple-600 bg-purple-50 px-2 py-0.5 rounded-lg">
                              {(match.weight * 100).toFixed(0)}%
                            </span>
                          </div>
                          <div className="w-full h-2 bg-gray-100 rounded-full overflow-hidden shadow-inner">
                            <div 
                              className="h-full bg-gradient-to-r from-purple-400 to-purple-600 rounded-full transition-all shadow-sm"
                              style={{ width: `${match.weight * 100}%` }}
                            />
                          </div>
                        </div>
                        
                        {/* 喜好强度 */}
                        <div className="mb-3">
                          <div className="flex justify-between items-center mb-1.5">
                            <span className="text-xs font-bold text-gray-600">喜好强度</span>
                            <span className={`text-xs font-black flex items-center px-2 py-0.5 rounded-lg ${
                              match.intensity > 0 
                                ? 'text-green-600 bg-green-50' 
                                : match.intensity < 0 
                                ? 'text-red-600 bg-red-50' 
                                : 'text-gray-600 bg-gray-50'
                            }`}>
                              {match.intensity > 0 ? '😊' : match.intensity < 0 ? '😞' : '😐'} 
                              <span className="ml-1">{Math.abs(match.intensity * 100).toFixed(0)}%</span>
                            </span>
                          </div>
                          <div className="relative w-full h-2 bg-gray-100 rounded-full overflow-hidden shadow-inner">
                            <div className="absolute inset-0 flex">
                              <div className="flex-1 border-r border-gray-300"></div>
                            </div>
                            <div 
                              className={`absolute h-full rounded-full transition-all shadow-sm ${
                                match.intensity > 0 
                                  ? 'bg-gradient-to-r from-green-400 to-green-600' 
                                  : match.intensity < 0 
                                  ? 'bg-gradient-to-l from-red-400 to-red-600' 
                                  : 'bg-gray-400'
                              }`}
                              style={{ 
                                width: `${Math.abs(match.intensity) * 50}%`,
                                left: match.intensity >= 0 ? '50%' : `${50 - Math.abs(match.intensity) * 50}%`
                              }}
                            />
                          </div>
                          <div className="flex justify-between text-xs font-bold text-gray-400 mt-1">
                            <span>讨厌</span>
                            <span>中性</span>
                            <span>喜欢</span>
                          </div>
                        </div>
                        
                        {/* 推理说明 */}
                        {match.reasoning && (
                          <div className="mt-2 p-2 bg-gradient-to-r from-yellow-50 to-amber-50 rounded-lg border-l-2 border-yellow-400 shadow-sm">
                            <p className="text-xs text-gray-700 font-medium leading-relaxed flex items-start">
                              <span className="mr-1.5 text-sm">💡</span>
                              <span>{match.reasoning}</span>
                            </p>
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
              
              {/* 元数据 */}
              <div className="flex justify-between text-xs font-medium text-gray-400 pt-3 border-t border-gray-100">
                <div className="flex items-center">
                  {selectedBehavior.timestamp && (
                    <div className="flex items-center bg-gray-50 px-2 py-1 rounded-lg">
                      <span className="mr-1">🕐</span>
                      {new Date(selectedBehavior.timestamp).toLocaleString('zh-CN')}
                    </div>
                  )}
                </div>
                <div className="flex items-center">
                  {selectedBehavior.source && (
                    <div className="flex items-center bg-gray-50 px-2 py-1 rounded-lg">
                      <span className="mr-1">📊</span>
                      {selectedBehavior.source === 'GAME' ? 'AI对话' : selectedBehavior.source === 'REPORT' ? '报告' : 'AI对话'}
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
      </div>
    </>
  );
};
