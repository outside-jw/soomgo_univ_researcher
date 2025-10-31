/**
 * Enhanced Message Card Component
 * Displays messages with metacognition tags and response depth indicators
 */
import './EnhancedMessageCard.css';
import { getScaffoldingPurpose } from '../constants/scaffolding';

interface Message {
  role: string;
  content: string;
  timestamp: string;
  metacog_elements?: string[];
  response_depth?: string;
  current_stage?: string;
}

interface Props {
  message: Message;
}

const METACOG_COLORS = {
  '점검': '#10B981',
  '조절': '#F59E0B',
  '지식': '#3B82F6',
};

const DEPTH_COLORS = {
  shallow: '#EF4444',
  medium: '#F59E0B',
  deep: '#10B981',
};

const DEPTH_LABELS = {
  shallow: '얕은 응답',
  medium: '보통 응답',
  deep: '깊은 응답',
};

export default function EnhancedMessageCard({ message }: Props) {
  const isUser = message.role === 'user';
  const isAgent = message.role === 'agent';

  return (
    <div className={`enhanced-message ${isUser ? 'user' : 'agent'}`}>
      <div className="message-avatar-enhanced">
        {isUser ? (
          <div className="avatar-circle user-avatar">
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
              <path
                d="M10 10C12.7614 10 15 7.76142 15 5C15 2.23858 12.7614 0 10 0C7.23858 0 5 2.23858 5 5C5 7.76142 7.23858 10 10 10Z"
                fill="white"
              />
              <path
                d="M10 12C5.58172 12 2 15.5817 2 20H18C18 15.5817 14.4183 12 10 12Z"
                fill="white"
              />
            </svg>
          </div>
        ) : (
          <div className="avatar-circle agent-avatar">
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
              <path
                d="M10 0L12.5 5L17.5 5.5L13.75 9.5L15 15L10 12L5 15L6.25 9.5L2.5 5.5L7.5 5L10 0Z"
                fill="white"
              />
            </svg>
          </div>
        )}
      </div>

      <div className="message-content-enhanced">
        <div className="message-header">
          <span className="message-sender">{isUser ? '학습자' : 'AI 에이전트'}</span>
          <span className="message-time">
            {new Date(message.timestamp).toLocaleTimeString('ko-KR', {
              hour: '2-digit',
              minute: '2-digit',
            })}
          </span>
        </div>

        <div className="message-text-enhanced">{message.content}</div>

        {isAgent && message.metacog_elements && message.metacog_elements.length > 0 && (
          <div className="message-tags">
            <div className="tags-label">촉진 요소:</div>
            <div className="tags-list">
              {message.metacog_elements.map((element, idx) => {
                const purpose = message.current_stage
                  ? getScaffoldingPurpose(message.current_stage, element)
                  : '';
                return (
                  <div key={idx} className="meta-tag-wrapper">
                    <span
                      className="meta-tag"
                      style={{
                        background: METACOG_COLORS[element as keyof typeof METACOG_COLORS] || '#6B7280',
                      }}
                    >
                      {element}
                    </span>
                    {purpose && (
                      <span className="meta-tag-purpose">
                        {purpose}
                      </span>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {isUser && message.response_depth && (
          <div
            className="depth-indicator-dot"
            style={{
              background: DEPTH_COLORS[message.response_depth as keyof typeof DEPTH_COLORS],
            }}
            aria-label={DEPTH_LABELS[message.response_depth as keyof typeof DEPTH_LABELS]}
            title={DEPTH_LABELS[message.response_depth as keyof typeof DEPTH_LABELS]}
          />
        )}

        {isAgent && message.reasoning && (
          <details className="reasoning-section">
            <summary className="reasoning-summary">
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none" className="reasoning-icon">
                <path
                  d="M8 0C3.6 0 0 3.6 0 8s3.6 8 8 8 8-3.6 8-8-3.6-8-8-8zm1 12H7V7h2v5zm0-6H7V4h2v2z"
                  fill="currentColor"
                />
              </svg>
              <span className="reasoning-label">왜 이 질문을?</span>
            </summary>
            <div className="reasoning-content">
              <p>{message.reasoning}</p>
            </div>
          </details>
        )}
      </div>
    </div>
  );
}
