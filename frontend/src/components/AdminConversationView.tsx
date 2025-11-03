import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { adminApi } from '../services/api';
import './AdminConversationView.css';

interface Conversation {
  id: number;
  role: string;
  message: string;
  cps_stage: string | null;
  metacog_elements: string[] | null;
  response_depth: string | null;
  created_at: string;
}

interface SessionData {
  session_id: string;  // UUID string, not number
  assignment_text: string;
  conversations: Conversation[];
}

export default function AdminConversationView() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [sessionData, setSessionData] = useState<SessionData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (id) {
      loadConversation(id);  // Pass UUID string directly, no parseInt
    }
  }, [id]);

  const loadConversation = async (sessionId: string) => {
    try {
      setIsLoading(true);
      const data = await adminApi.getSessionConversations(sessionId);
      setSessionData(data);
    } catch (err) {
      console.error('Failed to load conversation:', err);
      setError('대화 내용을 불러오는데 실패했습니다');
    } finally {
      setIsLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString('ko-KR', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  if (isLoading) {
    return (
      <div className="admin-container">
        <div className="loading">로딩 중...</div>
      </div>
    );
  }

  if (error || !sessionData) {
    return (
      <div className="admin-container">
        <div className="error-banner">{error || '세션을 찾을 수 없습니다'}</div>
        <button onClick={() => navigate('/admin/sessions')} className="back-button">
          목록으로 돌아가기
        </button>
      </div>
    );
  }

  return (
    <div className="admin-container">
      <header className="conversation-header">
        <button onClick={() => navigate('/admin/sessions')} className="back-button">
          ← 목록으로
        </button>
        <h1>세션 #{sessionData.session_id}</h1>
      </header>

      <div className="assignment-display">
        <h3>과제 내용</h3>
        <p>{sessionData.assignment_text}</p>
      </div>

      <div className="conversation-list">
        {sessionData.conversations.map((conv) => (
          <div key={conv.id} className={`conversation-item ${conv.role}`}>
            <div className="conversation-meta">
              <span className="conversation-role">
                {conv.role === 'user' ? '학생' : 'AI 에이전트'}
              </span>
              <span className="conversation-time">{formatDate(conv.created_at)}</span>
            </div>

            <div className="conversation-message">{conv.message}</div>

            {conv.role === 'agent' && (
              <div className="conversation-metadata">
                {conv.cps_stage && (
                  <span className="metadata-badge stage-badge">
                    단계: {conv.cps_stage.replace(/_/g, ' ')}
                  </span>
                )}
                {conv.response_depth && (
                  <span className={`metadata-badge depth-badge depth-${conv.response_depth}`}>
                    깊이: {conv.response_depth}
                  </span>
                )}
                {conv.metacog_elements && conv.metacog_elements.length > 0 && (
                  <span className="metadata-badge metacog-badge">
                    메타인지: {conv.metacog_elements.join(', ')}
                  </span>
                )}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
