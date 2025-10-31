/**
 * Stage Transition Notification Component
 * Shows a celebratory message when transitioning to the next CPS stage
 */
import { useEffect } from 'react';
import './StageTransitionNotification.css';
import { STAGE_TRANSITION_MESSAGES, NEXT_STAGE_NAMES } from '../constants/scaffolding';

interface Props {
  fromStage: string;
  toStage: string;
  onClose: () => void;
}

export default function StageTransitionNotification({ fromStage, onClose }: Props) {
  useEffect(() => {
    const timer = setTimeout(() => {
      onClose();
    }, 4000); // Auto-close after 4 seconds

    return () => clearTimeout(timer);
  }, [onClose]);

  const completionMessage = STAGE_TRANSITION_MESSAGES[fromStage] || '단계를 완료했습니다';
  const nextStageName = NEXT_STAGE_NAMES[fromStage] || '다음 단계';

  return (
    <div className="transition-notification">
      <div className="transition-content">
        <div className="transition-text">
          <div className="transition-title">
            <strong>잘하셨습니다!</strong> {completionMessage}
          </div>
          <div className="transition-subtitle">
            이제 <strong>{nextStageName}</strong> 단계로 넘어갑니다
          </div>
        </div>
        <button className="transition-close" onClick={onClose} aria-label="닫기">
          ×
        </button>
      </div>
      <div className="transition-progress" />
    </div>
  );
}
