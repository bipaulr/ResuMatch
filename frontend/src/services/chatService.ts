import api from './api';
import type { Message, ChatRoom } from '../types';

export const chatService = {
  async getChatHistory(roomId: string): Promise<{
    room_id: string;
    recruiter: string;
    message_count: number;
    messages: Message[];
  }> {
    const response = await api.get(`/recruiter/chat-history/${roomId}`);
    return response.data;
  },

  async sendMessage(roomId: string, message: string, receiverId: string): Promise<void> {
    // This would typically be handled by Socket.IO, but we might need REST fallback
    await api.post('/chat/send', {
      room_id: roomId,
      message,
      receiver_id: receiverId,
    });
  },

  async getChatRooms(): Promise<ChatRoom[]> {
    const response = await api.get('/chat/rooms');
    return response.data;
  },

  async createChatRoom(participantIds: string[], jobId?: string): Promise<ChatRoom> {
    const response = await api.post('/chat/rooms', {
      participants: participantIds,
      job_id: jobId,
    });
    return response.data;
  },

  async markAsRead(roomId: string): Promise<void> {
    await api.post(`/chat/rooms/${roomId}/read`);
  },
};
