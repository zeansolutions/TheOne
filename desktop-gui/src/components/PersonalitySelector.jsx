import React from 'react';
import { Brain } from 'lucide-react';

export default function PersonalitySelector({ lang, selectedPersona, setSelectedPersona, personas = [], t }) {
  const getPersonaName = (id) => {
    if (lang === 'ar') {
      if (id === 'sage_friend') return 'الحكيم الودود';
      if (id === 'scientist') return 'الباحث العلمي';
      if (id === 'witty_mentor') return 'المرشد الظريف';
      return id;
    } else {
      if (id === 'sage_friend') return 'The Wise Friend';
      if (id === 'scientist') return 'The Scientist';
      if (id === 'witty_mentor') return 'The Witty Mentor';
      return id;
    }
  };

  return (
    <div className="d-flex justify-between align-center mb-2 gap-2" style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.05)', paddingBottom: '6px' }}>
      <span className="text-[11px] text-slate-400 font-mono d-flex align-center gap-1">
        <Brain style={{ width: '12px', height: '12px' }} />
        {t('forcedPersonaOption')}:
      </span>
      <select
        value={selectedPersona}
        onChange={(e) => setSelectedPersona(e.target.value)}
        className="cyber-select text-[11px] py-0.5 px-2"
        style={{ minWidth: '130px' }}
      >
        <option value="auto">🤖 {lang === 'ar' ? 'تلقائي (حسب السؤال)' : 'Automatic / Dynamic'}</option>
        {personas && personas.map(pId => (
          <option key={pId} value={pId}>👤 {getPersonaName(pId)}</option>
        ))}
      </select>
    </div>
  );
}
