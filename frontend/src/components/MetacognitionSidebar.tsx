/**
 * Metacognition Sidebar Component
 * Real-time tracking of metacognitive elements (monitoring, control, knowledge)
 */
import { useState } from 'react';
import './MetacognitionSidebar.css';

interface MetacognitionStats {
  monitoring: number;
  control: number;
  knowledge: number;
}

interface Props {
  stats: MetacognitionStats;
  currentDepth: string;
  totalMessages: number;
}

const METACOG_INFO = {
  monitoring: {
    label: '점검',
    icon: '✓',
    color: '#10B981',
    description: '과제 특성 평가, 수행 예측',
  },
  control: {
    label: '조절',
    icon: '⚙',
    color: '#F59E0B',
    description: '전략 선택, 과제 조절',
  },
  knowledge: {
    label: '지식',
    icon: '✓',
    color: '#3B82F6',
    description: '경험 활용, 지식 적용',
  },
};

const DEPTH_INFO = {
  shallow: { label: '간단한 답변', color: '#EF4444' },
  medium: { label: '보통 깊이', color: '#F59E0B' },
  deep: { label: '깊은 사고', color: '#10B981' },
};

export default function MetacognitionSidebar({ stats, currentDepth, totalMessages }: Props) {
  const [showDetails, setShowDetails] = useState(false);
  const maxCount = Math.max(stats.monitoring, stats.control, stats.knowledge, 1);

  return (
    <div className="metacognition-sidebar">
      {/* Basic Summary - Always Visible */}
      <div className="sidebar-section">
        <div className="section-header">
          <h3 className="section-title">학습 현황</h3>
          <button
            className="toggle-details-button"
            onClick={() => setShowDetails(!showDetails)}
            aria-label={showDetails ? '상세 정보 숨기기' : '상세 정보 보기'}
          >
            {showDetails ? '간단히 보기' : '상세히 보기'}
          </button>
        </div>
        <div className="stats-grid">
          <div className="stat-item">
            <div className="stat-value">{totalMessages}</div>
            <div className="stat-label">총 메시지</div>
          </div>
          <div className="stat-item">
            <div className="stat-value">{stats.monitoring + stats.control + stats.knowledge}</div>
            <div className="stat-label">사고 촉진 활동</div>
          </div>
        </div>
      </div>

      {/* Detailed Information - Toggleable */}
      {showDetails && (
        <>
          <div className="sidebar-section">
            <div className="metacog-elements">
              {(Object.keys(METACOG_INFO) as Array<keyof typeof METACOG_INFO>).map((key) => {
                const info = METACOG_INFO[key];
                const count = stats[key];
                const percentage = (count / maxCount) * 100;

                return (
                  <div key={key} className="metacog-item">
                    <div className="metacog-header">
                      <div className="metacog-icon" style={{ background: info.color }}>
                        {info.icon}
                      </div>
                      <div className="metacog-info">
                        <div className="metacog-label">{info.label}</div>
                        <div className="metacog-count">{count}회</div>
                      </div>
                    </div>
                    <div className="metacog-bar">
                      <div
                        className="metacog-fill"
                        style={{
                          width: `${percentage}%`,
                          background: info.color,
                        }}
                      />
                    </div>
                    <div className="metacog-description">{info.description}</div>
                  </div>
                );
              })}
            </div>
          </div>

          <div className="sidebar-section">
            <h3 className="section-title">생각의 깊이</h3>
            <div className="depth-indicator">
              {currentDepth && DEPTH_INFO[currentDepth as keyof typeof DEPTH_INFO] ? (
                <>
                  <div
                    className="depth-badge"
                    style={{
                      background: DEPTH_INFO[currentDepth as keyof typeof DEPTH_INFO].color,
                    }}
                  >
                    <span className="depth-label">
                      {DEPTH_INFO[currentDepth as keyof typeof DEPTH_INFO].label}
                    </span>
                  </div>
                  <div className="depth-hint">
                    {currentDepth === 'shallow' && '더 구체적인 답변을 생각해보세요'}
                    {currentDepth === 'medium' && '좋습니다! 조금 더 깊이 생각해볼까요?'}
                    {currentDepth === 'deep' && '훌륭합니다! 깊이 있는 사고를 하고 계십니다'}
                  </div>
                </>
              ) : (
                <div className="depth-empty">대화를 시작해보세요</div>
              )}
            </div>
          </div>

          <div className="sidebar-tips">
            <div className="tip-content">
              <div className="tip-title">학습 가이드</div>
              <div className="tip-text">
                다양한 관점에서 문제를 바라보고, 여러 가능성을 탐색해보세요
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
