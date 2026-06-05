import React from 'react';
import { MessageSquare, Brain, Play } from 'lucide-react';
import PersonalitySelector from './PersonalitySelector';

export default function ChatInterface({
  lang,
  t,
  chatMessages = [],
  chatInput,
  setChatInput,
  isThinking,
  perfTrace,
  selectedPersona,
  setSelectedPersona,
  personas = [],
  handleAsk,
  messagesEndRef
}) {
  return (
    <div className="d-flex flex-column flex-grow h-full">
      {/* Chat Message flow */}
      <div className="flex-grow overflow-y-auto max-h-320 mb-3 pr-2 d-flex flex-column">
        {chatMessages.length === 0 && (
          <div className="d-flex flex-column align-center justify-center flex-grow text-center p-8 text-slate-500" style={{ margin: 'auto' }}>
            <Brain className="text-slate-600 animate-pulse" style={{ width: '48px', height: '48px', marginBottom: '12px' }} />
            <p className="text-xs">{t('queryPlaceholder')}</p>
          </div>
        )}
        {chatMessages.map((msg, index) => (
          <div 
            key={index} 
            className={`chat-bubble ${msg.sender === 'user' ? 'user' : 'system'}`}
          >
            {msg.sender === 'system' && (
              <div className="d-flex align-center gap-1-5 mb-1 text-xs text-purple font-mono">
                <Brain style={{ width: '12px', height: '12px' }} />
                <span>Persona: {msg.persona} ({msg.lang})</span>
              </div>
            )}
            <p className="text-sm font-medium">{msg.text}</p>
          </div>
        ))}
        {isThinking && (
          <div className="chat-bubble system d-flex align-center gap-2">
            <span className="animate-bounce" style={{ display: 'inline-block', width: '8px', height: '8px', backgroundColor: '#00f0ff', borderRadius: '50%', animationDelay: '0ms' }}></span>
            <span className="animate-bounce" style={{ display: 'inline-block', width: '8px', height: '8px', backgroundColor: '#00f0ff', borderRadius: '50%', animationDelay: '150ms' }}></span>
            <span className="animate-bounce" style={{ display: 'inline-block', width: '8px', height: '8px', backgroundColor: '#00f0ff', borderRadius: '50%', animationDelay: '300ms' }}></span>
            <span className="text-xs text-slate-400 font-mono" style={{ marginLeft: '8px' }}>{t('thinking')}</span>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Performance stats indicator */}
      {perfTrace && (
        <div className="mb-2 p-2 bg-slate-950-80 rounded border border-slate-800 text-xs font-mono text-slate-400 d-flex justify-between">
          <span>{t('confidence')}: <b className="text-cyan">{perfTrace.confidence.toFixed(2)}</b></span>
          <span>{t('elapsed')}: <b className="text-purple">{perfTrace.elapsed_ms.toFixed(1)}ms</b></span>
        </div>
      )}

      {/* Persona selector control row */}
      <PersonalitySelector
        lang={lang}
        selectedPersona={selectedPersona}
        setSelectedPersona={setSelectedPersona}
        personas={personas}
        t={t}
      />

      {/* Input box */}
      <form onSubmit={handleAsk} className="d-flex gap-2">
        <input 
          type="text" 
          value={chatInput} 
          onChange={(e) => setChatInput(e.target.value)}
          placeholder={t('queryPlaceholder')}
          className="cyber-input flex-grow text-xs"
          disabled={isThinking}
        />
        <button type="submit" className="cyber-btn text-xs py-2" disabled={isThinking}>
          <Play style={{ width: '14px', height: '14px' }} />
          <span>{t('askBtn')}</span>
        </button>
      </form>
    </div>
  );
}
