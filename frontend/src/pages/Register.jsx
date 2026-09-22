import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { ShieldAlert, BrainCircuit, Lock, CheckCircle2 } from 'lucide-react';
import api from '../services/api';

export default function Register() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({ email: '', username: '', password: '' });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess(false);
    setLoading(true);

    try {
      await api.post('/auth/register', formData);
      setSuccess(true);
      setTimeout(() => navigate('/login'), 2000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50 p-4 relative overflow-hidden">
      
      {/* Morphing Water Bubbles */}
      <div className="absolute top-10 left-20 w-64 h-64 bg-gradient-to-tr from-cyan-400 to-blue-300 opacity-60 mix-blend-multiply shadow-xl water-bubble delay-1"></div>
      <div className="absolute top-40 right-20 w-80 h-80 bg-gradient-to-tr from-purple-400 to-pink-300 opacity-60 mix-blend-multiply shadow-xl water-bubble delay-2"></div>
      <div className="absolute -bottom-20 left-1/3 w-72 h-72 bg-gradient-to-tr from-teal-300 to-emerald-200 opacity-60 mix-blend-multiply shadow-xl water-bubble delay-3"></div>
      <div className="absolute top-1/4 left-1/2 w-48 h-48 bg-gradient-to-tr from-orange-300 to-rose-300 opacity-60 mix-blend-multiply shadow-xl water-bubble delay-4"></div>

      {/* Main Card (z-10 puts it above the background bubbles) */}
      <div className="flex w-full max-w-5xl bg-white/90 backdrop-blur-xl shadow-2xl rounded-3xl overflow-hidden relative z-10 border border-white/50">
        
        {/* Left Side: Branding / Gradient (Hidden on mobile) */}
        <div className="hidden md:flex flex-col justify-between w-1/2 bg-gradient-to-br from-indigo-950 via-indigo-900 to-violet-900 p-12 text-white relative overflow-hidden">
          {/* Decorative background circle */}
          <div className="absolute top-0 left-0 w-full h-full opacity-10 pointer-events-none">
            <div className="absolute -top-24 -left-24 w-96 h-96 bg-white rounded-full blur-3xl"></div>
          </div>
          
          <div className="relative z-10">
            <div className="flex items-center gap-3 mb-12">
              <ShieldAlert className="w-10 h-10 text-indigo-400" />
              <h1 className="text-3xl font-bold tracking-tight">ML-Guardian</h1>
            </div>
            
            <h2 className="text-4xl font-extrabold mb-6 leading-tight">
              Secure your <br/> AI workflows.
            </h2>
            <p className="text-indigo-200 text-lg mb-12">
              Join the platform that provides enterprise-grade guardrails, bias auditing, and real-time prompt protection.
            </p>

            <div className="space-y-6">
              <div className="flex items-center gap-4">
                <div className="bg-indigo-800/50 p-3 rounded-xl"><BrainCircuit className="w-6 h-6 text-indigo-300"/></div>
                <div>
                  <h4 className="font-semibold text-white">Intelligent Routing</h4>
                  <p className="text-indigo-200 text-sm">Advanced agentic intent classification.</p>
                </div>
              </div>
              <div className="flex items-center gap-4">
                <div className="bg-indigo-800/50 p-3 rounded-xl"><Lock className="w-6 h-6 text-indigo-300"/></div>
                <div>
                  <h4 className="font-semibold text-white">PII & Injection Guard</h4>
                  <p className="text-indigo-200 text-sm">Military-grade prompt sanitization.</p>
                </div>
              </div>
              <div className="flex items-center gap-4">
                <div className="bg-indigo-800/50 p-3 rounded-xl"><CheckCircle2 className="w-6 h-6 text-indigo-300"/></div>
                <div>
                  <h4 className="font-semibold text-white">Risk Passports</h4>
                  <p className="text-indigo-200 text-sm">Automated bias and fairness auditing.</p>
                </div>
              </div>
            </div>
          </div>
          
          <div className="relative z-10 text-indigo-300 text-sm mt-12">
            © 2026 ML-Guardian. All rights reserved.
          </div>
        </div>

        {/* Right Side: The Form */}
        <div className="w-full md:w-1/2 p-8 lg:p-14 flex flex-col justify-center">
          <div className="mb-8">
            <h2 className="text-3xl font-bold text-gray-900 mb-2">Create an account</h2>
            <p className="text-gray-500">Get started with ML-Guardian today.</p>
          </div>

          {error && (
            <div className="bg-red-50 text-red-600 p-4 rounded-xl text-sm mb-6 border border-red-100 flex items-center gap-3">
              <div className="bg-red-100 p-1 rounded-full"><ShieldAlert className="w-4 h-4"/></div>
              {error}
            </div>
          )}

          {success && (
            <div className="bg-emerald-50 text-emerald-700 p-4 rounded-xl text-sm mb-6 border border-emerald-200 flex items-center gap-3 font-medium">
              <div className="bg-emerald-100 p-1 rounded-full"><CheckCircle2 className="w-4 h-4"/></div>
              User created successfully! Redirecting to login...
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-1.5">Email Address</label>
              <input
                type="email"
                required
                placeholder="you@company.com"
                className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:bg-white focus:ring-4 focus:ring-indigo-500/10 focus:border-indigo-500 outline-none transition-all text-gray-900"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              />
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-1.5">Username</label>
              <input
                type="text"
                required
                placeholder="johndoe"
                className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:bg-white focus:ring-4 focus:ring-indigo-500/10 focus:border-indigo-500 outline-none transition-all text-gray-900"
                value={formData.username}
                onChange={(e) => setFormData({ ...formData, username: e.target.value })}
              />
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-1.5">Password</label>
              <input
                type="password"
                required
                placeholder="••••••••"
                className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:bg-white focus:ring-4 focus:ring-indigo-500/10 focus:border-indigo-500 outline-none transition-all text-gray-900"
                value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
              />
            </div>

            <button
              type="submit"
              disabled={loading || success}
              className="w-full bg-indigo-950 text-white font-bold py-3.5 rounded-xl hover:bg-indigo-900 transition-all active:scale-[0.98] disabled:bg-indigo-950/50 shadow-lg shadow-indigo-900/20 mt-4"
            >
              {loading ? 'Creating account...' : 'Register Now'}
            </button>
          </form>

          <div className="mt-8 text-center text-sm text-gray-500 font-medium">
            Already have an account?{' '}
            <Link to="/login" className="text-indigo-600 hover:text-indigo-800 transition-colors">
              Log in here
            </Link>
          </div>
        </div>

      </div>
    </div>
  );
}
