import { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Send, ShieldAlert, LogOut, User, Bot, Loader2, ServerCrash, 
  History, Trash2, Sparkles, BrainCircuit, ShieldCheck, BookOpen,
  MessageSquarePlus, Zap, ArrowRight, Square
} from 'lucide-react';
import api from '../services/api';
import RiskPassport from '../components/RiskPassport';

// ── Suggested Prompts for the Welcome Screen ──
const SUGGESTED_PROMPTS = [
  { 
    icon: <BrainCircuit className="w-5 h-5 text-violet-500" />,
    label: "Model Recommendation",
    prompt: "I want to classify spam emails with 10,000 samples, what model should I use?",
    color: "from-violet-500/10 to-purple-500/10 hover:from-violet-500/20 hover:to-purple-500/20 border-violet-200"
  },
  {
    icon: <ShieldCheck className="w-5 h-5 text-rose-500" />,
    label: "Risk Analysis",
    prompt: "Analyze the ethical risks of using facial recognition for employee attendance",
    color: "from-rose-500/10 to-pink-500/10 hover:from-rose-500/20 hover:to-pink-500/20 border-rose-200"
  },
  {
    icon: <BookOpen className="w-5 h-5 text-cyan-500" />,
    label: "Learn ML Concepts",
    prompt: "Explain what gradient descent is and why it matters in deep learning",
    color: "from-cyan-500/10 to-blue-500/10 hover:from-cyan-500/20 hover:to-blue-500/20 border-cyan-200"
  },
  {
    icon: <Zap className="w-5 h-5 text-amber-500" />,
    label: "Quick Audit",
    prompt: "I'm training a loan approval model on historical bank data, what biases should I watch for?",
    color: "from-amber-500/10 to-orange-500/10 hover:from-amber-500/20 hover:to-orange-500/20 border-amber-200"
  }
];

// ── Agent Pipeline Steps (shown during loading) ──
const AGENT_STEPS = [
  { label: "Sanitizing input", icon: "🛡️" },
  { label: "Classifying intent", icon: "🧠" },
  { label: "Routing to specialist agents", icon: "🔀" },
  { label: "Running RAG + Web Search", icon: "🔍" },
  { label: "Auditing for bias & risk", icon: "⚖️" },
  { label: "Generating Risk Passport", icon: "📋" },
];

