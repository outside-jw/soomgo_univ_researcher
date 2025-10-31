/**
 * API service for communicating with backend
 */
import axios from 'axios';
import type { ChatRequest, ChatResponse, SessionResponse } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const chatApi = {
  /**
   * Send a message and receive scaffolding response
   */
  sendMessage: async (request: ChatRequest): Promise<ChatResponse> => {
    const response = await api.post<ChatResponse>('/api/chat/message', request);
    return response.data;
  },

  /**
   * Create a new session
   */
  createSession: async (assignmentText: string): Promise<SessionResponse> => {
    const response = await api.post<SessionResponse>('/api/chat/session', {
      assignment_text: assignmentText,
    });
    return response.data;
  },

  /**
   * Health check
   */
  healthCheck: async (): Promise<{ status: string }> => {
    const response = await api.get('/api/chat/health');
    return response.data;
  },
};

export default api;
