/**
 * CPS Progress Stepper Component
 * Visualizes the Creative Problem Solving process in 3 simplified groups
 * Internal: 6 stages, Display: 3 groups
 */
import './CPSProgressStepper.css';

interface CPSStage {
  id: string;
  name: string;
  shortName: string;
  category: 'understanding' | 'ideation' | 'preparation';
}

const CPS_STAGES: CPSStage[] = [
  { id: '도전_이해_기회구성', name: '기회 구성', shortName: '기회', category: 'understanding' },
  { id: '도전_이해_자료탐색', name: '자료 탐색', shortName: '탐색', category: 'understanding' },
  { id: '도전_이해_문제구조화', name: '문제 구조화', shortName: '구조화', category: 'understanding' },
  { id: '아이디어_생성', name: '아이디어 생성', shortName: '생성', category: 'ideation' },
  { id: '실행_준비_해결책고안', name: '해결책 고안', shortName: '고안', category: 'preparation' },
  { id: '실행_준비_수용구축', name: '수용 구축', shortName: '구축', category: 'preparation' },
];

const CATEGORY_INFO = {
  understanding: { label: '문제 이해', color: '#3B82F6' },
  ideation: { label: '아이디어 생성', color: '#F59E0B' },
  preparation: { label: '실행 준비', color: '#10B981' },
};

interface Props {
  currentStage: string;
  completedStages: string[];
}

export default function CPSProgressStepper({ currentStage, completedStages = [] }: Props) {
  // Get current stage category
  const currentStageData = CPS_STAGES.find(stage => stage.id === currentStage);
  const currentCategory = currentStageData?.category;

  // Calculate group progress
  const getGroupProgress = (category: keyof typeof CATEGORY_INFO) => {
    const groupStages = CPS_STAGES.filter(s => s.category === category);
    const completedCount = groupStages.filter(s => completedStages.includes(s.id)).length;
    const isCurrentGroup = currentCategory === category;
    const hasCurrentStage = groupStages.some(s => s.id === currentStage);

    return {
      total: groupStages.length,
      completed: completedCount,
      current: hasCurrentStage ? 1 : 0,
      isActive: isCurrentGroup,
      isCompleted: completedCount === groupStages.length,
      isPending: !isCurrentGroup && completedCount === 0,
    };
  };

  // Calculate overall progress
  const totalStages = CPS_STAGES.length;
  const currentIndex = CPS_STAGES.findIndex(stage => stage.id === currentStage);
  const progressPercentage = currentIndex >= 0 ? ((currentIndex + 1) / totalStages) * 100 : 0;

  return (
    <div className="cps-progress-stepper">
      <div className="stepper-header">
        <h2>창의적 문제해결 프로세스</h2>
        <div className="progress-info">
          {currentIndex >= 0 && (
            <>
              <span className="current-step">{currentIndex + 1} / {totalStages}</span>
              <span className="progress-bar-mini">
                <span
                  className="progress-fill"
                  style={{ width: `${progressPercentage}%` }}
                />
              </span>
            </>
          )}
        </div>
      </div>

      <div className="stepper-container-grouped">
        {(Object.keys(CATEGORY_INFO) as Array<keyof typeof CATEGORY_INFO>).map((category, groupIndex) => {
          const categoryInfo = CATEGORY_INFO[category];
          const progress = getGroupProgress(category);
          const progressPercent = ((progress.completed + progress.current) / progress.total) * 100;

          return (
            <div
              key={category}
              className={`stepper-group ${progress.isActive ? 'active' : ''} ${progress.isCompleted ? 'completed' : ''} ${progress.isPending ? 'pending' : ''}`}
            >
              <div className="group-indicator">
                <div
                  className="group-icon"
                  style={progress.isActive || progress.isCompleted ? {
                    background: categoryInfo.color
                  } : {}}
                >
                  {progress.isCompleted ? (
                    <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                      <path
                        d="M16.6667 5L7.50002 14.1667L3.33335 10"
                        stroke="white"
                        strokeWidth="2.5"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      />
                    </svg>
                  ) : progress.isActive ? (
                    <div className="pulse-dot" />
                  ) : (
                    <span className="group-number">{groupIndex + 1}</span>
                  )}
                </div>
              </div>

              <div className="group-content">
                <div className="group-label">{categoryInfo.label}</div>

                {progress.isActive && (
                  <div className="group-status">
                    {progress.completed + progress.current} / {progress.total} 진행 중
                  </div>
                )}

                {progress.isCompleted && (
                  <div className="group-status completed">완료</div>
                )}

                {progress.isPending && (
                  <div className="group-status pending">대기</div>
                )}

                {/* Progress bar for active group */}
                {(progress.isActive || progress.completed > 0) && !progress.isCompleted && (
                  <div className="group-progress-bar">
                    <div
                      className="group-progress-fill"
                      style={{
                        width: `${progressPercent}%`,
                        background: categoryInfo.color,
                      }}
                    />
                  </div>
                )}
              </div>

              {groupIndex < Object.keys(CATEGORY_INFO).length - 1 && (
                <div className={`group-connector ${progress.isCompleted ? 'completed' : ''}`} />
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
