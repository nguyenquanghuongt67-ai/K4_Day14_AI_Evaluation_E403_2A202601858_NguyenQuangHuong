import React from 'react';
import { MessageSquare, Plus, Download, Sun, Moon } from 'lucide-react';

export default function Sidebar({ isDarkMode, setIsDarkMode, setMessages }) {
  return (
    <div className="w-64 bg-slate-850 dark:bg-slate-900 border-r border-slate-700/50 flex flex-col h-full text-slate-300">
      <div className="p-4">
        <button 
          onClick={() => setMessages([])}
          className="flex items-center gap-2 w-full px-4 py-2 bg-teal-600 hover:bg-teal-500 text-white rounded-lg transition-colors shadow-sm"
        >
          <Plus size={18} />
          <span className="font-medium">New Chat</span>
        </button>
      </div>
      
      <div className="flex-1 overflow-y-auto px-3 py-2 space-y-1">
        <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2 px-2">History</div>
        <button className="flex items-center gap-3 w-full px-3 py-2 text-sm text-left hover:bg-slate-800 rounded-md transition-colors text-slate-200">
          <MessageSquare size={16} />
          <span className="truncate">Evaluation Run 1</span>
        </button>
      </div>

      <div className="p-4 border-t border-slate-700/50 space-y-2">
        <button 
          onClick={() => alert("Mock export to artifacts/actual_answers.json")}
          className="flex items-center gap-2 w-full px-4 py-2 hover:bg-slate-800 rounded-lg transition-colors text-sm"
        >
          <Download size={16} />
          <span>Export JSON</span>
        </button>
        <button 
          onClick={() => setIsDarkMode(!isDarkMode)}
          className="flex items-center gap-2 w-full px-4 py-2 hover:bg-slate-800 rounded-lg transition-colors text-sm"
        >
          {isDarkMode ? <Sun size={16} /> : <Moon size={16} />}
          <span>{isDarkMode ? 'Light Mode' : 'Dark Mode'}</span>
        </button>
      </div>
    </div>
  );
}
