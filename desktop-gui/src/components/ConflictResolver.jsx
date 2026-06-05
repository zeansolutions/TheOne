import React from 'react';
import { ShieldAlert } from 'lucide-react';

export default function ConflictResolver({
  conflictData,
  handleResolveConflict,
  t
}) {
  if (!conflictData) return null;

  return (
    <div className="fixed inset-0 bg-black-80 backdrop-blur-sm d-flex justify-center align-center p-4 z-50">
      <div className="glass-panel max-w-lg w-full p-6 d-flex flex-column gap-4 bg-slate-900" style={{ borderColor: 'rgba(239, 68, 68, 0.4)' }}>
        <div className="d-flex align-center gap-3 text-red">
          <ShieldAlert className="animate-bounce" style={{ width: '24px', height: '24px' }} />
          <h3 className="text-lg font-bold font-mono">{t('conflictDetected')}</h3>
        </div>
        
        <p className="text-sm text-slate-300 leading-relaxed font-medium">
          {conflictData.description}
        </p>

        <div className="d-flex flex-column gap-2 mt-2">
          <span className="text-xs text-slate-400 font-mono">{t('conflictChoose')}</span>
          
          <button 
            onClick={() => handleResolveConflict('replace')}
            className="w-full text-left p-2.5 bg-red-950-20 rounded border border-red-900-30 text-xs text-red transition"
            style={{ cursor: 'pointer' }}
          >
            {t('conflictReplace')}
          </button>
          
          <button 
            onClick={() => handleResolveConflict('merge')}
            className="w-full text-left p-2.5 bg-violet-950-20 rounded border border-violet-900-30 text-xs text-purple transition"
            style={{ cursor: 'pointer' }}
          >
            {t('conflictMerge')}
          </button>

          <button 
            onClick={() => handleResolveConflict('ignore')}
            className="w-full text-left p-2.5 bg-slate-900 rounded border border-slate-800 text-xs text-slate-300 transition"
            style={{ cursor: 'pointer' }}
          >
            {t('conflictIgnore')}
          </button>
        </div>
      </div>
    </div>
  );
}
