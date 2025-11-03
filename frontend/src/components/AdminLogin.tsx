import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './AdminLogin.css';

export default function AdminLogin() {
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();

    const correctPassword = import.meta.env.VITE_ADMIN_PASSWORD;

    if (password === correctPassword) {
      sessionStorage.setItem('admin_authenticated', 'true');
      navigate('/admin/sessions');
    } else {
      setError('잘못된 비밀번호입니다');
      setPassword('');
    }
  };

  return (
    <div className="admin-login-container">
      <div className="admin-login-card">
        <h1 className="admin-login-title">관리자 로그인</h1>
        <p className="admin-login-subtitle">대화 기록을 열람하려면 비밀번호를 입력하세요</p>

        <form onSubmit={handleLogin} className="admin-login-form">
          <div className="form-group">
            <label htmlFor="password">비밀번호</label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="비밀번호 입력"
              className="password-input"
              autoFocus
            />
          </div>

          {error && <div className="error-message">{error}</div>}

          <button type="submit" className="login-button">
            로그인
          </button>
        </form>
      </div>
    </div>
  );
}
