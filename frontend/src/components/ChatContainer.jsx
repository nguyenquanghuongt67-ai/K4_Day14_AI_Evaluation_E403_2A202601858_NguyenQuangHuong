import React, { useState, useRef, useEffect } from 'react';
import MessageBubble from './MessageBubble';
import ChatInput from './ChatInput';
import { Bot } from 'lucide-react';

export default function ChatContainer({ messages, setMessages }) {
  const [isTyping, setIsTyping] = useState(false);
  const [stepperState, setStepperState] = useState(0); // 0: Idle, 1: Request, 2: Waiting API
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping, stepperState]);

  const handleSend = async (text) => {
    // 1. Add User Message
    const userMsg = { id: Date.now(), role: 'user', content: text };
    setMessages(prev => [...prev, userMsg]);
    setIsTyping(true);
    setStepperState(1);
    
    try {
      setStepperState(2);
      // GỌI THẲNG XUỐNG BACKEND PYTHON (FASTAPI)
      const res = await fetch("http://localhost:8000/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: text })
      });
      
      const data = await res.json();
      
      const aiMsg = { 
        id: Date.now()+1, 
        role: 'assistant', 
        content: data.answer || data.error_message || "Lỗi xử lý từ hệ thống.",
        contexts: data.contexts || [],
        metrics: data.metrics || {}
      };
      
      setMessages(prev => [...prev, aiMsg]);
    } catch (e) {
      const errorMsg = { 
        id: Date.now()+1, 
        role: 'assistant', 
        content: "Thật xin lỗi, hệ thống không thể kết nối tới Backend API. Vui lòng đảm bảo server `uvicorn domain_assistant:app` đang chạy ở port 8000.",
      };
      setMessages(prev => [...prev, errorMsg]);
    }

    setIsTyping(false);
    setStepperState(0);
  };

  return (
    <div className="flex flex-col h-full bg-slate-900 dark:bg-slate-900 relative">
      {stepperState > 0 && (
        <div className="absolute top-0 left-0 right-0 bg-slate-800/80 backdrop-blur border-b border-slate-700 p-2 flex justify-center items-center gap-4 text-xs font-mono text-teal-400 z-10">
          <span className={stepperState >= 1 ? "text-teal-400" : "text-slate-500"}>1. Sending Query</span> ➔
          <span className={stepperState >= 2 ? "text-teal-400" : "text-slate-500"}>2. Agent Processing & Scoring</span> ➔
          <span className={stepperState >= 3 ? "text-teal-400" : "text-slate-500"}>3. Complete</span>
        </div>
      )}

      <div className="flex-1 overflow-y-auto px-4 py-6 sm:px-6 md:px-8 space-y-6">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-slate-500 space-y-4">
            <div className="w-16 h-16 bg-slate-800 rounded-2xl flex items-center justify-center mb-2">
              <Bot size={32} className="text-teal-500" />
            </div>
            <h2 className="text-2xl font-semibold text-slate-300">How can I help you today?</h2>
            <div className="flex flex-wrap justify-center gap-2 mt-4 max-w-lg">
              <button onClick={() => handleSend("How much is OrbitPlus?")} className="px-4 py-2 bg-slate-800 hover:bg-slate-700 rounded-full text-sm transition-colors text-slate-300">How much is OrbitPlus?</button>
              <button onClick={() => handleSend("What is the return policy for opened items?")} className="px-4 py-2 bg-slate-800 hover:bg-slate-700 rounded-full text-sm transition-colors text-slate-300">Return policy for opened items?</button>
              <button onClick={() => handleSend("xin chào")} className="px-4 py-2 bg-slate-800 hover:bg-slate-700 rounded-full text-sm transition-colors text-slate-300">xin chào</button>
              <button onClick={() => handleSend("Tôi bị ốm thì nên uống thuốc gì?")} className="px-4 py-2 bg-slate-800 hover:bg-slate-700 rounded-full text-sm transition-colors text-slate-300">Tôi bị ốm thì nên uống thuốc gì?</button>
            </div>
          </div>
        ) : (
          messages.map(msg => <MessageBubble key={msg.id} msg={msg} />)
        )}
        
        {isTyping && stepperState === 2 && (
          <div className="flex items-center gap-3 text-slate-400 max-w-3xl mx-auto w-full px-4">
             <div className="w-8 h-8 rounded-full bg-teal-600 flex items-center justify-center text-white shrink-0"><Bot size={18}/></div>
             <div className="bg-slate-800 rounded-2xl px-4 py-3 flex gap-1">
               <span className="w-2 h-2 bg-slate-500 rounded-full animate-bounce"></span>
               <span className="w-2 h-2 bg-slate-500 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></span>
               <span className="w-2 h-2 bg-slate-500 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></span>
             </div>
             <span className="text-xs">Agent is searching KB and generating answer...</span>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <div className="p-4 bg-gradient-to-t from-slate-900 via-slate-900 to-transparent">
        <ChatInput onSend={handleSend} disabled={isTyping} />
      </div>
    </div>
  );
}
