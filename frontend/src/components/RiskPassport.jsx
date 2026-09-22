import React from 'react';
import { 
  ShieldAlert, ShieldCheck, Cpu, AlertTriangle, 
  BookOpen, Link as LinkIcon, CheckCircle2, Info 
} from 'lucide-react';
import TypewriterText from './TypewriterText';

export default function RiskPassport({ data }) {
  // If it's a blocked message from the security guardrails
  if (data.status === 'blocked') {
    return (
      <div className="bg-red-50 border border-red-200 rounded-xl p-5 shadow-sm">
        <div className="flex items-center gap-3 mb-2 text-red-700 font-bold">
          <ShieldAlert className="w-5 h-5" />
          Security Block
        </div>
        <p className="text-red-600 text-sm">{data.message}</p>
      </div>
    );
  }

  const intent = data.query_intent || 'UNKNOWN';
  const content = data.content || {};

  // If it's a general chat (no ML features triggered)
  if (intent === 'GENERAL_CHAT' && content.general?.response) {
    return (
      <div className="px-2">
        <TypewriterText text={content.general.response} speed={10} />
      </div>
    );
  }

  return (
    <div className="bg-white border border-indigo-100 rounded-xl overflow-hidden shadow-sm">
      
      {/* Header */}
      <div className="bg-indigo-50 border-b border-indigo-100 p-4 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Cpu className="w-5 h-5 text-indigo-600" />
          <h3 className="font-bold text-indigo-900">ML Risk Passport</h3>
        </div>
        <span className="bg-indigo-100 text-indigo-700 text-xs font-bold px-3 py-1 rounded-full uppercase tracking-wider">
          {intent.replace(/_/g, ' ')}
        </span>
      </div>

      <div className="p-5 space-y-6">
        
        {/* ML Recommendation Section */}
        {content.recommendations && (
          <section>
            <h4 className="flex items-center gap-2 text-sm font-bold text-gray-700 uppercase mb-3">
              <CheckCircle2 className="w-4 h-4 text-emerald-500" /> Recommended Models
            </h4>
            <div className="flex flex-wrap gap-2 mb-3">
              {content.recommendations.models?.map((model, i) => (
                <span key={i} className="bg-gray-100 border border-gray-200 text-gray-700 px-3 py-1 rounded-md text-sm font-medium">
                  {model}
                </span>
              ))}
            </div>
            {content.recommendations.reasoning && (
              <div className="bg-gray-50 p-4 rounded-lg border border-gray-100 mb-4">
                <TypewriterText text={content.recommendations.reasoning} speed={5} />
              </div>
            )}
            
            {/* Preprocessing & Challenges Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {content.recommendations.preprocessing && content.recommendations.preprocessing.length > 0 && (
                <div className="bg-blue-50/50 p-4 rounded-lg border border-blue-100">
                  <h5 className="text-xs font-bold text-blue-800 uppercase mb-3">Preprocessing</h5>
                  <ul className="list-disc list-inside text-sm text-gray-600 space-y-2">
                    {content.recommendations.preprocessing.map((step, i) => (
                      <li key={i}>{step}</li>
                    ))}
                  </ul>
                </div>
              )}
              {content.recommendations.challenges && (
                <div className="bg-orange-50/50 p-4 rounded-lg border border-orange-100">
                  <h5 className="text-xs font-bold text-orange-800 uppercase mb-3">Known Challenges</h5>
                  <p className="text-sm text-gray-600 leading-relaxed">{content.recommendations.challenges}</p>
                </div>
              )}
            </div>
          </section>
        )}

        {/* Risk Audit Section (Member 3) */}
        {content.risk_assessment && (
          <section className="border-t border-gray-100 pt-5">
            <div className="flex items-center justify-between mb-4">
              <h4 className="flex items-center gap-2 text-sm font-bold text-gray-700 uppercase">
                <ShieldCheck className="w-4 h-4 text-rose-500" /> Ethics & Risk Audit
              </h4>
              <span className={`text-xs font-bold px-3 py-1 rounded-full ${
                content.risk_assessment.level === 'HIGH' ? 'bg-red-100 text-red-700' :
                content.risk_assessment.level === 'MEDIUM' ? 'bg-orange-100 text-orange-700' :
                'bg-green-100 text-green-700'
              }`}>
                {content.risk_assessment.level} RISK
              </span>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-rose-50 p-4 rounded-xl border border-rose-100">
                <h5 className="text-xs font-bold text-rose-800 uppercase mb-3 flex items-center gap-1">
                  <AlertTriangle className="w-4 h-4" /> Bias Risks
                </h5>
                <ul className="list-disc list-inside text-sm text-gray-700 space-y-2">
                  {content.risk_assessment.bias_risks?.map((risk, i) => (
                    <li key={i}>{risk}</li>
                  ))}
                </ul>
              </div>
              <div className="bg-purple-50 p-4 rounded-xl border border-purple-100">
                <h5 className="text-xs font-bold text-purple-800 uppercase mb-3 flex items-center gap-1">
                  <Info className="w-4 h-4" /> Privacy Risks
                </h5>
                <ul className="list-disc list-inside text-sm text-gray-700 space-y-2">
                  {content.risk_assessment.privacy_risks?.map((risk, i) => (
                    <li key={i}>{risk}</li>
                  ))}
                </ul>
              </div>
            </div>
          </section>
        )}

        {/* Explanation / RAG Section (Member 4) */}
        {content.education && (
          <section className="border-t border-gray-100 pt-5">
            <h4 className="flex items-center gap-2 text-sm font-bold text-gray-700 uppercase mb-4">
              <BookOpen className="w-4 h-4 text-blue-500" /> Concept Explanation
            </h4>
            <div className="mb-6">
              <TypewriterText text={content.education.explanation} speed={8} />
            </div>
            
            {/* Sources */}
            {content.education.sources && content.education.sources.length > 0 && (
              <div className="bg-slate-50 p-3 rounded-lg border border-slate-200">
                <h5 className="text-xs font-bold text-slate-500 uppercase mb-2 flex items-center gap-1">
                  <LinkIcon className="w-3 h-3" /> Sources
                </h5>
                <ul className="text-xs text-slate-600 space-y-1">
                  {content.education.sources.map((source, i) => (
                    <li key={i} className="flex items-center gap-2">
                      <span className="w-1.5 h-1.5 bg-slate-400 rounded-full"></span>
                      {source.startsWith('http') ? (
                        <a href={source} target="_blank" rel="noopener noreferrer" className="text-indigo-600 hover:underline truncate">
                          {source}
                        </a>
                      ) : (
                        source
                      )}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </section>
        )}

      </div>
    </div>
  );
}
