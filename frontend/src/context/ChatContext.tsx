import React, { createContext, useContext, useEffect, useState, useCallback } from 'react';
import type { ReactNode } from 'react';
import { io, Socket } from 'socket.io-client';
import { useAuth } from './AuthContext';
import { API_BASE_URL } from '../utils/auth';
import type { Message, ChatRoom } from '../types';

interface ChatContextType {
  socket: Socket | null;
  messages: Message[];
  chatRooms: ChatRoom[];
  currentRoom: string | null;
  isConnected: boolean;
  isTyping: boolean;
  typingUsers: string[];
  unreadCount: number;
  joinRoom: (roomId: string) => void;
  leaveRoom: (roomId: string) => void;
  sendMessage: (roomId: string, message: string, receiverId: string) => void;
  startTyping: (roomId: string) => void;
  stopTyping: (roomId: string) => void;
  markAsRead: (roomId: string) => void;
  clearMessages: () => void;
  fetchChatRooms: () => void;
}

const ChatContext = createContext<ChatContextType | undefined>(undefined);

export const useChat = () => {
  const context = useContext(ChatContext);
  if (context === undefined) {
    console.error('useChat was called outside of ChatProvider. Component tree:', new Error().stack);
    console.error('Make sure the component calling useChat is wrapped with ChatProvider');
    throw new Error('useChat must be used within a ChatProvider');
  }
  return context;
};

interface ChatProviderProps {
  children: ReactNode;
}

export const ChatProvider: React.FC<ChatProviderProps> = ({ children }) => {
  const { user, token } = useAuth();
  const [socket, setSocket] = useState<Socket | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [chatRooms, setChatRooms] = useState<ChatRoom[]>([]);
  const [currentRoom, setCurrentRoom] = useState<string | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [typingUsers, setTypingUsers] = useState<string[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);

  // Fetch chat rooms from backend
  const fetchChatRooms = useCallback(async () => {
    if (!user || !token) {
      console.log('ChatProvider: Cannot fetch chat rooms - user or token not available');
      return;
    }
    
    try {
      const endpoint = user.role === 'student' ? '/student/chat-rooms' : '/recruiter/chat-rooms';
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        setChatRooms(data.chat_rooms || []);
      } else {
        console.error('Failed to fetch chat rooms:', response.status);
      }
    } catch (error) {
      console.error('Error fetching chat rooms:', error);
    }
  }, [user, token]);

  // Fetch chat rooms on mount and when user changes
  useEffect(() => {
    fetchChatRooms();
  }, [fetchChatRooms]);

  // Initialize socket connection
  useEffect(() => {
    if (user && token) {
      console.log('ChatProvider: Initializing socket connection for user:', user.username);
      const newSocket = io(`${API_BASE_URL}`, {
        // Socket.IO server path - using /ws/socket.io for production
        path: '/ws/socket.io',
        query: {
          token: token,
        },
        extraHeaders: {
          'Authorization': `Bearer ${token}`
        },
        // Let client negotiate transports (polling -> websocket) to maximize compatibility
        timeout: 20000,
      });

      newSocket.on('connect', () => {
        console.log('✅ Connected to chat server');
        setIsConnected(true);
      });

      newSocket.on('disconnect', (reason) => {
        console.log('❌ Disconnected from chat server:', reason);
        setIsConnected(false);
      });

      newSocket.on('connect_error', (error) => {
        console.error('❌ Connection error:', error);
        setIsConnected(false);
      });

      newSocket.on('new_message', (message: Message) => {
        setMessages((prev) => [...prev, message]);
        if (message.room_id !== currentRoom) {
          setUnreadCount((prev) => prev + 1);
        }
      });

      newSocket.on('chat_history', ({ room_id, messages: roomMessages }: { room_id: string; messages: Message[] }) => {
        if (room_id === currentRoom) {
          setMessages(roomMessages);
        }
      });

      newSocket.on('error', (error: { msg: string }) => {
        console.error('Chat error:', error.msg);
      });

      newSocket.on('user_typing', ({ userId, roomId }: { userId: string; roomId: string }) => {
        if (roomId === currentRoom && userId !== user.username) {
          setTypingUsers((prev) => [...prev.filter(id => id !== userId), userId]);
          
          // Remove typing indicator after 3 seconds
          setTimeout(() => {
            setTypingUsers((prev) => prev.filter(id => id !== userId));
          }, 3000);
        }
      });

      newSocket.on('user_stopped_typing', ({ userId, roomId }: { userId: string; roomId: string }) => {
        if (roomId === currentRoom) {
          setTypingUsers((prev) => prev.filter(id => id !== userId));
        }
      });

      newSocket.on('room_joined', ({ roomId }: { roomId: string }) => {
        console.log(`✅ Joined room: ${roomId}`);
      });

      newSocket.on('room_left', ({ roomId }: { roomId: string }) => {
        console.log(`✅ Left room: ${roomId}`);
      });

      setSocket(newSocket);

      return () => {
        newSocket.close();
      };
    }
  }, [user, token]);

  const joinRoom = useCallback(async (roomId: string) => {
    if (socket && isConnected) {
      socket.emit('join_room', { room_id: roomId });
      setCurrentRoom(roomId);
      setMessages([]); // Clear previous messages
      
      // Fetch message history from API
      try {
        const response = await fetch(`${API_BASE_URL}/chat/history/${roomId}`, {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });
        
        if (response.ok) {
          const data = await response.json();
          setMessages(data.messages || []);
          console.log(`✅ Loaded ${data.messages?.length || 0} messages for room: ${roomId}`);
        } else {
          console.error('Failed to fetch chat history:', response.status);
        }
      } catch (error) {
        console.error('Error fetching chat history:', error);
      }
    }
  }, [socket, isConnected, token]);

  const leaveRoom = useCallback((roomId: string) => {
    if (socket && isConnected) {
      socket.emit('leave_room', { room_id: roomId });
      setCurrentRoom(null);
    }
  }, [socket, isConnected]);

  const sendMessage = useCallback((roomId: string, message: string, receiverId: string) => {
    if (socket && isConnected) {
      socket.emit('send_message', {
        room_id: roomId,
        content: message,
        receiver_id: receiverId,
      });
    }
  }, [socket, isConnected]);

  const startTyping = useCallback((roomId: string) => {
    if (socket && isConnected) {
      socket.emit('start_typing', { room_id: roomId });
    }
  }, [socket, isConnected]);

  const stopTyping = useCallback((roomId: string) => {
    if (socket && isConnected) {
      socket.emit('stop_typing', { room_id: roomId });
    }
  }, [socket, isConnected]);

  const markAsRead = useCallback((roomId: string) => {
    if (socket && isConnected) {
      socket.emit('mark_as_read', { room_id: roomId });
      setUnreadCount(0);
    }
  }, [socket, isConnected]);

  const clearMessages = useCallback(() => {
    setMessages([]);
  }, []);

  const value: ChatContextType = {
    socket,
    messages,
    chatRooms,
    currentRoom,
    isConnected,
    isTyping: typingUsers.length > 0,
    typingUsers,
    unreadCount,
    joinRoom,
    leaveRoom,
    sendMessage,
    startTyping,
    stopTyping,
    markAsRead,
    clearMessages,
    fetchChatRooms,
  };

  return <ChatContext.Provider value={value}>{children}</ChatContext.Provider>;
};
