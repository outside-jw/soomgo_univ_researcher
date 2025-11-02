/**
 * Turn counter component showing remaining turns for current CPS stage
 */
import './TurnCounter.css';

interface TurnCounts {
  [key: string]: {
    current: number;
    max: number;
  };
}

interface TurnCounterProps {
  currentStage: string;
  turnCounts: TurnCounts | null;
  forcedTransition?: boolean;
  forcedTransitionMessage?: string;
}

const STAGE_NAMES: { [key: string]: string } = {
  '도전_이해': '문제 이해',
  '아이디어_생성': '아이디어 생성',
  '실행_준비': '실행 준비',
};

export default function TurnCounter({
  currentStage,
  turnCounts,
  forcedTransition,
  forcedTransitionMessage
}: TurnCounterProps) {
  if (!turnCounts || !currentStage) return null;

  const stageCounts = turnCounts[currentStage];
  if (!stageCounts) return null;

  const { current, max } = stageCounts;
  const remaining = Math.max(0, max - current);
  const percentage = (current / max) * 100;

  // Determine status color based on remaining turns
  const getStatusColor = () => {
    if (remaining === 0) return 'danger';
    if (remaining <= 2) return 'warning';
    return 'normal';
  };

  const statusColor = getStatusColor();
  const stageName = STAGE_NAMES[currentStage] || currentStage;

  return (
    <div className={`turn-counter ${statusColor}`}>
      {forcedTransition && forcedTransitionMessage && (
        <div className="forced-transition-alert">
          <svg
            className="alert-icon"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <span>{forcedTransitionMessage}</span>
        </div>
      )}

      <div className="turn-counter-content">
        <div className="turn-counter-header">
          <span className="stage-name">{stageName}</span>
          <span className="turn-text">
            {current}/{max} 턴
          </span>
        </div>

        <div className="progress-bar-container">
          <div
            className={`progress-bar ${statusColor}`}
            style={{ width: `${percentage}%` }}
          />
        </div>

        {remaining > 0 ? (
          <div className="remaining-text">
            {remaining}턴 남음
          </div>
        ) : (
          <div className="limit-reached-text">
            최대 턴 수 도달
          </div>
        )}
      </div>
    </div>
  );
}
