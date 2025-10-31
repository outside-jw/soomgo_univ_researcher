/**
 * Type definitions for CPS Scaffolding Agent
 */

export interface Message {
  role: 'user' | 'agent';
  content: string;
  timestamp?: string;
}

export interface ScaffoldingData {
  current_stage: string;
  detected_metacog_needs: string[];
  response_depth: 'shallow' | 'medium' | 'deep';
  scaffolding_question: string;
  should_transition: boolean;
  reasoning: string;
}

export interface ChatResponse {
  session_id: string;
  agent_message: string;
  scaffolding_data: ScaffoldingData;
  timestamp: string;
}

export interface ChatRequest {
  session_id?: string;
  message: string;
  conversation_history: Message[];
  current_stage?: string;
}

export interface SessionResponse {
  session_id: string;
  created_at: string;
}
