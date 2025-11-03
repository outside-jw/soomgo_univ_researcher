/**
 * Main chat interface component with enhanced UI
 */
import { useState, useRef, useEffect } from 'react';
import { chatApi } from '../services/api';
import type { Message, ScaffoldingData, TurnCounts } from '../types';
import CPSProgressStepper from './CPSProgressStepper';
import MetacognitionSidebar from './MetacognitionSidebar';
import EnhancedMessageCard from './EnhancedMessageCard';
import AssignmentCard from './AssignmentCard';
import './ChatInterface.css';

export default function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [assignmentText, setAssignmentText] = useState<string>('');
  const [currentStage, setCurrentStage] = useState<string>('');
  const [completedStages, setCompletedStages] = useState<string[]>([]);
  const [scaffoldingInfo, setScaffoldingInfo] = useState<ScaffoldingData | null>(null);
  const [metacogStats, setMetacogStats] = useState({
    monitoring: 0,
    control: 0,
    knowledge: 0,
  });
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Update metacog stats when new scaffolding arrives
  useEffect(() => {
    if (scaffoldingInfo?.detected_metacog_needs) {
      const newStats = { ...metacogStats };
      scaffoldingInfo.detected_metacog_needs.forEach((element: string) => {
        if (element === '점검') newStats.monitoring++;
        else if (element === '조절') newStats.control++;
        else if (element === '지식') newStats.knowledge++;
      });
      setMetacogStats(newStats);
    }
  }, [scaffoldingInfo]);

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage: Message = {
      role: 'user',
      content: inputValue,
      timestamp: new Date().toISOString(),
    };

    setMessages(prev => [...prev, userMessage]);
    const currentInput = inputValue;
    setInputValue('');
    setIsLoading(true);

    try {
      // Create session if this is the first message
      let currentSessionId = sessionId;
      if (!currentSessionId) {
        const sessionResponse = await chatApi.createSession(currentInput);
        currentSessionId = sessionResponse.session_id;
        setSessionId(currentSessionId);
        setAssignmentText(currentInput); // Save the assignment text
      }

      const response = await chatApi.sendMessage({
        session_id: currentSessionId,
        message: currentInput,
        conversation_history: messages,
        current_stage: currentStage || undefined,
      });

      // Update stage tracking
      const newStage = response.scaffolding_data.current_stage;

      if (newStage !== currentStage && currentStage) {
        setCompletedStages(prev => [...new Set([...prev, currentStage])]);
      }
      setCurrentStage(newStage);
      setScaffoldingInfo(response.scaffolding_data);

      // Add agent response with metadata
      const agentMessage: Message = {
        role: 'agent',
        content: response.agent_message,
        timestamp: response.timestamp,
        metacog_elements: response.scaffolding_data.detected_metacog_needs,
        response_depth: response.scaffolding_data.response_depth,
        reasoning: response.scaffolding_data.reasoning,
        current_stage: response.scaffolding_data.current_stage,
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

  return (
    <div className="chat-interface-container">
      {/* CPS Progress Stepper */}
      <CPSProgressStepper currentStage={currentStage} completedStages={completedStages} />

      <div className="chat-main-area">
        {/* Metacognition Sidebar */}
        {sidebarOpen && (
          <MetacognitionSidebar
            stats={metacogStats}
            currentDepth={scaffoldingInfo?.response_depth || ''}
            totalMessages={messages.length}
          />
        )}

        {/* Chat Area */}
        <div className="chat-content-area">
          <div className="messages-container-enhanced">
            {/* Assignment Card - shown when session is active */}
            {assignmentText && <AssignmentCard assignmentText={assignmentText} />}

            {messages.length === 0 && (
              <div className="welcome-message-enhanced">
                <div className="welcome-icon">🎯</div>
                <h2>창의적 문제해결을 시작해볼까요?</h2>
                <p className="welcome-description">
                  AI 에이전트가 당신의 창의적 사고를 촉진하여<br />
                  더 나은 해결책을 찾을 수 있도록 도와드립니다.
                </p>
                <div className="welcome-features">
                  <div className="feature-item">
                    <span className="feature-text">체계적인 문제 분석</span>
                  </div>
                  <div className="feature-item">
                    <span className="feature-text">다양한 아이디어 생성</span>
                  </div>
                  <div className="feature-item">
                    <span className="feature-text">실행 가능한 해결책</span>
                  </div>
                </div>
              </div>
            )}

            {messages.map((msg, idx) => (
              <EnhancedMessageCard key={idx} message={msg} />
            ))}

            {isLoading && (
              <div className="enhanced-message agent">
                <div className="message-avatar-enhanced">
                  <div className="avatar-circle agent-avatar">
                    <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                      <path
                        d="M10 0L12.5 5L17.5 5.5L13.75 9.5L15 15L10 12L5 15L6.25 9.5L2.5 5.5L7.5 5L10 0Z"
                        fill="white"
                      />
                    </svg>
                  </div>
                </div>
                <div className="message-content-enhanced">
                  <div className="typing-indicator-enhanced">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <div className="input-container-enhanced">
            {/* Stage Transition Button - shown when not at final stage */}
            {currentStage && currentStage !== '실행_준비' && messages.length > 0 && (
              <div className="stage-transition-hint">
                <button
                  onClick={() => {
                    if (isLoading) return;

                    const nextStageMap: { [key: string]: string } = {
                      '도전_이해': '아이디어_생성',
                      '아이디어_생성': '실행_준비',
                    };
                    const nextStage = nextStageMap[currentStage];
                    if (nextStage) {
                      // Set the transition message in input
                      const transitionMessage = `이제 ${nextStage.replace('_', ' ')} 단계로 이동하고 싶습니다.`;
                      setInputValue(transitionMessage);

                      // Trigger send automatically after setting input
                      setTimeout(() => {
                        handleSendMessage();
                      }, 100);
                    }
                  }}
                  className="next-stage-button"
                  disabled={isLoading}
                >
                  <svg width="16" height="16" viewBox="0 0 16 16" fill="none" style={{ marginRight: '6px' }}>
                    <path d="M6 12L10 8L6 4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                  다음 단계로 이동
                </button>
                <span className="hint-text">충분히 탐색했다면 다음 단계로 이동할 수 있습니다</span>
              </div>
            )}

            <div className="input-wrapper">
              <textarea
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="여기에 메시지를 입력하세요... (Shift+Enter로 줄바꿈)"
                disabled={isLoading}
                rows={3}
                className="input-textarea"
              />
              <button
                onClick={handleSendMessage}
                disabled={isLoading || !inputValue.trim()}
                className="send-button"
              >
                {isLoading ? (
                  <>
                    <svg className="spinner" width="20" height="20" viewBox="0 0 20 20">
                      <circle cx="10" cy="10" r="8" stroke="currentColor" strokeWidth="2" fill="none" />
                    </svg>
                    전송 중...
                  </>
                ) : (
                  <>
                    <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                      <path d="M2 10L18 2L10 18L8 10L2 10Z" fill="currentColor" />
                    </svg>
                    전송
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Mobile Sidebar Toggle */}
      <button
        className="sidebar-toggle-mobile"
        onClick={() => setSidebarOpen(!sidebarOpen)}
        aria-label="Toggle sidebar"
      >
        {sidebarOpen ? '◀' : '▶'}
      </button>
    </div>
  );
}