export default function Chat() {
  const navigate = useNavigate();
  
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [historyList, setHistoryList] = useState([]);
  const [currentStep, setCurrentStep] = useState(0);
  
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);
  const abortControllerRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };
  useEffect(() => scrollToBottom(), [messages]);

  // Focus the input on mount
  useEffect(() => {
    inputRef.current?.focus();
  }, []);

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

  // Animate through agent steps during loading
  useEffect(() => {
    if (!loading) { setCurrentStep(0); return; }
    const interval = setInterval(() => {
      setCurrentStep((prev) => (prev < AGENT_STEPS.length - 1 ? prev + 1 : prev));
    }, 2200);
    return () => clearInterval(interval);
  }, [loading]);

  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/login');
  };

  const handleClearHistory = async () => {
    if (!window.confirm("Are you sure you want to permanently delete all your chat history?")) return;
    try {
      await api.delete('/chat/history');
      setHistoryList([]);
      setMessages([]);
    } catch (error) {
      console.error("Failed to clear history", error);
    }
  };

  const handleNewChat = () => {
    setMessages([]);
    inputRef.current?.focus();
  };

  // Stop the current generation
  const handleStop = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
    setLoading(false);
    setMessages((prev) => [...prev, { role: 'ai', type: 'greeting', content: '⏹ Generation stopped.' }]);
  };

  const loadPastChat = (session) => {
    setMessages([
      { role: 'user', content: session.user_query },
      { role: 'ai', type: 'response', data: session.agent_response }
    ]);
  };

  const handleSend = async (prompt) => {
    const text = prompt || input;
    if (!text.trim()) return;

    const userMessage = { role: 'user', content: text };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    // Create a new AbortController for this request
    const controller = new AbortController();
    abortControllerRef.current = controller;

    try {
      const response = await api.post('/chat/', { message: text }, { signal: controller.signal });
      const aiMessage = { role: 'ai', type: 'response', data: response.data };
      setMessages((prev) => [...prev, aiMessage]);
      
      const newHistoryItem = {
        user_query: text,
        intent: response.data.query_intent || 'UNKNOWN',
        agent_response: response.data
      };
      setHistoryList((prev) => [newHistoryItem, ...prev]);

    } catch (err) {
      // Don't show an error if the user intentionally cancelled
      if (err.code === 'ERR_CANCELED' || err.name === 'CanceledError') return;
      const errorMsg = err.response?.data?.detail || err.message || "Failed to reach backend.";
      setMessages((prev) => [...prev, { role: 'ai', type: 'error', content: errorMsg }]);
    } finally {
      abortControllerRef.current = null;
      setLoading(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    handleSend();
  };

  // ── Is this the welcome screen (no messages yet)? ──
  const isWelcome = messages.length === 0 && !loading;

  return (
    <div className="flex flex-col h-screen bg-slate-50 font-sans">
      
      {/* ═══ Navbar ═══ */}
      <header className="bg-gradient-to-r from-indigo-950 via-indigo-900 to-violet-950 text-white shadow-lg py-3.5 px-6 flex justify-between items-center z-10 shrink-0">
        <div className="flex items-center gap-3">
          <div className="bg-gradient-to-br from-indigo-600 to-violet-600 p-2 rounded-xl shadow-lg shadow-indigo-900/30">
            <ShieldAlert className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-lg font-bold tracking-tight leading-tight">ML-Guardian</h1>
            <p className="text-xs text-indigo-300 font-medium">Agentic AI Security Platform</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <div className="hidden sm:flex items-center gap-1.5 bg-emerald-500/15 text-emerald-300 px-3 py-1.5 rounded-full text-xs font-bold border border-emerald-500/20">
            <span className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse"></span>
            All Agents Online
          </div>
          <button 
            onClick={handleLogout}
            className="flex items-center gap-2 text-indigo-200 hover:text-white transition-colors text-sm font-medium bg-white/5 hover:bg-white/10 px-4 py-2 rounded-lg border border-white/10"
          >
            <LogOut className="w-4 h-4" /> Logout
          </button>
        </div>
      </header>

      {/* ═══ Main Layout ═══ */}
      <div className="flex flex-1 overflow-hidden">
        
        {/* ═══ Sidebar ═══ */}
        <aside className="w-72 bg-gray-950 text-gray-300 hidden md:flex flex-col shrink-0">
          
          {/* New Chat Button */}
          <div className="p-4">
            <button 
              onClick={handleNewChat}
              className="w-full flex items-center justify-center gap-2 bg-gradient-to-r from-indigo-600 to-violet-600 text-white font-semibold py-3 rounded-xl hover:from-indigo-500 hover:to-violet-500 transition-all active:scale-[0.98] shadow-lg shadow-indigo-900/30"
            >
              <MessageSquarePlus className="w-5 h-5" /> New Chat
            </button>
          </div>

          {/* History Header */}
          <div className="px-5 py-3 text-xs font-bold text-gray-500 uppercase tracking-widest flex items-center justify-between">
            <div className="flex items-center gap-2">
              <History className="w-3.5 h-3.5" />
              Recent Audits
            </div>
            {historyList.length > 0 && (
              <button 
                onClick={handleClearHistory} 
                className="text-gray-600 hover:text-red-400 transition-colors p-1 rounded hover:bg-gray-800" 
                title="Clear History"
              >
                <Trash2 className="w-3.5 h-3.5" />
              </button>
            )}
          </div>

          {/* History List */}
          <div className="flex-1 overflow-y-auto px-3 pb-3 space-y-1 custom-scrollbar">
            {historyList.length === 0 ? (
              <p className="text-sm text-gray-600 text-center mt-8">No conversations yet.</p>
            ) : (
              historyList.map((item, index) => (
                <button 
                  key={index} 
                  onClick={() => loadPastChat(item)}
                  className="sidebar-item w-full text-left px-3 py-3 rounded-xl transition-all border border-transparent hover:border-gray-800 group"
                >
                  <p className="text-sm text-gray-300 truncate group-hover:text-white transition-colors">
                    {item.user_query}
                  </p>
                  <span className="text-[11px] text-indigo-400/70 mt-1 block font-medium">
                    {item.intent?.replace(/_/g, ' ')}
                  </span>
                </button>
              ))
            )}
          </div>
        </aside>

        {/* ═══ Chat Area ═══ */}
        <div className="flex-1 flex flex-col min-w-0 bg-gradient-to-b from-slate-50 to-slate-100">
          
          <main className="flex-1 overflow-y-auto p-4 md:p-8">
            <div className="max-w-4xl mx-auto">

              {/* ═══ Welcome Screen ═══ */}
              {isWelcome && (
                <div className="flex flex-col items-center justify-center min-h-[70vh] animate-fade-in-up">
                  
                  {/* Hero */}
                  <div className="bg-gradient-to-br from-indigo-600 to-violet-600 p-5 rounded-2xl shadow-xl shadow-indigo-300/30 mb-8">
                    <Sparkles className="w-10 h-10 text-white" />
                  </div>
                  <h2 className="text-3xl md:text-4xl font-extrabold text-gray-900 mb-3 text-center">
                    What can I help you with?
                  </h2>
                  <p className="text-gray-500 text-center max-w-lg mb-10 text-lg">
                    I can recommend models, audit for bias, explain ML concepts, and generate Risk Passports.
                  </p>

                  {/* Suggested Prompt Cards */}
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 w-full max-w-2xl">
                    {SUGGESTED_PROMPTS.map((item, i) => (
                      <button
                        key={i}
                        onClick={() => handleSend(item.prompt)}
                        className={`group flex items-start gap-4 p-5 rounded-2xl bg-gradient-to-br ${item.color} border transition-all hover:shadow-md hover:scale-[1.02] active:scale-[0.98] text-left`}
                      >
                        <div className="mt-0.5 shrink-0">{item.icon}</div>
                        <div>
                          <p className="font-bold text-gray-800 text-sm mb-1">{item.label}</p>
                          <p className="text-gray-500 text-xs leading-relaxed line-clamp-2">{item.prompt}</p>
                        </div>
                        <ArrowRight className="w-4 h-4 text-gray-400 shrink-0 mt-1 opacity-0 group-hover:opacity-100 transition-opacity" />
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* ═══ Messages ═══ */}
              <div className="space-y-6">
                {messages.map((msg, index) => (
                  <div key={index} className={`flex gap-4 animate-fade-in-up ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                    
                    {/* AI Avatar */}
                    {msg.role === 'ai' && (
                      <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 to-violet-500 flex items-center justify-center shrink-0 shadow-lg shadow-indigo-200/50 mt-1">
                        {msg.type === 'error' ? <ServerCrash className="w-5 h-5 text-white" /> : <Bot className="w-5 h-5 text-white" />}
                      </div>
                    )}

                    {/* Message Bubble */}
                    <div className={`max-w-[85%] rounded-2xl ${
                      msg.role === 'user' 
                        ? 'bg-gradient-to-r from-indigo-600 to-violet-600 text-white p-5 shadow-lg shadow-indigo-200/40 rounded-tr-sm' 
                        : msg.type === 'error'
                          ? 'bg-red-50 text-red-700 border border-red-200 rounded-tl-sm p-5'
                          : msg.type === 'response' 
                            ? 'w-full' 
                            : 'bg-white text-gray-800 border border-gray-200 rounded-tl-sm p-5 shadow-sm'
                    }`}>
                      
                      {/* Simple text */}
                      {(msg.type === 'greeting' || msg.type === 'error' || msg.role === 'user') && (
                        <p className="whitespace-pre-wrap leading-relaxed">{msg.content}</p>
                      )}

                      {/* Risk Passport with gradient border */}
                      {msg.type === 'response' && (
                        <div className="gradient-border rounded-2xl">
                          <div className="bg-white rounded-2xl overflow-hidden">
                            <RiskPassport data={msg.data} />
                          </div>
                        </div>
                      )}
                    </div>

                    {/* User Avatar */}
                    {msg.role === 'user' && (
                      <div className="w-10 h-10 rounded-xl bg-slate-200 flex items-center justify-center shrink-0 border border-slate-300 mt-1 shadow-sm">
                        <User className="w-5 h-5 text-slate-600" />
                      </div>
                    )}
                  </div>
                ))}

                {/* ═══ Agent Pipeline Loading ═══ */}
                {loading && (
                  <div className="flex gap-4 justify-start animate-fade-in-up">
                    <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 to-violet-500 flex items-center justify-center shrink-0 shadow-lg shadow-indigo-200/50">
                      <Loader2 className="w-5 h-5 text-white animate-spin" />
                    </div>
                    <div className="bg-white border border-gray-200 rounded-2xl rounded-tl-sm p-5 shadow-sm w-full max-w-sm">
                      <p className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-4">Agent Pipeline</p>
                      <div className="space-y-3">
                        {AGENT_STEPS.map((step, i) => (
                          <div 
                            key={i} 
                            className={`flex items-center gap-3 text-sm transition-all duration-500 ${
                              i < currentStep ? 'text-emerald-600' :
                              i === currentStep ? 'text-indigo-700 font-semibold' :
                              'text-gray-300'
                            }`}
                          >
                            <span className="text-base w-6 text-center">
                              {i < currentStep ? '✓' : step.icon}
                            </span>
                            <span>{step.label}</span>
                            {i === currentStep && (
                              <div className="ml-auto flex gap-1">
                                <div className="w-1.5 h-1.5 bg-indigo-500 rounded-full animate-bounce"></div>
                                <div className="w-1.5 h-1.5 bg-indigo-500 rounded-full animate-bounce" style={{ animationDelay: '0.15s' }}></div>
                                <div className="w-1.5 h-1.5 bg-indigo-500 rounded-full animate-bounce" style={{ animationDelay: '0.3s' }}></div>
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>
            </div>
          </main>

          {/* ═══ Input Area ═══ */}
          <footer className="bg-white/80 backdrop-blur-lg border-t border-gray-200/50 p-4 shrink-0">
            <form onSubmit={handleSubmit} className="max-w-4xl mx-auto relative">
              <input
                ref={inputRef}
                type="text"
                className="w-full bg-white border-2 border-gray-200 rounded-2xl py-4 pl-6 pr-16 focus:outline-none focus:border-indigo-400 focus:ring-4 focus:ring-indigo-500/10 transition-all shadow-sm text-gray-800 placeholder:text-gray-400"
                placeholder="Ask about ML models, risks, or concepts..."
                value={input}
                onChange={(e) => setInput(e.target.value)}
                disabled={loading}
              />
              {loading ? (
                <button
                  type="button"
                  onClick={handleStop}
                  className="absolute right-2.5 top-2.5 bottom-2.5 bg-red-500 text-white rounded-xl px-4 hover:bg-red-600 transition-all flex items-center justify-center gap-2 shadow-lg shadow-red-200/50"
                >
                  <Square className="w-4 h-4 fill-white" />
                </button>
              ) : (
                <button
                  type="submit"
                  disabled={!input.trim()}
                  className="send-btn-glow absolute right-2.5 top-2.5 bottom-2.5 bg-gradient-to-r from-indigo-600 to-violet-600 text-white rounded-xl px-4 hover:from-indigo-500 hover:to-violet-500 transition-all disabled:from-gray-200 disabled:to-gray-300 disabled:text-gray-400 disabled:shadow-none flex items-center justify-center gap-2"
                >
                  <Send className="w-4 h-4" />
                </button>
              )}
            </form>
            <div className="flex items-center justify-center gap-4 mt-3">
              <p className="text-xs text-gray-400 font-medium">
                Powered by LangGraph · Groq · ChromaDB · Tavily
              </p>
            </div>
          </footer>
        </div>
      </div>
    </div>
  );
}
