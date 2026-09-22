import { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Send, ShieldAlert, LogOut, User, Bot, Loader2, ServerCrash, History, Trash2 } from 'lucide-react';
import api from '../services/api';
import RiskPassport from '../components/RiskPassport';

export default function Chat() {
  const navigate = useNavigate();
  
  // State for current chat
  const [messages, setMessages] = useState([
    { role: 'ai', type: 'greeting', content: 'Hello! I am ML-Guardian. Describe your Machine Learning problem, or ask me to audit an existing model.' }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  
  // State for sidebar history
  const [historyList, setHistoryList] = useState([]);
  
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom of chat
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };
  useEffect(() => scrollToBottom(), [messages]);

  // Fetch Chat History on mount
  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const response = await api.get('/chat/history');
        setHistoryList(response.data.history);
      } catch (error) {
        console.error("Could not fetch chat history", error);
      }
    };
    fetchHistory();
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/login');
  };

  // Clear Chat History
  const handleClearHistory = async () => {
    if (!window.confirm("Are you sure you want to permanently delete all your chat history?")) return;
    try {
      await api.delete('/chat/history');
      setHistoryList([]);
      setMessages([{ role: 'ai', type: 'greeting', content: 'History cleared. How can I help you today?' }]);
    } catch (error) {
      console.error("Failed to clear history", error);
      alert("Failed to clear history.");
    }
  };

  // Load a past chat from the sidebar
  const loadPastChat = (session) => {
    setMessages([
      { role: 'user', content: session.user_query },
      { role: 'ai', type: 'response', data: session.agent_response }
    ]);
  };

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage = { role: 'user', content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await api.post('/chat/', { message: userMessage.content });
      const aiMessage = { role: 'ai', type: 'response', data: response.data };
      setMessages((prev) => [...prev, aiMessage]);
      
      // Instantly add the new chat to the top of the sidebar history list
      const newHistoryItem = {
        user_query: userMessage.content,
        intent: response.data.query_intent || 'UNKNOWN',
        agent_response: response.data
      };
      setHistoryList((prev) => [newHistoryItem, ...prev]);

    } catch (err) {
      const errorMsg = err.response?.data?.detail || err.message || "Failed to reach backend.";
      setMessages((prev) => [...prev, { role: 'ai', type: 'error', content: errorMsg }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-slate-50 font-sans">
      
      {/* Navbar */}
      <header className="bg-indigo-950 text-white shadow-md py-4 px-6 flex justify-between items-center z-10 shrink-0">
        <div className="flex items-center gap-3">
          <div className="bg-indigo-800 p-2 rounded-lg">
            <ShieldAlert className="w-6 h-6 text-indigo-300" />
          </div>
          <h1 className="text-xl font-bold tracking-tight">ML-Guardian</h1>
        </div>
        <button 
          onClick={handleLogout}
          className="flex items-center gap-2 text-indigo-200 hover:text-white transition-colors text-sm font-medium bg-indigo-900/50 hover:bg-indigo-800 px-4 py-2 rounded-lg"
        >
          <LogOut className="w-4 h-4" /> Logout
        </button>
      </header>

      {/* Main Layout (Sidebar + Chat) */}
      <div className="flex flex-1 overflow-hidden">
        
        {/* Sidebar History (Hidden on mobile) */}
        <aside className="w-72 bg-gray-900 text-gray-300 hidden md:flex flex-col border-r border-gray-800 shrink-0">
          <div className="p-5 font-bold text-white border-b border-gray-800 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <History className="w-5 h-5 text-indigo-400" />
              Recent Audits
            </div>
            {historyList.length > 0 && (
              <button 
                onClick={handleClearHistory} 
                className="text-gray-500 hover:text-red-400 transition-colors p-1 rounded hover:bg-gray-800" 
                title="Clear History"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            )}
          </div>
          <div className="flex-1 overflow-y-auto p-3 space-y-2 custom-scrollbar">
            {historyList.length === 0 ? (
              <p className="text-sm text-gray-500 text-center mt-6">No history yet.</p>
            ) : (
              historyList.map((item, index) => (
                <button 
                  key={index} 
                  onClick={() => loadPastChat(item)}
                  className="w-full text-left p-3 rounded-lg hover:bg-gray-800 transition-colors border border-transparent hover:border-gray-700 group"
                >
                  <p className="text-sm text-gray-100 truncate group-hover:text-white transition-colors">
                    {item.user_query}
                  </p>
                  <span className="text-xs text-indigo-400 mt-1.5 block font-medium">
                    {item.intent?.replace(/_/g, ' ')}
                  </span>
                </button>
              ))
            )}
          </div>
        </aside>

        {/* Chat Area */}
        <div className="flex-1 flex flex-col min-w-0">
          <main className="flex-1 overflow-y-auto p-4 md:p-8 space-y-6">
            <div className="max-w-4xl mx-auto space-y-6">
              {messages.map((msg, index) => (
                <div key={index} className={`flex gap-4 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  
                  {/* AI Avatar */}
                  {msg.role === 'ai' && (
                    <div className="w-10 h-10 rounded-full bg-indigo-100 flex items-center justify-center shrink-0 border border-indigo-200 mt-1">
                      {msg.type === 'error' ? <ServerCrash className="w-5 h-5 text-red-500" /> : <Bot className="w-5 h-5 text-indigo-600" />}
                    </div>
                  )}

                  {/* Message Bubble */}
                  <div className={`max-w-[85%] rounded-2xl p-5 shadow-sm border ${
                    msg.role === 'user' 
                      ? 'bg-indigo-600 text-white border-indigo-700 rounded-tr-none' 
                      : msg.type === 'error'
                        ? 'bg-red-50 text-red-700 border-red-200 rounded-tl-none'
                        : msg.type === 'response' 
                          ? 'bg-transparent border-none shadow-none p-0 w-full' 
                          : 'bg-white text-gray-800 border-gray-200 rounded-tl-none'
                  }`}>
                    
                    {/* Render simple text (Greeting/Error/User) */}
                    {(msg.type === 'greeting' || msg.type === 'error' || msg.role === 'user') && (
                      <p className="whitespace-pre-wrap leading-relaxed">{msg.content}</p>
                    )}

                    {/* Render the Beautiful ML Risk Passport */}
                    {msg.type === 'response' && (
                      <RiskPassport data={msg.data} />
                    )}
                  </div>

                  {/* User Avatar */}
                  {msg.role === 'user' && (
                    <div className="w-10 h-10 rounded-full bg-slate-200 flex items-center justify-center shrink-0 border border-slate-300 mt-1">
                      <User className="w-5 h-5 text-slate-600" />
                    </div>
                  )}
                </div>
              ))}

              {/* Loading Indicator */}
              {loading && (
                <div className="flex gap-4 justify-start animate-pulse">
                  <div className="w-10 h-10 rounded-full bg-indigo-100 flex items-center justify-center shrink-0 border border-indigo-200">
                    <Loader2 className="w-5 h-5 text-indigo-600 animate-spin" />
                  </div>
                  <div className="bg-white border border-gray-200 rounded-2xl rounded-tl-none p-5 shadow-sm flex items-center gap-3">
                    <div className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce" style={{ animationDelay: '0.15s' }}></div>
                    <div className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce" style={{ animationDelay: '0.3s' }}></div>
                    <span className="text-sm text-gray-500 ml-2 font-medium">Orchestrating agents...</span>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          </main>

          {/* Input Area */}
          <footer className="bg-white border-t border-gray-200 p-4 shrink-0">
            <form onSubmit={handleSend} className="max-w-4xl mx-auto relative">
              <input
                type="text"
                className="w-full bg-gray-50 border border-gray-300 rounded-full py-4 pl-6 pr-14 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white transition-all shadow-sm"
                placeholder="Ask a machine learning question..."
                value={input}
                onChange={(e) => setInput(e.target.value)}
                disabled={loading}
              />
              <button
                type="submit"
                disabled={loading || !input.trim()}
                className="absolute right-2 top-2 bottom-2 bg-indigo-600 text-white rounded-full p-3 hover:bg-indigo-700 transition-colors disabled:bg-gray-300 disabled:text-gray-500 flex items-center justify-center"
              >
                <Send className="w-5 h-5 ml-1" />
              </button>
            </form>
            <p className="text-center text-xs text-gray-400 mt-3 font-medium">
              ML-Guardian can make mistakes. Consider verifying critical AI ethics advice.
            </p>
          </footer>
        </div>
      </div>
    </div>
  );
}
