import { useState, useRef, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import api from '../lib/api';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  suggestions?: string[];
}

export default function Chat() {
  const { t } = useTranslation();
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [provider, setProvider] = useState('gemini');
  const [sessionId, setSessionId] = useState<string | null>(null);
  const chatRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    chatRef.current?.scrollTo(0, chatRef.current.scrollHeight);
  }, [messages]);

  const send = async (message?: string) => {
    const text = message || input.trim();
    if (!text) return;
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: text }]);
    setLoading(true);

    try {
      const res = await api.post('/chat/', {
        message: text,
        session_id: sessionId,
        llm_provider: provider,
      });
      setSessionId(res.data.session_id);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: res.data.response,
        suggestions: res.data.suggestions,
      }]);
    } catch (err: unknown) {
      const axiosErr = err as { response?: { data?: { detail?: string } } };
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: axiosErr.response?.data?.detail || 'Error occurred',
      }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      <nav className="bg-gradient-to-r from-indigo-500 to-purple-600 text-white px-6 py-4 flex justify-between items-center">
        <Link to="/" className="text-xl font-bold">{t('app_name')}</Link>
        <select value={provider} onChange={e => setProvider(e.target.value)}
          className="bg-white/20 border border-white/30 rounded px-3 py-1 text-sm">
          <option value="gemini">Gemini</option>
          <option value="claude">Claude</option>
        </select>
      </nav>

      <div ref={chatRef} className="flex-1 overflow-y-auto p-6 space-y-4">
        {messages.length === 0 && (
          <div className="text-center text-gray-400 mt-20">
            <p className="text-lg">{t('welcome')}</p>
            <p>{t('ask_anything')}</p>
          </div>
        )}
        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[70%] rounded-2xl px-5 py-3 ${
              msg.role === 'user'
                ? 'bg-gradient-to-r from-indigo-500 to-purple-600 text-white'
                : 'bg-white border shadow-sm'
            }`}>
              <p className="whitespace-pre-wrap">{msg.content}</p>
              {msg.suggestions && (
                <div className="flex flex-wrap gap-2 mt-3">
                  {msg.suggestions.map((s, j) => (
                    <button key={j} onClick={() => send(s)}
                      className="text-xs border border-indigo-400 text-indigo-600 rounded-full px-3 py-1 hover:bg-indigo-50">
                      {s}
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-white border shadow-sm rounded-2xl px-5 py-3 text-gray-400">
              {t('loading')}
            </div>
          </div>
        )}
      </div>

      <div className="border-t bg-white px-6 py-4 flex gap-3">
        <input value={input} onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && send()}
          placeholder={t('ask_anything')}
          className="flex-1 border rounded-full px-5 py-3 focus:outline-none focus:ring-2 focus:ring-indigo-500" />
        <button onClick={() => send()} disabled={loading}
          className="bg-gradient-to-r from-indigo-500 to-purple-600 text-white rounded-full px-8 py-3 font-semibold hover:opacity-90 disabled:opacity-50">
          {t('send')}
        </button>
      </div>
    </div>
  );
}
