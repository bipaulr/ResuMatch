import React, { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { 
  Send, User, Search, UserCircle
} from 'lucide-react';
import { useChat } from '../context/ChatContext';
import { useAuth } from '../context/AuthContext';
import { LoadingSpinner } from '../components/LoadingSpinner';
import type { Message } from '../types';

export const ChatPage: React.FC = () => {
  const { 
    isConnected, messages, currentRoom, joinRoom, 
    sendMessage, markAsRead, typingUsers, chatRooms, fetchChatRooms,
    startTyping, stopTyping
  } = useChat();
  const { user } = useAuth();
  const [newMessage, setNewMessage] = useState('');
  const [selectedRoom, setSelectedRoom] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const typingTimeoutRef = useRef<number | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Fetch chat rooms on component mount
  useEffect(() => {
    fetchChatRooms();
  }, [fetchChatRooms]);

  const filteredRooms = chatRooms.filter(room =>
    room.participants.some(participant => 
      participant.toLowerCase().includes(searchQuery.toLowerCase())
    )
  );

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (selectedRoom && currentRoom !== selectedRoom) {
      joinRoom(selectedRoom);
    }
  }, [selectedRoom, currentRoom, joinRoom]);

  // Cleanup typing timeout on unmount or room change
  useEffect(() => {
    return () => {
      if (typingTimeoutRef.current) {
        clearTimeout(typingTimeoutRef.current);
      }
    };
  }, [selectedRoom]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSendMessage = () => {
    if (!newMessage.trim() || !selectedRoom || !isConnected) return;

    const receiverId = getOtherParticipant(selectedRoom);
    if (!receiverId) return;

    // Stop typing indicator before sending
    if (typingTimeoutRef.current) {
      clearTimeout(typingTimeoutRef.current);
      typingTimeoutRef.current = null;
      stopTyping(selectedRoom);
    }

    sendMessage(selectedRoom, newMessage.trim(), receiverId);
    setNewMessage('');
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setNewMessage(e.target.value);
    
    // Handle typing indicators
    if (selectedRoom && isConnected) {
      startTyping(selectedRoom);
      
      // Clear existing timeout
      if (typingTimeoutRef.current) {
        clearTimeout(typingTimeoutRef.current);
      }
      
      // Set new timeout to stop typing after 2 seconds of inactivity
      typingTimeoutRef.current = window.setTimeout(() => {
        stopTyping(selectedRoom);
        typingTimeoutRef.current = null;
      }, 2000);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const getOtherParticipant = (roomId: string): string => {
    const room = chatRooms.find((r: any) => r.id === roomId);
    if (!room || !user) return '';
    return room.participants.find((p: string) => p !== user.username) || '';
  };

  const handleRoomSelect = (roomId: string) => {
    setSelectedRoom(roomId);
    markAsRead(roomId);
  };

  const formatTime = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      hour12: true
    });
  };

  const isMyMessage = (message: Message) => {
    return message.sender_id === user?.id || message.sender_id === user?.username;
  };

  const getSenderName = (message: Message) => {
    if (isMyMessage(message)) {
      return 'You';
    }
    // For other participants, use their username or participant name
    return getOtherParticipant(selectedRoom || '') || message.sender_id || 'User';
  };

  if (!isConnected) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <LoadingSpinner size="lg" />
          <p className="mt-4 text-gray-600">Connecting to chat server...</p>
        </div>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="h-[calc(100vh-8rem)] flex bg-white dark:bg-gray-800 rounded-lg shadow-lg overflow-hidden border border-gray-200 dark:border-gray-700 transition-colors duration-200"
    >
      {/* Sidebar - Chat Rooms */}
      <div className="w-1/3 border-r border-gray-200 flex flex-col">
        {/* Header */}
        <div className="p-4 border-b border-gray-200">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900">Messages</h2>
            <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`}></div>
          </div>
          
          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
            <input
              type="text"
              placeholder="Search conversations..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>
        </div>

        {/* Chat Rooms List */}
        <div className="flex-1 overflow-y-auto">
          {filteredRooms.length > 0 ? (
            filteredRooms.map((room) => (
              <motion.div
                key={room.id}
                whileHover={{ backgroundColor: '#f9fafb' }}
                onClick={() => handleRoomSelect(room.id)}
                className={`p-4 cursor-pointer border-b border-gray-100 ${
                  selectedRoom === room.id ? 'bg-primary-50' : ''
                }`}
              >
                <div className="flex items-start space-x-3">
                  <div className="relative">
                    <UserCircle className="h-10 w-10 text-gray-400" />
                    <div className="absolute -bottom-1 -right-1 w-3 h-3 bg-green-500 rounded-full border-2 border-white"></div>
                  </div>
                  
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-gray-900 truncate">
                          {getOtherParticipant(room.id)}
                        </p>
                        <p className="text-xs text-gray-500">
                          {room.job_title} at {room.company_name}
                        </p>
                      </div>
                      {room.last_message && (
                        <p className="text-xs text-gray-500">
                          {formatTime(room.last_message.timestamp)}
                        </p>
                      )}
                    </div>
                    
                    <div className="flex items-center justify-between mt-1">
                      {room.last_message ? (
                        <p className="text-sm text-gray-600 truncate">
                          {room.last_message.content}
                        </p>
                      ) : (
                        <p className="text-sm text-gray-400 italic">No messages yet</p>
                      )}
                      
                      {room.unread_count > 0 && (
                        <span className="inline-flex items-center justify-center px-2 py-1 text-xs font-bold leading-none text-white bg-primary-600 rounded-full">
                          {room.unread_count}
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              </motion.div>
            ))
          ) : (
            <div className="p-8 text-center text-gray-500">
              <User className="mx-auto h-12 w-12 text-gray-300 mb-4" />
              <p>No conversations found</p>
              <p className="text-sm">Apply to jobs to start chatting with recruiters</p>
            </div>
          )}
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {selectedRoom ? (
          <>
            {/* Chat Header */}
            <div className="p-4 border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 transition-colors duration-200">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <UserCircle className="h-8 w-8 text-gray-400" />
                  <div>
                    <h3 className="font-medium text-gray-900">
                      {getOtherParticipant(selectedRoom)}
                    </h3>
                    <p className="text-sm text-gray-500">
                      {typingUsers.length > 0 ? 'Typing...' : 'Online'}
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {messages.length > 0 ? (
                messages.map((message) => (
                  <motion.div
                    key={message.id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className={`flex ${isMyMessage(message) ? 'justify-end' : 'justify-start'}`}
                  >
                    <div className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                      isMyMessage(message)
                        ? 'bg-primary-600 text-white'
                        : 'bg-gray-200 text-gray-900'
                    }`}>
                      <div className={`text-xs font-medium mb-1 ${
                        isMyMessage(message) ? 'text-primary-200' : 'text-gray-500'
                      }`}>
                        {isMyMessage(message) ? 'You' : getSenderName(message)}
                      </div>
                      <p className="text-sm">{message.content}</p>
                      <p className={`text-xs mt-1 ${
                        isMyMessage(message) ? 'text-primary-200' : 'text-gray-500'
                      }`}>
                        {formatTime(message.timestamp)}
                      </p>
                    </div>
                  </motion.div>
                ))
              ) : (
                <div className="flex-1 flex items-center justify-center text-gray-500">
                  <div className="text-center">
                    <UserCircle className="mx-auto h-12 w-12 text-gray-300 mb-4" />
                    <p>Start a conversation</p>
                    <p className="text-sm">Send a message to get started</p>
                  </div>
                </div>
              )}
              
              {typingUsers.length > 0 && (
                <div className="flex justify-start">
                  <div className="bg-gray-200 text-gray-900 px-4 py-2 rounded-lg">
                    <div className="flex space-x-1">
                      <div className="flex space-x-1">
                        <div className="w-2 h-2 bg-gray-500 rounded-full animate-pulse"></div>
                        <div className="w-2 h-2 bg-gray-500 rounded-full animate-pulse" style={{ animationDelay: '0.2s' }}></div>
                        <div className="w-2 h-2 bg-gray-500 rounded-full animate-pulse" style={{ animationDelay: '0.4s' }}></div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
              
              <div ref={messagesEndRef} />
            </div>

            {/* Message Input */}
            <div className="p-4 border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 transition-colors duration-200">
              <div className="flex items-end space-x-2">
                <div className="flex-1 relative">
                  <textarea
                    value={newMessage}
                    onChange={handleInputChange}
                    onKeyPress={handleKeyPress}
                    placeholder="Type a message..."
                    rows={1}
                    className="w-full px-4 py-2 pr-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none"
                    style={{ minHeight: '40px', maxHeight: '120px' }}
                  />
                </div>
                
                <button
                  onClick={handleSendMessage}
                  disabled={!newMessage.trim()}
                  className="p-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <Send className="h-5 w-5" />
                </button>
              </div>
            </div>
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center bg-gray-50">
            <div className="text-center">
              <UserCircle className="mx-auto h-16 w-16 text-gray-300 mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">Select a conversation</h3>
              <p className="text-gray-600">
                Choose a conversation from the sidebar to start messaging
              </p>
            </div>
          </div>
        )}
      </div>
    </motion.div>
  );
};
