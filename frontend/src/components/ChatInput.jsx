import React, { useState } from 'react';
import { SendHorizontal } from 'lucide-react';

export default function ChatInput({ onSend, disabled }) {
  const [text, setText] = useState("");

  const handleSend = () => {
    if (text.trim() && !disabled) {
      onSend(text);
      setText("");
    }
  };

  return (
    <div className="max-w-3xl mx-auto w-full relative">
      <div className="relative flex items-end w-full bg-slate-800 border border-slate-700 rounded-2xl p-1 focus-within:border-teal-500/50 focus-within:ring-1 focus-within:ring-teal-500/50 transition-all shadow-lg">
        <textarea
          className="w-full bg-transparent text-slate-100 px-4 py-3 min-h-[52px] max-h-48 resize-none focus:outline-none text-[15px]"
          placeholder="Message OrbitTech Agent..."
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault();
              handleSend();
            }
          }}
          disabled={disabled}
        />
        <button
          onClick={handleSend}
          disabled={!text.trim() || disabled}
          className="m-1.5 p-2 bg-white text-slate-900 rounded-xl hover:bg-slate-200 disabled:bg-slate-700 disabled:text-slate-500 transition-colors"
        >
          <SendHorizontal size={18} />
        </button>
      </div>
      <div className="text-center text-xs text-slate-500 mt-2">
        Demo UI - Calls OpenRouter API and mocks Context/Metrics.
      </div>
    </div>
  );
}
