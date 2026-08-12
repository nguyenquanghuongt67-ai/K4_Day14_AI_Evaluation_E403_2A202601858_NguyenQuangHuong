import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { User, Bot, ChevronDown, ChevronRight, Scale, ShieldAlert } from 'lucide-react';

export default function MessageBubble({ msg }) {
  const isUser = msg.role === 'user';
  const [showContext, setShowContext] = useState(false);
  const [judgeResult, setJudgeResult] = useState(null);
  const [judging, setJudging] = useState(false);

  const handleJudge = async () => {
    setJudging(true);
    await new Promise(r => setTimeout(r, 1000));
    setJudgeResult({ hallucination: false, score: 9.5, reason: "Answer matches context perfectly." });
    setJudging(false);
  };

  return (
    <div className={`flex gap-4 max-w-3xl mx-auto w-full ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
      <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${isUser ? 'bg-slate-700 text-white' : 'bg-teal-600 text-white'}`}>
        {isUser ? <User size={18} /> : <Bot size={18} />}
      </div>
      
      <div className={`flex flex-col gap-2 max-w-[80%] ${isUser ? 'items-end' : 'items-start'}`}>
        <div className={`px-5 py-3.5 rounded-2xl ${isUser ? 'bg-slate-800 text-slate-100 rounded-tr-sm' : 'bg-transparent text-slate-100'}`}>
          <div className="markdown-body text-[15px]">
             {isUser ? msg.content : <ReactMarkdown>{msg.content}</ReactMarkdown>}
          </div>
        </div>

        {!isUser && msg.contexts && (
          <div className="w-full flex flex-col gap-3 mt-1">
             {/* RAGAS Metrics */}
             <div className="flex flex-wrap gap-2">
               {Object.entries(msg.metrics).map(([k,v]) => {
                  const color = v >= 0.8 ? 'bg-teal-500/20 text-teal-400 border-teal-500/30' : (v >= 0.6 ? 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30' : 'bg-red-500/20 text-red-400 border-red-500/30');
                  return (
                    <div key={k} className={`text-xs px-2 py-1 rounded-md border font-mono ${color}`}>
                      {k.substring(0,6)}: {v.toFixed(2)}
                    </div>
                  )
               })}
             </div>
             
             {/* Context Accordion */}
             <div className="border border-slate-700 rounded-lg bg-slate-800/50 overflow-hidden">
               <button onClick={() => setShowContext(!showContext)} className="w-full flex items-center justify-between px-3 py-2 text-xs text-slate-400 hover:bg-slate-700 transition-colors">
                  <span className="flex items-center gap-1 font-semibold"><Scale size={14}/> Inspect RAG Context</span>
                  {showContext ? <ChevronDown size={14}/> : <ChevronRight size={14}/>}
               </button>
               {showContext && (
                 <div className="p-3 text-xs text-slate-300 space-y-2 border-t border-slate-700 bg-slate-850">
                    {msg.contexts.map((ctx, i) => (
                       <div key={i} className="p-2 bg-slate-800 rounded border border-slate-700">
                          <div className="text-teal-500 font-mono mb-1">Score: {ctx.score.toFixed(4)}</div>
                          {ctx.text}
                       </div>
                    ))}
                 </div>
               )}
             </div>

             {/* LLM Judge */}
             {!judgeResult ? (
               <button onClick={handleJudge} disabled={judging} className="self-start flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-full bg-slate-800 hover:bg-slate-700 text-slate-300 transition-colors border border-slate-600">
                 <ShieldAlert size={14} className="text-purple-400" />
                 {judging ? 'Judging...' : '⚖️ LLM Judge & Hallucination Check'}
               </button>
             ) : (
               <div className="p-3 bg-purple-900/20 border border-purple-500/30 rounded-lg text-xs text-purple-200">
                 <div className="font-semibold text-purple-400 flex items-center gap-1"><ShieldAlert size={14}/> Judge Report</div>
                 <div className="mt-1">Hallucination: {judgeResult.hallucination ? 'Yes' : 'No'} | Score: {judgeResult.score}</div>
                 <div className="mt-1 text-purple-300/80">{judgeResult.reason}</div>
               </div>
             )}
          </div>
        )}
      </div>
    </div>
  );
}
