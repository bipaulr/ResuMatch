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

  // Initialize socket connection with multiple path fallbacks
  useEffect(() => {
    if (user && token) {
      console.log('ChatProvider: Initializing socket connection for user:', user.username);
      
      // Get API base URL from environment - prioritize production URL
      const API_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
      console.log('ChatProvider: Connecting to:', API_URL);
      console.log('ChatProvider: Environment:', import.meta.env.MODE);
      
      // Try multiple Socket.IO paths in order of preference
      const SOCKET_PATHS = [
        '/socket.io',        // Standard Socket.IO path
        '/ws/socket.io',     // WebSocket prefixed path
        '/socketio',         // Alternative path
        '/ws/socketio',      // WebSocket alternative
        '/api/socket.io'     // API prefixed path
      ];
      
      let currentSocket: Socket | null = null;
      let pathIndex = 0;
      
      const tryConnection = (pathIndex: number): Socket => {
        const SOCKET_PATH = SOCKET_PATHS[pathIndex] || '/socket.io';
        console.log(`ChatProvider: Attempting connection with path: ${SOCKET_PATH} (attempt ${pathIndex + 1}/${SOCKET_PATHS.length})`);
        
        const newSocket = io(API_URL, {
          // Use current Socket.IO path
          path: SOCKET_PATH,
          query: {
            token: token,
          },
          extraHeaders: {
            'Authorization': `Bearer ${token}`
          },
          // Force websocket for production (more reliable than polling)
          transports: ['websocket', 'polling'],
          // Enable credentials for CORS
          withCredentials: true,
          // Reconnection settings for production
          reconnection: false, // Disable auto-reconnection for path testing
          // Increase timeout for production
          timeout: 10000, // Shorter timeout for path testing
          // Force new connection
          forceNew: true
        });
        
        return newSocket;
      };
      
      const attemptConnection = () => {
        if (pathIndex >= SOCKET_PATHS.length) {
          console.error('❌ All Socket.IO paths failed. Connection unsuccessful.');
          return;
        }
        
        currentSocket = tryConnection(pathIndex);
        
        currentSocket.on('connect', () => {
          console.log(`✅ Connected to chat server using path: ${SOCKET_PATHS[pathIndex]}`);
          console.log('🔗 Socket ID:', currentSocket?.id);
          console.log('🚀 Transport:', currentSocket?.io.engine.transport.name);
          setIsConnected(true);
          
          // Enable reconnection now that we found a working path
          currentSocket!.io.opts.reconnection = true;
          currentSocket!.io.opts.reconnectionAttempts = 10;
          currentSocket!.io.opts.reconnectionDelay = 1000;
          currentSocket!.io.opts.reconnectionDelayMax = 5000;
        });

        currentSocket.on('disconnect', (reason) => {
          console.log('❌ Disconnected from chat server:', reason);
          setIsConnected(false);
        });

        currentSocket.on('connect_error', (error) => {
          console.error(`❌ Connection error with path ${SOCKET_PATHS[pathIndex]}:`, error.message);
          
          // Try next path
          pathIndex++;
          currentSocket?.close();
          
          if (pathIndex < SOCKET_PATHS.length) {
            console.log(`� Trying next path: ${SOCKET_PATHS[pathIndex]}`);
            setTimeout(attemptConnection, 1000); // Wait 1 second before trying next path
          } else {
            console.error('❌ All Socket.IO connection paths failed');
            setIsConnected(false);
          }
        });
        
        return currentSocket;
      };
      
      attemptConnection();
      
      // Set up handlers when connection is successful
      let finalSocket: Socket | null = null;
      
      const setupEventHandlers = (connectedSocket: Socket) => {
        connectedSocket.on('new_message', (message: Message) => {
          setMessages((prev) => [...prev, message]);
          if (message.room_id !== currentRoom) {
            setUnreadCount((prev) => prev + 1);
          }
        });

        connectedSocket.on('chat_history', ({ room_id, messages: roomMessages }: { room_id: string; messages: Message[] }) => {
          if (room_id === currentRoom) {
            setMessages(roomMessages);
          }
        });

        connectedSocket.on('error', (error: { msg: string }) => {
          console.error('Chat error:', error.msg);
        });

        connectedSocket.on('user_typing', ({ userId, roomId }: { userId: string; roomId: string }) => {
          if (roomId === currentRoom && userId !== user.username) {
            setTypingUsers((prev) => [...prev.filter(id => id !== userId), userId]);
            
            // Remove typing indicator after 3 seconds
            setTimeout(() => {
              setTypingUsers((prev) => prev.filter(id => id !== userId));
            }, 3000);
          }
        });

        connectedSocket.on('user_stopped_typing', ({ userId, roomId }: { userId: string; roomId: string }) => {
          if (roomId === currentRoom) {
            setTypingUsers((prev) => prev.filter(id => id !== userId));
          }
        });

        connectedSocket.on('room_joined', ({ roomId }: { roomId: string }) => {
          console.log(`✅ Joined room: ${roomId}`);
        });

        connectedSocket.on('room_left', ({ roomId }: { roomId: string }) => {
          console.log(`✅ Left room: ${roomId}`);
        });
        
        setSocket(connectedSocket);
        finalSocket = connectedSocket;
      };
      
      // Update the connection logic to call setupEventHandlers
      currentSocket = tryConnection(pathIndex);
      
      currentSocket.on('connect', () => {
        console.log(`✅ Connected to chat server using path: ${SOCKET_PATHS[pathIndex]}`);
        console.log('🔗 Socket ID:', currentSocket?.id);
        console.log('🚀 Transport:', currentSocket?.io.engine.transport.name);
        setIsConnected(true);
        
        // Enable reconnection now that we found a working path
        currentSocket!.io.opts.reconnection = true;
        currentSocket!.io.opts.reconnectionAttempts = 10;
        currentSocket!.io.opts.reconnectionDelay = 1000;
        currentSocket!.io.opts.reconnectionDelayMax = 5000;
        
        // Set up all event handlers
        setupEventHandlers(currentSocket!);
      });

      currentSocket.on('disconnect', (reason) => {
        console.log('❌ Disconnected from chat server:', reason);
        setIsConnected(false);
      });

      currentSocket.on('connect_error', (error) => {
        console.error(`❌ Connection error with path ${SOCKET_PATHS[pathIndex]}:`, error.message);
        
        // Try next path
        pathIndex++;
        currentSocket?.close();
        
        if (pathIndex < SOCKET_PATHS.length) {
          console.log(`🔄 Trying next path: ${SOCKET_PATHS[pathIndex]}`);
          setTimeout(() => {
            currentSocket = tryConnection(pathIndex);
            // Re-attach event handlers for the new connection attempt
            currentSocket.on('connect', () => {
              console.log(`✅ Connected to chat server using path: ${SOCKET_PATHS[pathIndex]}`);
              setIsConnected(true);
              setupEventHandlers(currentSocket!);
            });
            
            currentSocket.on('connect_error', (error) => {
              console.error(`❌ Connection error with path ${SOCKET_PATHS[pathIndex]}:`, error.message);
              pathIndex++;
              if (pathIndex >= SOCKET_PATHS.length) {
                console.error('❌ All Socket.IO connection paths failed');
                setIsConnected(false);
              }
            });
          }, 1000);
        } else {
          console.error('❌ All Socket.IO connection paths failed');
          setIsConnected(false);
        }
      });

      return () => {
        finalSocket?.close();
        currentSocket?.close();
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
