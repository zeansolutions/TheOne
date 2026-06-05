import React, { useState, useEffect, useRef } from 'react';
import { 
  MessageSquare, PlusCircle, Moon, Activity, Server, Globe, Brain, ShieldAlert, Zap, Info
} from 'lucide-react';
import { translations } from './translations';
import ChatInterface from './components/ChatInterface';
import GraphVisualizer from './components/GraphVisualizer';
import KnowledgePanel from './components/KnowledgePanel';
import ConflictResolver from './components/ConflictResolver';

const LANGUAGES = [
  { code: 'en', name: 'English', dir: 'ltr' },
  { code: 'ar', name: 'العربية', dir: 'rtl' },
  { code: 'fr', name: 'Français', dir: 'ltr' },
  { code: 'es', name: 'Español', dir: 'ltr' },
  { code: 'zh', name: '中文', dir: 'ltr' },
  { code: 'tr', name: 'Türkçe', dir: 'ltr' },
  { code: 'de', name: 'Deutsch', dir: 'ltr' },
  { code: 'ru', name: 'Русский', dir: 'ltr' },
  { code: 'pt', name: 'Português', dir: 'ltr' },
  { code: 'ja', name: '日本語', dir: 'ltr' },
  { code: 'ko', name: '한국어', dir: 'ltr' }
];

