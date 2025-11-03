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

const DEPTH_INFO = {
  shallow: { label: '간단한 답변', color: '#EF4444' },
  medium: { label: '보통 깊이', color: '#F59E0B' },
  deep: { label: '깊은 사고', color: '#10B981' },
};

export default function MetacognitionSidebar({ stats, currentDepth, totalMessages }: Props) {
  const [showDetails, setShowDetails] = useState(false);

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
        </div>
      </div>

      {/* Detailed Information - Toggleable */}
      {showDetails && (
        <>
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
