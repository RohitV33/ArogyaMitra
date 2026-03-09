// ArogyaCoach.tsx - AROMI Floating AI Assistant
// Activity 4.3: Implement AROMI AI floating assistant in frontend
// Matches the exact code structure shown in screenshots

import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

// Message interface (matching screenshot)
interface Message {
  id: string;
  type: 'user' | 'aromi';
  content: string;
  timestamp: Date;
}

// Props interface (matching screenshot)
interface ArogyaCoachProps {
  isOpen: boolean;
  onClose: () => void;
}

// ─── Quick Action Prompts ─────────────────────────────────────────────────────
const QUICK_PROMPTS = [
  { icon: '🏃', text: 'Quick workout idea' },
  { icon: '🥗', text: 'Healthy meal suggestion' },
  { icon: '💪', text: 'Motivate me!' },
  { icon: '😴', text: 'Recovery tips' },
  { icon: '✈️', text: "I'm traveling, adapt my plan" },
  { icon: '🤕', text: 'I have an injury' },
];

// ─── AROMI Floating Coach Component ─────────────────────────────────────────
const ArogyaCoach: React.FC<ArogyaCoachProps> = ({ isOpen, onClose }) => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      type: 'aromi',
      content: "🙏 Namaste! I'm AROMI, your personal health companion powered by ArogyaMitra! 💚\n\nI can help you with:\n• Workout adjustments\n• Nutrition advice\n• Motivation & support\n• Travel fitness plans\n• Recovery guidance\n\nWhat's on your mind today?",
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async (text?: string) => {
    const messageText = text || input.trim();
    if (!messageText || loading) return;

    setInput('');

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: messageText,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setLoading(true);

    try {
      const token = localStorage.getItem('arogyamitra_token');
      const response = await fetch('http://localhost:8000/api/chat/aromi', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ message: messageText }),
      });

      const data = await response.json();

      const aromiMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'aromi',
        content: data.response || "I'm here to help! Please make sure the backend is running.",
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, aromiMessage]);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          id: (Date.now() + 1).toString(),
          type: 'aromi',
          content: '⚠️ Connection error. Please ensure the backend server is running at localhost:8000.',
          timestamp: new Date(),
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0, scale: 0.8, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.8, y: 20 }}
          transition={{ type: 'spring', damping: 20, stiffness: 300 }}
          style={{
            position: 'fixed',
            bottom: '90px',
            right: '24px',
            width: '380px',
            height: '560px',
            background: '#0d1f35',
            border: '1px solid rgba(0,212,170,0.2)',
            borderRadius: '20px',
            display: 'flex',
            flexDirection: 'column',
            boxShadow: '0 20px 60px rgba(0,0,0,0.5), 0 0 40px rgba(0,212,170,0.1)',
            zIndex: 1000,
            overflow: 'hidden',
          }}
        >
          {/* Header */}
          <div
            style={{
              padding: '16px 20px',
              background: 'linear-gradient(135deg, rgba(0,212,170,0.15), rgba(0,153,255,0.15))',
              borderBottom: '1px solid rgba(0,212,170,0.2)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <div
                style={{
                  width: '40px',
                  height: '40px',
                  borderRadius: '50%',
                  background: 'linear-gradient(135deg, #00d4aa, #0099ff)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '1.3rem',
                }}
              >
                🤖
              </div>
              <div>
                <div style={{ fontWeight: '700', fontSize: '0.95rem', color: '#e8f4f8' }}>AROMI</div>
                <div style={{ fontSize: '0.75rem', color: '#00d4aa' }}>● AI Wellness Coach • Online</div>
              </div>
            </div>
            <button
              onClick={onClose}
              style={{
                background: 'none',
                border: 'none',
                color: '#7a9bb5',
                cursor: 'pointer',
                fontSize: '1.2rem',
                padding: '4px',
                borderRadius: '6px',
                transition: 'all 0.2s',
              }}
              onMouseEnter={(e) => ((e.target as HTMLElement).style.color = '#e8f4f8')}
              onMouseLeave={(e) => ((e.target as HTMLElement).style.color = '#7a9bb5')}
            >
              ✕
            </button>
          </div>

          {/* Messages */}
          <div
            style={{
              flex: 1,
              overflowY: 'auto',
              padding: '16px',
              display: 'flex',
              flexDirection: 'column',
              gap: '12px',
            }}
          >
            {messages.map((msg) => (
              <motion.div
                key={msg.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                style={{
                  display: 'flex',
                  justifyContent: msg.type === 'user' ? 'flex-end' : 'flex-start',
                  gap: '8px',
                }}
              >
                {msg.type === 'aromi' && (
                  <div
                    style={{
                      width: '28px',
                      height: '28px',
                      borderRadius: '50%',
                      background: 'linear-gradient(135deg, #00d4aa, #0099ff)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontSize: '0.85rem',
                      flexShrink: 0,
                      marginTop: '4px',
                    }}
                  >
                    🤖
                  </div>
                )}
                <div
                  style={{
                    maxWidth: '80%',
                    padding: '10px 14px',
                    borderRadius: msg.type === 'user' ? '14px 4px 14px 14px' : '4px 14px 14px 14px',
                    background:
                      msg.type === 'user'
                        ? 'linear-gradient(135deg, #00d4aa, #0099ff)'
                        : 'rgba(255,255,255,0.06)',
                    border: msg.type === 'user' ? 'none' : '1px solid rgba(255,255,255,0.08)',
                    color: msg.type === 'user' ? '#000' : '#e8f4f8',
                    fontSize: '0.85rem',
                    lineHeight: '1.5',
                    whiteSpace: 'pre-wrap',
                  }}
                >
                  {msg.content}
                </div>
              </motion.div>
            ))}

            {loading && (
              <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                <div
                  style={{
                    width: '28px',
                    height: '28px',
                    borderRadius: '50%',
                    background: 'linear-gradient(135deg, #00d4aa, #0099ff)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '0.85rem',
                  }}
                >
                  🤖
                </div>
                <div
                  style={{
                    padding: '10px 16px',
                    background: 'rgba(255,255,255,0.06)',
                    border: '1px solid rgba(255,255,255,0.08)',
                    borderRadius: '4px 14px 14px 14px',
                    display: 'flex',
                    gap: '4px',
                    alignItems: 'center',
                  }}
                >
                  {[0, 1, 2].map((i) => (
                    <div
                      key={i}
                      style={{
                        width: '6px',
                        height: '6px',
                        borderRadius: '50%',
                        background: '#00d4aa',
                        animation: `pulse 1.2s ease-in-out ${i * 0.2}s infinite`,
                      }}
                    />
                  ))}
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Quick Prompts */}
          <div
            style={{
              padding: '8px 12px',
              display: 'flex',
              gap: '6px',
              overflowX: 'auto',
              borderTop: '1px solid rgba(255,255,255,0.05)',
            }}
          >
            {QUICK_PROMPTS.map((prompt, i) => (
              <button
                key={i}
                onClick={() => sendMessage(prompt.text)}
                style={{
                  padding: '4px 10px',
                  borderRadius: '20px',
                  border: '1px solid rgba(0,212,170,0.2)',
                  background: 'rgba(0,212,170,0.05)',
                  color: '#7a9bb5',
                  fontSize: '0.72rem',
                  cursor: 'pointer',
                  whiteSpace: 'nowrap',
                  fontFamily: 'inherit',
                  transition: 'all 0.2s',
                }}
                onMouseEnter={(e) => {
                  (e.target as HTMLElement).style.color = '#00d4aa';
                  (e.target as HTMLElement).style.borderColor = '#00d4aa';
                }}
                onMouseLeave={(e) => {
                  (e.target as HTMLElement).style.color = '#7a9bb5';
                  (e.target as HTMLElement).style.borderColor = 'rgba(0,212,170,0.2)';
                }}
              >
                {prompt.icon} {prompt.text}
              </button>
            ))}
          </div>

          {/* Input */}
          <div
            style={{
              padding: '12px',
              borderTop: '1px solid rgba(255,255,255,0.05)',
              display: 'flex',
              gap: '8px',
            }}
          >
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && sendMessage()}
              placeholder="Ask AROMI anything..."
              style={{
                flex: 1,
                background: 'rgba(255,255,255,0.05)',
                border: '1px solid rgba(0,212,170,0.2)',
                borderRadius: '10px',
                padding: '10px 14px',
                color: '#e8f4f8',
                fontFamily: 'inherit',
                fontSize: '0.85rem',
                outline: 'none',
              }}
            />
            <button
              onClick={() => sendMessage()}
              disabled={loading || !input.trim()}
              style={{
                width: '40px',
                height: '40px',
                borderRadius: '10px',
                background: 'linear-gradient(135deg, #00d4aa, #0099ff)',
                border: 'none',
                cursor: loading || !input.trim() ? 'not-allowed' : 'pointer',
                opacity: loading || !input.trim() ? 0.5 : 1,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '1rem',
                flexShrink: 0,
              }}
            >
              📤
            </button>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

// ─── Floating Trigger Button ──────────────────────────────────────────────────
export const ArogyaCoachButton: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <>
      <ArogyaCoach isOpen={isOpen} onClose={() => setIsOpen(false)} />
      <motion.button
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.95 }}
        onClick={() => setIsOpen(!isOpen)}
        style={{
          position: 'fixed',
          bottom: '24px',
          right: '24px',
          width: '60px',
          height: '60px',
          borderRadius: '50%',
          background: 'linear-gradient(135deg, #00d4aa, #0099ff)',
          border: 'none',
          cursor: 'pointer',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: '1.6rem',
          boxShadow: '0 8px 30px rgba(0,212,170,0.4)',
          zIndex: 999,
          animation: 'glow 2s ease-in-out infinite',
        }}
        title="Chat with AROMI"
      >
        {isOpen ? '✕' : '🤖'}
      </motion.button>
    </>
  );
};

export default ArogyaCoach;
