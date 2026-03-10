import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { Send, MessageCircle, LogOut, Menu, X } from 'lucide-react';

interface Message {
  id: string;
  role: 'user' | 'agent';
  content: string;
  timestamp: Date;
  issue_type?: string;
  ticket_id?: string;
}

interface ChatSession {
  id: string;
  customerId: string;
  messages: Message[];
  tickets: any[];
  activeTicket: any;
}

export const ChatDashboard: React.FC = () => {
  const [session, setSession] = useState<ChatSession>({
    id: `session-${Date.now()}`,
    customerId: `CUST-${Math.random().toString(36).substr(2, 9)}`,
    messages: [],
    tickets: [],
    activeTicket: null
  });

  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [session.messages]);

  const sendMessage = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!inputMessage.trim() || loading) return;

    // Add user message to chat
    const userMessage: Message = {
      id: `msg-${Date.now()}`,
      role: 'user',
      content: inputMessage,
      timestamp: new Date()
    };

    setSession(prev => ({
      ...prev,
      messages: [...prev.messages, userMessage]
    }));

    setInputMessage('');
    setLoading(true);

    try {
      // Call backend API
      const response = await axios.post('/api/support/chat', {
        customer_id: session.customerId,
        message: inputMessage,
        session_id: session.id
      });

      const agentMessage: Message = {
        id: `msg-${Date.now() + 1}`,
        role: 'agent',
        content: response.data.response,
        timestamp: new Date(),
        issue_type: response.data.issue_type,
        ticket_id: response.data.ticket_id
      };

      setSession(prev => ({
        ...prev,
        messages: [...prev.messages, agentMessage],
        activeTicket: {
          id: response.data.ticket_id,
          status: response.data.resolved ? 'resolved' : 'open',
          issue_type: response.data.issue_type,
          satisfaction_score: response.data.satisfaction_score
        }
      }));
    } catch (error) {
      console.error('Failed to send message:', error);
      const errorMessage: Message = {
        id: `msg-${Date.now() + 1}`,
        role: 'agent',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date()
      };
      setSession(prev => ({
        ...prev,
        messages: [...prev.messages, errorMessage]
      }));
    } finally {
      setLoading(false);
    }
  };

  const escalateTicket = async () => {
    if (!session.activeTicket) return;

    try {
      await axios.post('/api/support/escalate', {
        ticket_id: session.activeTicket.id,
        reason: 'Customer requested escalation',
        customer_id: session.customerId
      });

      setSession(prev => ({
        ...prev,
        activeTicket: {
          ...prev.activeTicket,
          status: 'escalated'
        }
      }));
    } catch (error) {
      console.error('Escalation failed:', error);
    }
  };

  const rateSatisfaction = async (score: number) => {
    if (!session.activeTicket) return;

    try {
      await axios.post('/api/support/rate', {
        ticket_id: session.activeTicket.id,
        satisfaction_score: score,
        feedback: 'Customer rating'
      });

      alert(`Thank you! Your rating of ${score}/5 has been recorded.`);
    } catch (error) {
      console.error('Rating failed:', error);
    }
  };

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <div className={`${sidebarOpen ? 'w-64' : 'w-0'} bg-gray-900 text-white transition-all duration-300 overflow-hidden flex flex-col`}>
        <div className="p-4 border-b border-gray-700">
          <div className="flex items-center gap-2">
            <MessageCircle className="w-6 h-6" />
            <span className="font-bold text-lg">Support Chat</span>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-4">
          <div className="space-y-2">
            <div className="text-xs text-gray-400">SESSION</div>
            <div className="text-sm font-mono bg-gray-800 p-2 rounded">
              {session.customerId}
            </div>

            {session.activeTicket && (
              <>
                <div className="text-xs text-gray-400 mt-4">ACTIVE TICKET</div>
                <div className="text-sm bg-gray-800 p-2 rounded space-y-1">
                  <div className="text-blue-400">{session.activeTicket.id}</div>
                  <div className="text-gray-400">
                    Type: {session.activeTicket.issue_type}
                  </div>
                  <div className="text-gray-400">
                    Status: <span className={session.activeTicket.status === 'resolved' ? 'text-green-400' : 'text-yellow-400'}>
                      {session.activeTicket.status}
                    </span>
                  </div>
                </div>
              </>
            )}
          </div>
        </div>

        <div className="p-4 border-t border-gray-700">
          <button className="w-full flex items-center justify-center gap-2 bg-red-600 hover:bg-red-700 px-4 py-2 rounded transition">
            <LogOut className="w-4 h-4" />
            Logout
          </button>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="bg-white border-b border-gray-200 p-4 flex items-center justify-between">
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="lg:hidden p-2 hover:bg-gray-100 rounded"
          >
            {sidebarOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
          <h1 className="text-2xl font-bold text-gray-900">Customer Service Dashboard</h1>
          <div className="text-sm text-gray-500">
            Messages: {session.messages.length}
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {session.messages.length === 0 ? (
            <div className="flex items-center justify-center h-full">
              <div className="text-center">
                <MessageCircle className="w-16 h-16 mx-auto text-gray-300 mb-4" />
                <h2 className="text-2xl font-bold text-gray-900 mb-2">Start a Conversation</h2>
                <p className="text-gray-500">
                  Ask us anything! We're here to help with FAQs, resets, refunds, and more.
                </p>
              </div>
            </div>
          ) : (
            <>
              {session.messages.map((msg) => (
                <div
                  key={msg.id}
                  className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                      msg.role === 'user'
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-200 text-gray-900'
                    }`}
                  >
                    <p className="text-sm">{msg.content}</p>
                    <div className={`text-xs mt-1 ${
                      msg.role === 'user' ? 'text-blue-100' : 'text-gray-500'
                    }`}>
                      {msg.timestamp.toLocaleTimeString()}
                    </div>
                    {msg.issue_type && (
                      <div className={`text-xs mt-1 ${msg.role === 'user' ? 'text-blue-100' : 'text-gray-600'}`}>
                        Type: {msg.issue_type}
                      </div>
                    )}
                  </div>
                </div>
              ))}
              <div ref={messagesEndRef} />
            </>
          )}
        </div>

        {/* Action Buttons */}
        {session.activeTicket && (
          <div className="px-4 py-2 bg-gray-100 border-b border-gray-200 space-x-2 flex">
            {session.activeTicket.status === 'open' && (
              <button
                onClick={escalateTicket}
                className="px-4 py-2 bg-orange-600 hover:bg-orange-700 text-white rounded transition text-sm"
              >
                Escalate to Agent
              </button>
            )}
            {session.activeTicket.status === 'resolved' && (
              <div className="flex gap-2">
                <span className="text-sm text-gray-600">Rate your experience:</span>
                {[1, 2, 3, 4, 5].map((score) => (
                  <button
                    key={score}
                    onClick={() => rateSatisfaction(score)}
                    className="px-2 py-1 bg-gray-300 hover:bg-yellow-400 rounded transition text-sm"
                  >
                    {score}⭐
                  </button>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Input Area */}
        <form
          onSubmit={sendMessage}
          className="bg-white border-t border-gray-200 p-4"
        >
          <div className="flex gap-2">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              placeholder="Type your message here..."
              disabled={loading}
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500 disabled:bg-gray-100"
            />
            <button
              type="submit"
              disabled={loading || !inputMessage.trim()}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition disabled:bg-gray-400 flex items-center gap-2"
            >
              {loading ? (
                <>
                  <div className="animate-spin w-4 h-4 border-2 border-white border-t-transparent rounded-full" />
                  Sending...
                </>
              ) : (
                <>
                  <Send className="w-4 h-4" />
                  Send
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ChatDashboard;
