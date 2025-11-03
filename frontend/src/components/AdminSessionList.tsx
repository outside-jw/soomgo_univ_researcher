import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { adminApi } from '../services/api';
import './AdminSessionList.css';

interface Session {
  session_id: string;
  assignment_text: string;
  created_at: string;
  user_id: string | null;
  updated_at: string;
  completed_at: string | null;
  is_active: boolean;
}

export default function AdminSessionList() {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    loadSessions();
  }, []);

  const loadSessions = async () => {
    try {
      setIsLoading(true);
      const data = await adminApi.getAllSessions();
      // API returns { total: number, sessions: array }, extract sessions
      setSessions(data.sessions || []);
    } catch (err) {
      console.error('Failed to load sessions:', err);
      setError('세션 목록을 불러오는데 실패했습니다');
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogout = () => {
    sessionStorage.removeItem('admin_authenticated');
    navigate('/admin');
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString('ko-KR', {
      year: 'numeric',
      month: 'long',
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

  return (
    <div className="admin-container">
      <header className="admin-header">
        <h1>대화 기록 관리</h1>
        <button onClick={handleLogout} className="logout-button">
          로그아웃
        </button>
      </header>

      {error && <div className="error-banner">{error}</div>}

      <div className="sessions-list">
        {sessions.length === 0 ? (
          <div className="empty-state">
            <p>아직 대화 기록이 없습니다</p>
          </div>
        ) : (
          sessions.map((session) => (
            <div
              key={session.session_id}
              className="session-card"
              onClick={() => navigate(`/admin/sessions/${session.session_id}`)}
            >
              <div className="session-header">
                <span className="session-id">세션 {session.session_id.substring(0, 8)}</span>
                <span className="session-date">{formatDate(session.created_at)}</span>
              </div>
              <div className="session-assignment">
                {session.assignment_text || '과제 내용 없음'}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
