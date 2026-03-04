/**
 * 图片引导组件
 * 使用4张图片展示引导流程
 */

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronLeft, ChevronRight, X } from 'lucide-react';
import image1 from '../img/1.jpg';
import image2 from '../img/2.jpg';
import image3 from '../img/3.jpg';
import image4 from '../img/4.jpg';

interface ImageOnboardingTourProps {
  isOpen: boolean;
  onComplete: () => void;
  onSkip: () => void;
}

const images = [image1, image2, image3, image4];

export const ImageOnboardingTour: React.FC<ImageOnboardingTourProps> = ({
  isOpen,
  onComplete,
  onSkip,
}) => {
  const [currentStep, setCurrentStep] = useState(0);

  // 每次打开引导时重置为第一步
  useEffect(() => {
    if (isOpen) {
      setCurrentStep(0);
    }
  }, [isOpen]);

  const isFirstStep = currentStep === 0;
  const isLastStep = currentStep === images.length - 1;

  const handleNext = () => {
    if (isLastStep) {
      onComplete();
    } else {
      setCurrentStep(prev => prev + 1);
    }
  };

  const handlePrev = () => {
    if (!isFirstStep) {
      setCurrentStep(prev => prev - 1);
    }
  };

  const handleKeyDown = (e: KeyboardEvent) => {
    if (!isOpen) return;
    
    if (e.key === 'ArrowRight' || e.key === 'Enter') {
      handleNext();
    } else if (e.key === 'ArrowLeft') {
      handlePrev();
    } else if (e.key === 'Escape') {
      onSkip();
    }
  };

  useEffect(() => {
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, currentStep]);

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-[9999] flex items-center justify-center">
        {/* 遮罩层 */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="absolute inset-0 bg-black/80"
          onClick={onSkip}
        />

        {/* 图片容器 */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.95 }}
          className="relative z-10 max-w-5xl max-h-[90vh] w-full mx-4"
          onClick={(e) => e.stopPropagation()}
        >
          {/* 关闭按钮 */}
          <button
            onClick={onSkip}
            className="absolute -top-9 right-0 text-white/80 hover:text-white transition-colors p-2 rounded-full hover:bg-white/10"
            title="跳过引导 (Esc)"
          >
            <X className="w-6 h-6" />
          </button>

          {/* 图片 */}
          <div className="relative bg-white rounded-2xl shadow-2xl overflow-hidden">
            <AnimatePresence mode="wait">
              <motion.img
                key={currentStep}
                src={images[currentStep]}
                alt={`引导步骤 ${currentStep + 1}`}
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                transition={{ duration: 0.3 }}
                className="w-full h-auto object-contain"
              />
            </AnimatePresence>

            {/* 上一步按钮 */}
            {!isFirstStep && (
              <motion.button
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                onClick={handlePrev}
                className="absolute left-4 top-1/2 -translate-y-1/2 bg-black/50 backdrop-blur-md hover:bg-black/70 text-white p-4 rounded-full shadow-2xl transition-all hover:scale-110 active:scale-95 border-2 border-white/30"
                title="上一步 (←)"
              >
                <ChevronLeft className="w-8 h-8" />
              </motion.button>
            )}

            {/* 下一步按钮 */}
            <motion.button
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              onClick={handleNext}
              className="absolute right-4 top-1/2 -translate-y-1/2 bg-black/50 backdrop-blur-md hover:bg-black/70 text-white p-4 rounded-full shadow-2xl transition-all hover:scale-110 active:scale-95 border-2 border-white/30"
              title={isLastStep ? '完成引导 (→)' : '下一步 (→)'}
            >
              {isLastStep ? (
                <span className="px-2 text-lg font-bold">完成</span>
              ) : (
                <ChevronRight className="w-8 h-8" />
              )}
            </motion.button>

            {/* 步骤计数 */}
            <div className="absolute top-6 left-6 bg-black/30 backdrop-blur-md text-white px-4 py-2 rounded-full text-sm font-medium">
              {currentStep + 1} / {images.length}
            </div>

            {/* 进度指示器 */}
            <div className="absolute top-6 left-1/2 -translate-x-1/2 flex items-center gap-2 bg-black/30 backdrop-blur-md px-4 py-2 rounded-full">
              {images.map((_, index) => (
                <button
                  key={index}
                  onClick={() => setCurrentStep(index)}
                  className={`transition-all ${
                    index === currentStep
                      ? 'w-8 h-2 bg-white'
                      : 'w-2 h-2 bg-white/50 hover:bg-white/70'
                  } rounded-full`}
                  title={`跳转到第 ${index + 1} 步`}
                />
              ))}
            </div>
          </div>

          {/* 键盘提示 */}
          <div className="mt-4 text-center text-white/60 text-sm">
            使用 ← → 键切换 | Enter 下一步 | Esc 跳过
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
};
