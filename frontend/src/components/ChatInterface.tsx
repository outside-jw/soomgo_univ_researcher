/**
 * Main chat interface component
 */
import { useState, useRef, useEffect } from 'react';
import { chatApi } from '../services/api';
import type { Message, ScaffoldingData } from '../types';
import './ChatInterface.css';

export default function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [currentStage, setCurrentStage] = useState<string>('');
  const [scaffoldingInfo, setScaffoldingInfo] = useState<ScaffoldingData | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage: Message = {
      role: 'user',
      content: inputValue,
      timestamp: new Date().toISOString(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      const response = await chatApi.sendMessage({
        session_id: sessionId || undefined,
        message: inputValue,
        conversation_history: messages,
        current_stage: currentStage || undefined,
      });

      // Update session ID if new
      if (!sessionId) {
        setSessionId(response.session_id);
      }

      // Update current stage
      setCurrentStage(response.scaffolding_data.current_stage);
      setScaffoldingInfo(response.scaffolding_data);

      // Add agent response
      const agentMessage: Message = {
        role: 'agent',
        content: response.agent_message,
        timestamp: response.timestamp,
      };

      setMessages(prev => [...prev, agentMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage: Message = {
        role: 'agent',
        content: '죄송합니다. 오류가 발생했습니다. 다시 시도해주세요.',
        timestamp: new Date().toISOString(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const getStageName = (stage: string): string => {
    const stageMap: Record<string, string> = {
      '도전_이해_기회구성': '도전 이해 - 기회 구성',
      '도전_이해_자료탐색': '도전 이해 - 자료 탐색',
      '도전_이해_문제구조화': '도전 이해 - 문제 구조화',
      '아이디어_생성': '아이디어 생성',
      '실행_준비_해결책고안': '실행 준비 - 해결책 고안',
      '실행_준비_수용구축': '실행 준비 - 수용 구축',
    };
    return stageMap[stage] || stage;
  };

  return (
    <div className="chat-container">
      <div className="chat-header">
        <h1>창의적 문제해결 스캐폴딩 에이전트</h1>
        {currentStage && (
          <div className="stage-info">
            <span className="stage-label">현재 단계:</span>
            <span className="stage-value">{getStageName(currentStage)}</span>
          </div>
        )}
      </div>

      <div className="messages-container">
        {messages.length === 0 && (
          <div className="welcome-message">
            <h2>안녕하세요! 👋</h2>
            <p>저는 여러분의 창의적 문제해결을 돕는 AI 에이전트입니다.</p>
            <p>해결하고 싶은 문제나 고민을 자유롭게 말씀해주세요.</p>
          </div>
        )}

        {messages.map((msg, idx) => (
          <div key={idx} className={`message ${msg.role}`}>
            <div className="message-avatar">
              {msg.role === 'user' ? '👤' : '🤖'}
            </div>
            <div className="message-content">
              <div className="message-text">{msg.content}</div>
              <div className="message-time">
                {msg.timestamp && new Date(msg.timestamp).toLocaleTimeString('ko-KR')}
              </div>
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="message agent">
            <div className="message-avatar">🤖</div>
            <div className="message-content">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {scaffoldingInfo && (
        <div className="scaffolding-info">
          <div className="info-item">
            <strong>메타인지 요소:</strong> {scaffoldingInfo.detected_metacog_needs.join(', ')}
          </div>
          <div className="info-item">
            <strong>응답 깊이:</strong> {scaffoldingInfo.response_depth}
          </div>
        </div>
      )}

      <div className="input-container">
        <textarea
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="메시지를 입력하세요... (Shift+Enter로 줄바꿈)"
          disabled={isLoading}
          rows={3}
        />
        <button
          onClick={handleSendMessage}
          disabled={isLoading || !inputValue.trim()}
        >
          {isLoading ? '전송 중...' : '전송'}
        </button>
      </div>
    </div>
  );
}