export default function App() {
  const [activeTab, setActiveTab] = useState('chat');
  const [lang, setLang] = useState('en');
  const [status, setStatus] = useState({
    status: 'offline',
    active_world: 'reality',
    active_language: 'en',
    concepts_count: 0,
    facts_count: 0,
    inferred_count: 0,
    worlds: ['reality'],
    personas: ['al_hakim']
  });

  const [graphData, setGraphData] = useState({ nodes: [], edges: [] });
  const [activeNode, setActiveNode] = useState(null);

  // Chat State
  const [chatInput, setChatInput] = useState('');
  const [chatMessages, setChatMessages] = useState([]);
  const [isThinking, setIsThinking] = useState(false);
  const [selectedPersona, setSelectedPersona] = useState('auto');
  const [reasoningTrace, setReasoningTrace] = useState('');
  const [perfTrace, setPerfTrace] = useState(null);

  // Teach State
  const [sourceConcept, setSourceConcept] = useState('');
  const [targetConcept, setTargetConcept] = useState('');
  const [selectedRelation, setSelectedRelation] = useState('has_property');
  const [teachWorld, setTeachWorld] = useState('reality');
  const [teachConfidence, setTeachConfidence] = useState(1.0);
  const [teachModality, setTeachModality] = useState('');
  const [teachMessage, setTeachMessage] = useState(null);

  // Sleep State
  const [sleepDepth, setSleepDepth] = useState(2);
  const [sleepCleanup, setSleepCleanup] = useState(true);
  const [sleepStats, setSleepStats] = useState(null);
  const [isSleeping, setIsSleeping] = useState(false);

  // Curiosity State
  const [curiosityQuestions, setCuriosityQuestions] = useState([]);

  // Conflict state
  const [conflictData, setConflictData] = useState(null);

  // Log monitor trace
  const [systemLogs, setSystemLogs] = useState([]);

  // Database / Ingest state
  const [jsonInput, setJsonInput] = useState('');
  const [importStats, setImportStats] = useState(null);
  const [dbMessage, setDbMessage] = useState(null);
  const [worldToDelete, setWorldToDelete] = useState('');

  // Custom worlds / relations state
  const [customWorlds, setCustomWorlds] = useState([]);
  const [newWorldName, setNewWorldName] = useState('');
  const [newRelId, setNewRelId] = useState('');
  const [newRelName, setNewRelName] = useState('');
  const [newRelTransitive, setNewRelTransitive] = useState(false);
  const [newRelSymmetric, setNewRelSymmetric] = useState(false);
  const [newRelDecay, setNewRelDecay] = useState(0.0);
  const [relAddMessage, setRelAddMessage] = useState(null);

  // Procedural state variables
  const [procedures, setProcedures] = useState({});
  const [newProcedureName, setNewProcedureName] = useState('');
  const [newProcedureSteps, setNewProcedureSteps] = useState([]);
  const [newStepText, setNewStepText] = useState('');
  const [proceduralMessage, setProceduralMessage] = useState(null);

  const messagesEndRef = useRef(null);

  // Get active translation dictionary
  const t = (key) => {
    const dict = translations[lang] || translations['en'];
    return dict[key] || translations['en'][key] || key;
  };

  const getDir = () => {
    const currentLang = LANGUAGES.find(l => l.code === lang);
    return currentLang ? currentLang.dir : 'ltr';
  };

  // Poll system status and fetch graph
  const fetchStatus = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/status');
      const data = await res.json();
      if (data.status === 'online') {
        setStatus(data);
      }
    } catch (e) {
      setStatus(prev => ({ ...prev, status: 'offline' }));
    }
  };

  const fetchGraph = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/graph');
      const data = await res.json();
      setGraphData(data);
    } catch (e) {
      console.error('Failed to load graph:', e);
    }
  };

  const fetchCuriosity = async () => {
    try {
      const res = await fetch(`http://localhost:8000/api/curiosity?lang=${lang}&limit=5`);
      const data = await res.json();
      setCuriosityQuestions(data.questions || []);
    } catch (e) {
      console.error('Failed to load curiosity:', e);
    }
  };

  const fetchProcedures = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/procedural/get');
      const data = await res.json();
      setProcedures(data);
    } catch (e) {
      console.error('Failed to load procedures:', e);
    }
  };

  const handleSaveProcedure = async (e) => {
    e.preventDefault();
    if (!newProcedureName.trim() || newProcedureSteps.length === 0) {
      setProceduralMessage({ type: 'error', text: lang === 'ar' ? 'الرجاء إدخال اسم الإجراء وخطوة واحدة على الأقل' : 'Please enter procedure name and at least one step.' });
      return;
    }
    setProceduralMessage(null);
    try {
      const res = await fetch('http://localhost:8000/api/procedural/add', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          procedure_name: newProcedureName.trim(),
          steps: newProcedureSteps
        })
      });
      const data = await res.json();
      if (data.success) {
        setProceduralMessage({ type: 'success', text: data.message });
        setNewProcedureName('');
        setNewProcedureSteps([]);
        setNewStepText('');
        fetchProcedures();
        logMessage(`Saved cognitive procedure: ${newProcedureName}`, 'success');
      } else {
        setProceduralMessage({ type: 'error', text: data.error });
      }
    } catch (err) {
      setProceduralMessage({ type: 'error', text: 'Error saving procedure' });
    }
  };

  const handleDeleteProcedure = async (name) => {
    if (!window.confirm(lang === 'ar' ? `هل أنت متأكد من حذف الإجراء ${name}؟` : `Are you sure you want to delete procedure ${name}?`)) return;
    setProceduralMessage(null);
    try {
      const res = await fetch('http://localhost:8000/api/procedural/delete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ procedure_name: name })
      });
      const data = await res.json();
      if (data.success) {
        setProceduralMessage({ type: 'success', text: data.message });
        fetchProcedures();
        logMessage(`Deleted cognitive procedure: ${name}`, 'success');
      } else {
        setProceduralMessage({ type: 'error', text: data.error });
      }
    } catch (err) {
      setProceduralMessage({ type: 'error', text: 'Error deleting procedure' });
    }
  };

  useEffect(() => {
    fetchStatus();
    fetchGraph();
    fetchCuriosity();
    fetchProcedures();

    const interval = setInterval(() => {
      fetchStatus();
      fetchCuriosity();
    }, 5000);

    return () => clearInterval(interval);
  }, [lang]);

  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [chatMessages]);

  const logMessage = (msg, type = 'info') => {
    const time = new Date().toLocaleTimeString();
    setSystemLogs(prev => [`[${time}] [${type.toUpperCase()}] ${msg}`, ...prev.slice(0, 99)]);
  };

  const handleSetWorld = async (worldName) => {
    try {
      const res = await fetch('http://localhost:8000/api/set_world', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ world: worldName })
      });
      const data = await res.json();
      if (data.success) {
        logMessage(`Swapped reasoning world to: '${worldName}'`, 'world');
        fetchStatus();
        fetchGraph();
      }
    } catch (e) {
      console.error(e);
    }
  };

  const handleSetLanguage = async (langCode) => {
    setLang(langCode);
    try {
      await fetch('http://localhost:8000/api/set_language', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ lang: langCode })
      });
      logMessage(`Swapped interface language to: ${langCode}`, 'system');
    } catch (e) {
      console.error(e);
    }
  };

  const handleAsk = async (e) => {
    if (e) e.preventDefault();
    if (!chatInput.trim()) return;

    const queryText = chatInput;
    setChatInput('');
    setChatMessages(prev => [...prev, { sender: 'user', text: queryText }]);
    setIsThinking(true);
    logMessage(`Processing query: "${queryText}"`, 'query');

    try {
      const res = await fetch('http://localhost:8000/api/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          query: queryText, 
          lang: lang,
          persona: selectedPersona === 'auto' ? null : selectedPersona
        })
      });
      const data = await res.json();
      if (data.success) {
        setChatMessages(prev => [...prev, { 
          sender: 'system', 
          text: data.response, 
          persona: data.persona,
          lang: data.language 
        }]);
        setReasoningTrace(data.formatted_trace);
        setPerfTrace({
          confidence: data.confidence,
          elapsed_ms: data.elapsed_ms
        });
        logMessage(`Reasoning completed in ${data.elapsed_ms.toFixed(1)}ms. Confidence: ${data.confidence.toFixed(2)}`, 'success');
      } else {
        setChatMessages(prev => [...prev, { sender: 'system', text: `Error: ${data.error}` }]);
        logMessage(data.error, 'error');
      }
    } catch (err) {
      setChatMessages(prev => [...prev, { sender: 'system', text: 'Backend offline. Make sure api.py is running!' }]);
      logMessage('Failed to connect to backend server', 'error');
    } finally {
      setIsThinking(false);
    }
  };

  const handleAddNewWorld = () => {
    const trimmed = newWorldName.trim().toLowerCase();
    if (!trimmed) return;
    if (!customWorlds.includes(trimmed)) {
      setCustomWorlds(prev => [...prev, trimmed]);
      logMessage(`Locally registered new world: '${trimmed}'`, 'world');
    }
    handleSetWorld(trimmed);
    setNewWorldName('');
  };

  const handleDeleteActiveWorld = async () => {
    const worldToDelete = status.active_world;
    if (worldToDelete === 'reality') {
      alert(lang === 'ar' ? 'لا يمكن حذف العالم الواقعي الأساسي (reality).' : 'Cannot delete the base reality world.');
      return;
    }
    
    const confirmation = window.confirm(
      lang === 'ar' 
        ? `هل أنت متأكد من حذف العالم '${worldToDelete}' بالكامل؟` 
        : `Are you sure you want to delete world '${worldToDelete}'?`
    );
    if (!confirmation) return;

    try {
      const res = await fetch('http://localhost:8000/api/clear_db', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ type: 'world', world: worldToDelete })
      });
      const data = await res.json();
      if (data.success) {
        logMessage(data.message, 'success');
        setCustomWorlds(prev => prev.filter(w => w !== worldToDelete));
        handleSetWorld('reality');
      } else {
        logMessage(data.error, 'error');
      }
    } catch (err) {
      logMessage('Failed to delete world', 'error');
    }
  };

  const handleRegisterRelation = async () => {
    const id = newRelId.trim().toLowerCase();
    const name = newRelName.trim();
    if (!id) {
      setRelAddMessage({ type: 'error', text: lang === 'ar' ? 'يرجى إدخال معرّف العلاقة' : 'Please enter Relation ID' });
      return;
    }

    logMessage(`Registering relation: ID='${id}', Transitive=${newRelTransitive}, Symmetric=${newRelSymmetric}, Decay=${newRelDecay}`, 'teach');

    try {
      const res = await fetch('http://localhost:8000/api/add_relation', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          id,
          name: name || id,
          transitive: newRelTransitive,
          symmetric: newRelSymmetric,
          decay: newRelTransitive ? newRelDecay : 0.0
        })
      });
      const data = await res.json();
      if (data.success) {
        setRelAddMessage({ type: 'success', text: data.message });
        logMessage(data.message, 'success');
        setNewRelId('');
        setNewRelName('');
        setNewRelTransitive(false);
        setNewRelSymmetric(false);
        setNewRelDecay(0.0);
        fetchStatus();
      } else {
        setRelAddMessage({ type: 'error', text: data.error });
        logMessage(data.error, 'error');
      }
    } catch (e) {
      setRelAddMessage({ type: 'error', text: 'Connection failed' });
    }
  };

  const handleTeach = async (e) => {
    e.preventDefault();
    if (!sourceConcept.trim() || !targetConcept.trim()) return;

    const payload = {
      subject: sourceConcept.trim().toLowerCase(),
      object: targetConcept.trim().toLowerCase(),
      relation: selectedRelation,
      world: teachWorld,
      confidence: teachConfidence,
      modality: teachModality || null,
      lang: lang
    };

    logMessage(`Teaching fact: [${payload.subject}] --(${payload.relation})--> [${payload.object}] in '${payload.world}'`, 'teach');

    try {
      const res = await fetch('http://localhost:8000/api/teach', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      if (data.success) {
        if (data.status === 'auto_rejected' || data.status === 'replaced' || data.status === 'ignored' || data.status === 'merged') {
          logMessage(data.message, 'success');
          setTeachMessage({ type: 'success', text: data.message });
        } else if (data.message.includes('تعارض') || data.message.includes('Conflict')) {
          setConflictData({
            subject: payload.subject,
            object: payload.object,
            relation: payload.relation,
            world: payload.world,
            description: data.message
          });
          logMessage(`Logical conflict detected for subject ${payload.subject}`, 'warning');
        } else {
          setTeachMessage({ type: 'success', text: data.message });
          logMessage(data.message, 'success');
        }
        
        setSourceConcept('');
        setTargetConcept('');
        setTeachModality('');
        setTeachConfidence(1.0);
        fetchGraph();
        fetchStatus();
      } else {
        setTeachMessage({ type: 'error', text: data.error });
        logMessage(data.error, 'error');
      }
    } catch (err) {
      setTeachMessage({ type: 'error', text: 'Error connecting to API server' });
    }
  };

  const handleResolveConflict = async (action) => {
    if (!conflictData) return;
    logMessage(`Resolving conflict with action: ${action}`, 'action');
    try {
      const res = await fetch('http://localhost:8000/api/resolve_conflict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          subject: conflictData.subject,
          object: conflictData.object,
          relation: conflictData.relation,
          world: conflictData.world,
          action: action
        })
      });
      const data = await res.json();
      if (data.success) {
        logMessage(`Conflict resolved: ${data.message}`, 'success');
        setConflictData(null);
        fetchGraph();
        fetchStatus();
      }
    } catch (e) {
      console.error(e);
    }
  };

  const handleSleep = async () => {
    setIsSleeping(true);
    logMessage('Initiating Cognitive Sleep Cycle...', 'sleep');
    try {
      const res = await fetch('http://localhost:8000/api/sleep', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ depth: sleepDepth, cleanup: sleepCleanup })
      });
      const data = await res.json();
      if (data.success) {
        setSleepStats(data.stats);
        logMessage('Cognitive Sleep Cycle completed successfully.', 'success');
        fetchGraph();
        fetchStatus();
      }
    } catch (e) {
      logMessage('Failed to complete sleep cycle', 'error');
    } finally {
      setIsSleeping(false);
    }
  };

  const handleImportJson = async (e) => {
    if (e) e.preventDefault();
    if (!jsonInput.trim()) return;
    setDbMessage(null);
    setImportStats(null);

    try {
      let parsed = JSON.parse(jsonInput);
      const res = await fetch('http://localhost:8000/api/import_json', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(parsed)
      });
      const data = await res.json();
      if (data.success) {
        setImportStats(data.stats);
        setDbMessage({ type: 'success', text: t('importSuccess') });
        setJsonInput('');
        logMessage(`Knowledge imported: ${JSON.stringify(data.stats)}`, 'success');
        fetchStatus();
        fetchGraph();
      } else {
        setDbMessage({ type: 'error', text: data.error });
        logMessage(`Failed to import JSON: ${data.error}`, 'error');
      }
    } catch (err) {
      setDbMessage({ type: 'error', text: 'Invalid JSON format. Check syntax.' });
      logMessage(`JSON parsing error: ${err.message}`, 'error');
    }
  };

  const handleClearDb = async (type, world = null) => {
    const confirmation = window.confirm(t('confirmClear'));
    if (!confirmation) return;
    setDbMessage(null);

    try {
      const res = await fetch('http://localhost:8000/api/clear_db', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ type, world })
      });
      const data = await res.json();
      if (data.success) {
        setDbMessage({ type: 'success', text: data.message });
        logMessage(data.message, 'success');
        fetchStatus();
        fetchGraph();
      } else {
        setDbMessage({ type: 'error', text: data.error });
        logMessage(data.error, 'error');
      }
    } catch (err) {
      setDbMessage({ type: 'error', text: 'Failed to clear database.' });
      logMessage('Failed to clear database', 'error');
    }
  };

  return (
    <div dir={getDir()} className="d-flex flex-column min-h-screen p-4 gap-4">
      {/* Top Header Bar */}
      <header className="glass-panel d-flex justify-between align-center p-4 gap-4">
        <div className="d-flex align-center gap-3">
          <Brain className="text-cyan animate-pulse" style={{ width: '32px', height: '32px' }} />
          <div>
            <h1 className="text-xl font-bold cyber-title">{t('title')}</h1>
            <p className="text-xs text-slate-400 font-medium">{t('subtitle')}</p>
          </div>
        </div>

        <div className="d-flex flex-wrap align-center gap-3">
          {/* Server status indicator */}
          <div className="d-flex align-center gap-2">
            <Server className="text-slate-400" style={{ width: '16px', height: '16px' }} />
            {status.status === 'online' ? (
              <span className="pulse-badge">{t('status')}: ONLINE</span>
            ) : (
              <span className="p-2 bg-red-950-60 text-red rounded" style={{ fontSize: '10px', fontWeight: 'bold' }}>
                OFFLINE
              </span>
            )}
          </div>

          {/* Active World swap drop down */}
          <div className="d-flex align-center gap-2">
            <div className="d-flex align-center gap-1">
              <Globe className="text-slate-400" style={{ width: '16px', height: '16px' }} />
              <select 
                value={status.active_world} 
                onChange={(e) => handleSetWorld(e.target.value)}
                className="cyber-select py-1 px-2 text-xs"
              >
                {Array.from(new Set([...(status.worlds || []), ...customWorlds, 'reality', 'khayali'])).map(w => (
                  <option key={w} value={w}>{t('activeWorld')}: {w}</option>
                ))}
              </select>
              {status.active_world !== 'reality' && (
                <button
                  type="button"
                  onClick={handleDeleteActiveWorld}
                  className="cyber-btn py-0.5 px-2 text-xs text-red hover-bg-red-950-40"
                  style={{ height: '24px', minWidth: 'auto', borderColor: 'rgba(239, 68, 68, 0.4)' }}
                  title={lang === 'ar' ? 'حذف هذا العالم' : 'Delete Active World'}
                >
                  🗑️
                </button>
              )}
            </div>
            
            {/* Add new world inline form */}
            <div className="d-flex align-center gap-1">
              <input
                type="text"
                placeholder={lang === 'ar' ? 'عالم جديد...' : 'New world...'}
                value={newWorldName}
                onChange={(e) => setNewWorldName(e.target.value)}
                className="cyber-input py-1 px-2 text-xs"
                style={{ width: '90px', height: '24px' }}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') handleAddNewWorld();
                }}
              />
              <button
                type="button"
                onClick={handleAddNewWorld}
                className="cyber-btn py-0.5 px-2 text-xs"
                style={{ height: '24px', minWidth: 'auto' }}
                title={lang === 'ar' ? 'إضافة عالم' : 'Add World'}
              >
                +
              </button>
            </div>
          </div>

          {/* Language selector */}
          <div className="d-flex align-center gap-1">
            <Globe className="text-slate-400" style={{ width: '16px', height: '16px' }} />
            <select 
              value={lang} 
              onChange={(e) => handleSetLanguage(e.target.value)}
              className="cyber-select py-1 px-2 text-xs"
            >
              {LANGUAGES.map(l => (
                <option key={l.code} value={l.code}>{l.name}</option>
              ))}
            </select>
          </div>
        </div>
      </header>

      {/* Main Database Stats Strip */}
      <div className="grid grid-cols-4 gap-4">
        <div className="glass-panel p-3 d-flex align-center justify-between">
          <span className="text-xs text-slate-400">{t('concepts')}</span>
          <span className="text-lg font-bold text-cyan">{status.concepts_count}</span>
        </div>
        <div className="glass-panel p-3 d-flex align-center justify-between">
          <span className="text-xs text-slate-400">{t('facts')}</span>
          <span className="text-lg font-bold text-purple">{status.facts_count}</span>
        </div>
        <div className="glass-panel p-3 d-flex align-center justify-between">
          <span className="text-xs text-slate-400">{t('inferred')}</span>
          <span className="text-lg font-bold text-pink">{status.inferred_count}</span>
        </div>
        <div className="glass-panel p-3 d-flex align-center justify-between lang-stats-trigger cursor-pointer" title={lang === 'ar' ? 'عرض تفاصيل القواعد اللغوية' : 'View grammar rules details'}>
          <span className="text-xs text-slate-400">{lang === 'ar' ? 'القواعد اللغوية' : 'Linguistic Rules'}</span>
          <span className="text-lg font-bold text-teal">
            {Object.keys(status.language_stats || {}).filter(k => k !== 'global_morphology').length} {lang === 'ar' ? 'لغات' : 'Langs'}
          </span>
          
          <div className="lang-stats-popover">
            <h4 className="text-xs font-bold text-cyan border-b border-slate-800 pb-1 mb-2">
              {lang === 'ar' ? 'تفاصيل القواعد اللغوية النشطة' : 'Active Linguistic Rules'}
            </h4>
            {status.language_stats && Object.keys(status.language_stats).filter(k => k !== 'global_morphology').map(langCode => {
              const stats = status.language_stats[langCode];
              const langNames = {
                ar: lang === 'ar' ? 'العربية' : 'Arabic',
                en: lang === 'ar' ? 'الإنجليزية' : 'English',
                fr: lang === 'ar' ? 'الفرنسية' : 'French',
                es: lang === 'ar' ? 'الإسبانية' : 'Spanish'
              };
              return (
                <div key={langCode} className="mb-2 last:mb-0">
                  <div className="text-xs font-semibold text-slate-200" style={{ borderBottom: '1px solid rgba(255,255,255,0.05)', paddingBottom: '2px', marginBottom: '4px' }}>
                    {langNames[langCode] || langCode.toUpperCase()}
                  </div>
                  <div className="d-flex justify-between text-xxs text-slate-400 mt-0.5" style={{ fontSize: '10px' }}>
                    <span>{lang === 'ar' ? 'المفردات (Lexicon):' : 'Vocabulary (Lexicon):'}</span>
                    <span className="font-mono text-cyan" style={{ fontSize: '10px' }}>{stats.lexicon_count}</span>
                  </div>
                  <div className="d-flex justify-between text-xxs text-slate-400" style={{ fontSize: '10px' }}>
                    <span>{lang === 'ar' ? 'القواعد والروابط:' : 'Grammar & Rules:'}</span>
                    <span className="font-mono text-purple" style={{ fontSize: '10px' }}>{stats.grammar_rules_count}</span>
                  </div>
                </div>
              );
            })}
            
            {status.language_stats?.global_morphology && (
              <div className="mt-2 pt-2 border-t border-slate-800" style={{ borderTop: '1px solid rgba(255,255,255,0.1)' }}>
                <div className="text-xs font-semibold text-slate-300" style={{ fontSize: '11px', marginBottom: '4px' }}>
                  {lang === 'ar' ? 'المورفولوجيا والجذور المشتركة' : 'Common Morphology & Roots'}
                </div>
                <div className="d-flex justify-between text-xxs text-slate-400 mt-0.5" style={{ fontSize: '10px' }}>
                  <span>{lang === 'ar' ? 'الجذور الصرفية:' : 'Morphological Roots:'}</span>
                  <span className="font-mono text-teal" style={{ fontSize: '10px' }}>{status.language_stats.global_morphology.roots_count}</span>
                </div>
                <div className="d-flex justify-between text-xxs text-slate-400" style={{ fontSize: '10px' }}>
                  <span>{lang === 'ar' ? 'السوابق واللواحق:' : 'Particles/Affixes:'}</span>
                  <span className="font-mono text-pink" style={{ fontSize: '10px' }}>{status.language_stats.global_morphology.particles_count}</span>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Dual Panel Workspace */}
      <div className="workspace-layout flex-grow">
        
        {/* Left Side: Physics Directed Graph Network */}
        <GraphVisualizer
          graphData={graphData}
          activeNode={activeNode}
          setActiveNode={setActiveNode}
          sourceConcept={sourceConcept}
          setSourceConcept={setSourceConcept}
          targetConcept={targetConcept}
          setTargetConcept={setTargetConcept}
          fetchGraph={fetchGraph}
          lang={lang}
        />

        {/* Right Side: Interactive reasoning and tools panels */}
        <div className="d-flex flex-column gap-4">
          
          {/* Tab Selection */}
          <div className="glass-panel d-flex bg-slate-950-60 p-1 rounded-lg">
            <button 
              onClick={() => setActiveTab('chat')} 
              className={`flex-grow tab-btn justify-center py-2 ${activeTab === 'chat' ? 'active' : ''}`}
            >
              <MessageSquare style={{ width: '16px', height: '16px' }} />
              <span>{t('chatTab')}</span>
            </button>
            <button 
              onClick={() => setActiveTab('teach')} 
              className={`flex-grow tab-btn justify-center py-2 ${activeTab === 'teach' ? 'active' : ''}`}
            >
              <PlusCircle style={{ width: '16px', height: '16px' }} />
              <span>{t('teachTab')}</span>
            </button>
            <button 
              onClick={() => setActiveTab('maintenance')} 
              className={`flex-grow tab-btn justify-center py-2 ${activeTab === 'maintenance' ? 'active' : ''}`}
            >
              <Moon style={{ width: '16px', height: '16px' }} />
              <span>{t('maintenanceTab')}</span>
            </button>
            <button 
              onClick={() => setActiveTab('db')} 
              className={`flex-grow tab-btn justify-center py-2 ${activeTab === 'db' ? 'active' : ''}`}
            >
              <Server style={{ width: '16px', height: '16px' }} />
              <span>{t('databaseTab')}</span>
            </button>
            <button 
              onClick={() => setActiveTab('procedural')} 
              className={`flex-grow tab-btn justify-center py-2 ${activeTab === 'procedural' ? 'active' : ''}`}
            >
              <Zap style={{ width: '16px', height: '16px' }} />
              <span>{t('proceduralTab')}</span>
            </button>
          </div>

          {/* Active Tab Panel Body */}
          {activeTab === 'chat' ? (
            <div className="glass-panel flex-grow d-flex flex-column p-4 min-h-380">
              <ChatInterface
                lang={lang}
                t={t}
                chatMessages={chatMessages}
                chatInput={chatInput}
                setChatInput={setChatInput}
                isThinking={isThinking}
                perfTrace={perfTrace}
                selectedPersona={selectedPersona}
                setSelectedPersona={setSelectedPersona}
                personas={status.personas}
                handleAsk={handleAsk}
                messagesEndRef={messagesEndRef}
              />
            </div>
          ) : (
            <KnowledgePanel
              activeTab={activeTab}
              setActiveTab={setActiveTab}
              lang={lang}
              t={t}
              status={status}
              customWorlds={customWorlds}
              sourceConcept={sourceConcept}
              setSourceConcept={setSourceConcept}
              targetConcept={targetConcept}
              setTargetConcept={setTargetConcept}
              selectedRelation={selectedRelation}
              setSelectedRelation={setSelectedRelation}
              teachWorld={teachWorld}
              setTeachWorld={setTeachWorld}
              teachConfidence={teachConfidence}
              setTeachConfidence={setTeachConfidence}
              teachModality={teachModality}
              setTeachModality={setTeachModality}
              teachMessage={teachMessage}
              newRelId={newRelId}
              setNewRelId={setNewRelId}
              newRelName={newRelName}
              setNewRelName={setNewRelName}
              newRelTransitive={newRelTransitive}
              setNewRelTransitive={setNewRelTransitive}
              newRelSymmetric={newRelSymmetric}
              setNewRelSymmetric={setNewRelSymmetric}
              newRelDecay={newRelDecay}
              setNewRelDecay={setNewRelDecay}
              relAddMessage={relAddMessage}
              handleTeach={handleTeach}
              handleRegisterRelation={handleRegisterRelation}
              sleepDepth={sleepDepth}
              setSleepDepth={setSleepDepth}
              sleepCleanup={sleepCleanup}
              setSleepCleanup={setSleepCleanup}
              sleepStats={sleepStats}
              isSleeping={isSleeping}
              curiosityQuestions={curiosityQuestions}
              handleSleep={handleSleep}
              setChatInput={setChatInput}
              jsonInput={jsonInput}
              setJsonInput={setJsonInput}
              importStats={importStats}
              dbMessage={dbMessage}
              worldToDelete={worldToDelete}
              setWorldToDelete={setWorldToDelete}
              handleImportJson={handleImportJson}
              handleClearDb={handleClearDb}
              procedures={procedures}
              newProcedureName={newProcedureName}
              setNewProcedureName={setNewProcedureName}
              newProcedureSteps={newProcedureSteps}
              setNewProcedureSteps={setNewProcedureSteps}
              newStepText={newStepText}
              setNewStepText={setNewStepText}
              proceduralMessage={proceduralMessage}
              handleSaveProcedure={handleSaveProcedure}
              handleDeleteProcedure={handleDeleteProcedure}
            />
          )}

        </div>

      </div>

      {/* Logic reasoning trace area */}
      {reasoningTrace && (
        <div className="glass-panel p-4 d-flex flex-column gap-2">
          <h3 className="text-xs font-bold font-mono text-cyan uppercase tracking-wider d-flex align-center gap-2">
            <Info style={{ width: '16px', height: '16px' }} />
            <span>{t('reasoningTrace')}</span>
          </h3>
          <div className="p-3 bg-slate-950-90 rounded border border-slate-800 max-h-160 overflow-y-auto">
            <div className="console-log text-xs font-mono whitespace-pre-wrap text-emerald">
              {reasoningTrace}
            </div>
          </div>
        </div>
      )}

      {/* Interactive Contradiction Resolution Modal */}
      <ConflictResolver
        conflictData={conflictData}
        handleResolveConflict={handleResolveConflict}
        t={t}
      />

      {/* Bottom Panel: Live system event log stream */}
      <footer className="glass-panel p-4 d-flex flex-column gap-2">
        <h3 className="text-xs font-bold font-mono text-cyan uppercase tracking-wider d-flex align-center gap-2">
          <Activity className="text-emerald" style={{ width: '16px', height: '16px' }} />
          <span>{t('systemLogsTab')}</span>
        </h3>
        <div className="p-3 bg-slate-950-90 rounded border border-slate-800 h-100 overflow-y-auto d-flex flex-column gap-1">
          {systemLogs.length === 0 ? (
            <span className="text-xs text-slate-600 font-mono">System idle. Waiting for events...</span>
          ) : (
            systemLogs.map((log, i) => (
              <span key={i} className="text-xs font-mono" style={{ color: '#34d399' }}>
                {log}
              </span>
            ))
          )}
        </div>
      </footer>
    </div>
  );
}
