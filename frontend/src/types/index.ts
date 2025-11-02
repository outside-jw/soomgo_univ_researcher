/**
 * Type definitions for CPS Scaffolding Agent
 */

export interface Message {
  role: 'user' | 'agent';
  content: string;
  timestamp: string;
  metacog_elements?: string[];
  response_depth?: string;
  reasoning?: string;
  current_stage?: string;
}

export interface ScaffoldingData {
  current_stage: string;
  detected_metacog_needs: string[];
  response_depth: 'shallow' | 'medium' | 'deep';
  scaffolding_question: string;
  should_transition: boolean;
  reasoning: string;
}

export interface TurnCounts {
  [stage: string]: {
    current: number;
    max: number;
  };
}

export interface ChatResponse {
  session_id: string;
  agent_message: string;
  scaffolding_data: ScaffoldingData;
  turn_counts?: TurnCounts;
  forced_transition?: boolean;
  forced_transition_message?: string;
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
