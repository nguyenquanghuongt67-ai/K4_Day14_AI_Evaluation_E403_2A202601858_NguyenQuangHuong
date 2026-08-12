import React, { useState } from 'react';
import Sidebar from './components/Sidebar';
import ChatContainer from './components/ChatContainer';

function App() {
  const [messages, setMessages] = useState([]);
  const [isDarkMode, setIsDarkMode] = useState(true);

  return (
    <div className={`flex h-screen w-full ${isDarkMode ? 'dark bg-slate-900' : 'bg-gray-50'}`}>
      <Sidebar isDarkMode={isDarkMode} setIsDarkMode={setIsDarkMode} setMessages={setMessages} />
      <div className="flex-1 flex flex-col relative h-full">
        <ChatContainer messages={messages} setMessages={setMessages} />
      </div>
    </div>
  );
}

export default App;
