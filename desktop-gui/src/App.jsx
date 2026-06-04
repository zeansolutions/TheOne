import React, { useState, useEffect, useRef } from 'react';
import { 
  MessageSquare, PlusCircle, Moon, Activity, Trash2, Globe, Brain, ShieldAlert,
  Server, Play, HelpCircle, Check, HelpCircle as QueryIcon, Info, RefreshCw, X, Zap
} from 'lucide-react';
import { translations } from './translations';
import PhysicsGraph from './PhysicsGraph';

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

const RELATION_TYPES = [
  'is_a',
  'lives_in',
  'has_property',
  'requires',
  'provides'
];

const MODALITY_TYPES = [
  { code: 'definitely', name: 'Definitely / Absolutely (يقين)' },
  { code: 'probably', name: 'Probably / Mostly (غالباً)' },
  { code: 'rarely', name: 'Rarely / Scarcely (نادراً)' }
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

  // Push messages to system log console
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
        // Filter out from local state
        setCustomWorlds(prev => prev.filter(w => w !== worldToDelete));
        // Switch back to reality
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
        // Reset inputs
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
          // It was automatically resolved or confirmation was triggered
          logMessage(data.message, 'success');
          setTeachMessage({ type: 'success', text: data.message });
        } else if (data.message.includes('تعارض') || data.message.includes('Conflict')) {
          // Manual conflict detection fallback (if backend flags a contradiction)
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
        
        // Reset inputs and reload graph
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

  const handleDeleteEdge = async (edge) => {
    if (!window.confirm(`Are you sure you want to delete this relationship?`)) return;
    try {
      const res = await fetch('http://localhost:8000/api/delete_edge', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          source: edge.source,
          target: edge.target,
          relation: edge.relation,
          world: edge.world
        })
      });
      const data = await res.json();
      if (data.success) {
        logMessage(data.message, 'success');
        fetchGraph();
        fetchStatus();
      }
    } catch (e) {
      console.error(e);
    }
  };

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
      <div className="grid grid-cols-3 gap-4">
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
      </div>

      {/* Dual Panel Workspace */}
      <div className="workspace-layout flex-grow">
        
        {/* Left Side: Physics Directed Graph Network */}
        <div className="glass-panel d-flex flex-column min-h-450 relative overflow-hidden">
          <div className="p-3 border-b border-slate-800 d-flex justify-between align-center bg-slate-950-40">
            <span className="text-xs font-bold font-mono tracking-wider text-cyan">📺 INTERACTIVE NEURAL PATHWAYS</span>
            <button 
              onClick={fetchGraph} 
              className="p-1 hover-bg-slate-800 rounded transition" 
              style={{ background: 'none', border: 'none' }}
              title="Refresh Graph"
            >
              <RefreshCw className="text-slate-400" style={{ width: '14px', height: '14px' }} />
            </button>
          </div>
          <div className="flex-grow w-full relative min-h-380">
            <PhysicsGraph 
              nodes={graphData.nodes} 
              edges={graphData.edges} 
              activeNode={activeNode} 
              onNodeClick={(nodeId) => {
                setActiveNode(nodeId);
                // Prepopulate teaching form with clicked concept
                if (!sourceConcept) {
                  setSourceConcept(nodeId);
                } else if (!targetConcept) {
                  setTargetConcept(nodeId);
                } else {
                  setSourceConcept(nodeId);
                  setTargetConcept('');
                }
              }}
              lang={lang} 
            />
          </div>
        </div>

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
          <div className="glass-panel flex-grow d-flex flex-column p-4 min-h-380">
            
            {/* Tab: Chat Interface */}
            {activeTab === 'chat' && (
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
                    {status.personas && status.personas.map(pId => (
                      <option key={pId} value={pId}>👤 {getPersonaName(pId)}</option>
                    ))}
                  </select>
                </div>

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
            )}

            {/* Tab: Teach Engine */}
            {activeTab === 'teach' && (
              <form onSubmit={handleTeach} className="d-flex flex-column gap-3 flex-grow">
                <h3 className="text-xs font-bold font-mono text-cyan uppercase tracking-wider">{t('teachTitle')}</h3>
                
                <div className="grid grid-cols-2 gap-2">
                  <div className="d-flex flex-column gap-1">
                    <label className="text-xs text-slate-400 font-mono">Source / Subject</label>
                    <input 
                      type="text" 
                      value={sourceConcept} 
                      onChange={(e) => setSourceConcept(e.target.value)}
                      placeholder={t('subjPlaceholder')}
                      className="cyber-input py-2 text-xs"
                      required
                    />
                  </div>
                  <div className="d-flex flex-column gap-1">
                    <label className="text-xs text-slate-400 font-mono">Target / Object</label>
                    <input 
                      type="text" 
                      value={targetConcept} 
                      onChange={(e) => setTargetConcept(e.target.value)}
                      placeholder={t('objPlaceholder')}
                      className="cyber-input py-2 text-xs"
                      required
                    />
                  </div>
                </div>

                <div className="d-flex flex-column gap-1">
                  <label className="text-xs text-slate-400 font-mono">{t('relSelect')}</label>
                  <select 
                    value={selectedRelation} 
                    onChange={(e) => setSelectedRelation(e.target.value)}
                    className="cyber-select py-2 text-xs"
                  >
                    {Array.from(new Set([...(status.relations || []), ...RELATION_TYPES])).map(rel => (
                      <option key={rel} value={rel}>{rel}</option>
                    ))}
                  </select>
                </div>

                <div className="grid grid-cols-2 gap-2">
                  <div className="d-flex flex-column gap-1">
                    <label className="text-xs text-slate-400 font-mono">{t('worldSelect')}</label>
                    <select 
                      value={teachWorld} 
                      onChange={(e) => setTeachWorld(e.target.value)}
                      className="cyber-select py-2 text-xs"
                    >
                      {Array.from(new Set([...(status.worlds || []), ...customWorlds, 'reality', 'khayali'])).map(w => (
                        <option key={w} value={w}>{w}</option>
                      ))}
                    </select>
                  </div>
                  <div className="d-flex flex-column gap-1">
                    <label className="text-xs text-slate-400 font-mono">{t('modalitySelect')}</label>
                    <select 
                      value={teachModality} 
                      onChange={(e) => setTeachModality(e.target.value)}
                      className="cyber-select py-2 text-xs"
                    >
                      <option value="">No modifier</option>
                      {MODALITY_TYPES.map(m => (
                        <option key={m.code} value={m.code}>{m.name}</option>
                      ))}
                    </select>
                  </div>
                </div>

                <div className="d-flex flex-column gap-1 mt-1">
                  <div className="d-flex justify-between text-xs text-slate-400 font-mono">
                    <span>{t('confidenceSlider')}</span>
                    <span className="text-cyan font-bold">{teachConfidence.toFixed(2)}</span>
                  </div>
                  <input 
                    type="range" 
                    min="0" 
                    max="1" 
                    step="0.05" 
                    value={teachConfidence} 
                    onChange={(e) => setTeachConfidence(parseFloat(e.target.value))}
                    style={{ width: '100%', height: '4px', backgroundColor: '#1e293b', borderRadius: '4px', outline: 'none', cursor: 'pointer' }}
                  />
                </div>

                {teachMessage && (
                  <div className={`p-2 rounded text-xs border ${
                    teachMessage.type === 'success' 
                      ? 'bg-emerald-950-60 border-emerald-800 text-emerald' 
                      : 'bg-red-950-60 border-red-800 text-red'
                  }`}>
                    {teachMessage.text}
                  </div>
                )}

                <button type="submit" className="cyber-btn mt-2 py-2 text-xs">
                  <PlusCircle style={{ width: '16px', height: '16px' }} />
                  <span>{t('teachBtn')}</span>
                </button>
              </form>
            )}

            {activeTab === 'teach' && (
              <div className="mt-4 p-3 border border-slate-800 rounded bg-slate-950-40">
                <h4 className="text-xs font-bold font-mono text-pink uppercase tracking-wider mb-2 d-flex justify-between align-center">
                  <span>{lang === 'ar' ? 'تعريف علاقة منطقية جديدة' : 'Define New Relation Type'}</span>
                </h4>
                <div className="d-flex flex-column gap-2">
                  <div className="grid grid-cols-2 gap-2">
                    <div className="d-flex flex-column gap-1">
                      <label className="text-[10px] text-slate-400 font-mono">Relation ID (e.g. contains)</label>
                      <input 
                        type="text" 
                        placeholder="e.g. contains"
                        value={newRelId}
                        onChange={(e) => setNewRelId(e.target.value)}
                        className="cyber-input py-1 px-2 text-xs"
                      />
                    </div>
                    <div className="d-flex flex-column gap-1">
                      <label className="text-[10px] text-slate-400 font-mono">Display Name / الاسم العربي</label>
                      <input 
                        type="text" 
                        placeholder="e.g. يحتوي على"
                        value={newRelName}
                        onChange={(e) => setNewRelName(e.target.value)}
                        className="cyber-input py-1 px-2 text-xs"
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-2 align-center mt-1">
                    <label className="d-flex align-center gap-1 text-xs text-slate-300 cursor-pointer">
                      <input 
                        type="checkbox" 
                        checked={newRelTransitive}
                        onChange={(e) => setNewRelTransitive(e.target.checked)}
                        className="cyber-checkbox"
                      />
                      <span>{lang === 'ar' ? 'متعدية (استدلال بالتعميم)' : 'Transitive (Generalization)'}</span>
                    </label>
                    <label className="d-flex align-center gap-1 text-xs text-slate-300 cursor-pointer">
                      <input 
                        type="checkbox" 
                        checked={newRelSymmetric}
                        onChange={(e) => setNewRelSymmetric(e.target.checked)}
                        className="cyber-checkbox"
                      />
                      <span>{lang === 'ar' ? 'متماثلة (علاقة متبادلة)' : 'Symmetric (Mutual)'}</span>
                    </label>
                  </div>

                  {newRelTransitive && (
                    <div className="d-flex flex-column gap-1 mt-1">
                      <div className="d-flex justify-between text-[10px] text-slate-400 font-mono">
                        <span>{lang === 'ar' ? 'معدل تلاشي الثقة بالتعميم' : 'Decay Rate (Confidence Loss)'}</span>
                        <span className="text-pink font-bold">{newRelDecay.toFixed(2)}</span>
                      </div>
                      <input 
                        type="range" 
                        min="0" 
                        max="1" 
                        step="0.05" 
                        value={newRelDecay} 
                        onChange={(e) => setNewRelDecay(parseFloat(e.target.value))}
                        style={{ width: '100%', height: '4px', backgroundColor: '#1e293b', borderRadius: '4px', outline: 'none', cursor: 'pointer' }}
                      />
                    </div>
                  )}

                  {relAddMessage && (
                    <div className={`p-1.5 rounded text-[11px] border ${
                      relAddMessage.type === 'success' ? 'bg-emerald-950-60 border-emerald-800 text-emerald' : 'bg-rose-950-60 border-rose-800 text-rose'
                    }`}>
                      {relAddMessage.text}
                    </div>
                  )}

                  <button 
                    type="button" 
                    onClick={handleRegisterRelation}
                    className="cyber-btn py-1 text-xs mt-1"
                  >
                    {lang === 'ar' ? 'تسجيل العلاقة' : 'Register Relation'}
                  </button>
                </div>
              </div>
            )}

            {/* Tab: Sleep Cycle & Curiosity */}
            {activeTab === 'maintenance' && (
              <div className="d-flex flex-column gap-4 flex-grow overflow-y-auto max-h-350">
                
                {/* Cognitive Sleep block */}
                <div className="p-3 bg-slate-950-50 rounded border border-slate-800 d-flex flex-column gap-2">
                  <h4 className="text-xs font-bold text-purple font-mono d-flex align-center gap-1-5">
                    <Moon style={{ width: '14px', height: '14px' }} />
                    <span>{t('sleepTitle')}</span>
                  </h4>
                  <p className="text-[11px] text-slate-400">{t('sleepSub')}</p>

                  <div className="grid grid-cols-2 gap-2 my-1">
                    <div className="d-flex flex-column gap-1">
                      <label className="text-xs text-slate-400 font-mono">Sleep Depth</label>
                      <select 
                        value={sleepDepth} 
                        onChange={(e) => setSleepDepth(parseInt(e.target.value))}
                        className="cyber-select py-1 text-xs"
                      >
                        <option value="1">1 (Fast)</option>
                        <option value="2">2 (Deep)</option>
                        <option value="3">3 (Core cleanup)</option>
                      </select>
                    </div>
                    <div className="d-flex align-center gap-2 mt-3">
                      <input 
                        type="checkbox" 
                        id="sleep-clean"
                        checked={sleepCleanup} 
                        onChange={(e) => setSleepCleanup(e.target.checked)}
                        className="rounded"
                        style={{ cursor: 'pointer' }}
                      />
                      <label htmlFor="sleep-clean" className="text-xs text-slate-400 font-mono cursor-pointer">Node cleanup</label>
                    </div>
                  </div>

                  {sleepStats && (
                    <div className="p-2 bg-slate-900 rounded text-xs font-mono text-emerald border border-emerald-950">
                      <span>✓ Cleaned concepts: {sleepStats.removed_nodes_count || 0}</span>
                    </div>
                  )}

                  <button 
                    onClick={handleSleep} 
                    disabled={isSleeping}
                    className="cyber-btn py-1.5 text-xs mt-1"
                  >
                    <Moon style={{ width: '14px', height: '14px' }} />
                    <span>{isSleeping ? t('sleepProgress') : t('sleepBtn')}</span>
                  </button>
                </div>

                {/* Curiosity questions list */}
                <div className="d-flex flex-column gap-2">
                  <h4 className="text-xs font-bold text-amber font-mono d-flex align-center gap-1-5">
                    <HelpCircle style={{ width: '14px', height: '14px' }} />
                    <span>{t('curiosityTitle')}</span>
                  </h4>
                  <p className="text-xs text-slate-400">{t('curiositySub')}</p>
                  
                  {curiosityQuestions.length === 0 ? (
                    <div className="p-3 bg-slate-900-40 rounded text-center text-xs text-slate-500">
                      {t('noCuriosity')}
                    </div>
                  ) : (
                    <div className="d-flex flex-column gap-2">
                      {curiosityQuestions.map((q, idx) => (
                        <div 
                          key={idx} 
                          onClick={() => {
                            // Fill chat input with curiosity question
                            setActiveTab('chat');
                            setChatInput(q.question);
                          }}
                          className="p-2 bg-slate-950-60 hover-bg-slate-900-80 rounded border border-slate-800 cursor-pointer d-flex justify-between align-center transition"
                        >
                          <span className="text-xs text-slate-300 font-medium">{q.question}</span>
                          <span className="text-xs font-mono px-2 py-0.5 rounded" style={{ backgroundColor: 'rgba(245, 158, 11, 0.1)', border: '1px solid rgba(245, 158, 11, 0.2)', color: 'var(--neon-amber)' }}>
                            {q.mystery_score ? `${q.mystery_score.toFixed(0)}%` : '50%'}
                          </span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

              </div>
            )}

            {/* Tab: Database Control & Ingestion */}
            {activeTab === 'db' && (
              <div className="d-flex flex-column gap-3 flex-grow overflow-y-auto max-h-350 pr-1">
                <h3 className="text-xs font-bold font-mono text-cyan uppercase tracking-wider">{t('ingestJsonTitle')}</h3>
                
                <form onSubmit={handleImportJson} className="d-flex flex-column gap-2">
                  <div className="d-flex flex-column gap-1 mb-1">
                    <label className="text-xs text-slate-400 font-mono">
                      {lang === 'ar' ? 'اختر ملف JSON أو اسحبه هنا:' : 'Select JSON file:'}
                    </label>
                    <input
                      type="file"
                      accept=".json"
                      onChange={(e) => {
                        const file = e.target.files[0];
                        if (file) {
                          const reader = new FileReader();
                          reader.onload = (event) => {
                            setJsonInput(event.target.result);
                          };
                          reader.readAsText(file);
                        }
                      }}
                      className="text-xs text-slate-400 file:mr-2 file:py-1 file:px-2 file:rounded file:border-0 file:text-xs file:font-semibold file:bg-cyan-950-60 file:text-cyan hover:file:bg-cyan-900 cursor-pointer"
                    />
                  </div>
                  
                  <textarea
                    value={jsonInput}
                    onChange={(e) => setJsonInput(e.target.value)}
                    placeholder={t('jsonTextPlaceholder')}
                    className="cyber-input p-2 text-xs font-mono"
                    rows="6"
                    style={{ resize: 'vertical', minHeight: '100px' }}
                    required
                  />
                  <button type="submit" className="cyber-btn py-1.5 text-xs">
                    <Server style={{ width: '14px', height: '14px' }} />
                    <span>{t('ingestBtn')}</span>
                  </button>
                </form>

                {importStats && (
                  <div className="p-2.5 bg-slate-950-80 rounded border border-cyan-900-40 text-[11px] font-mono text-cyan animate-pulse">
                    <div className="font-bold border-b border-cyan-950 pb-1 mb-1 text-xs">📊 IMPORT RESULTS:</div>
                    <div className="grid grid-cols-2 gap-x-2 gap-y-1">
                      <span>• {t('conceptsAdded')}: <b>{importStats.concepts_added}</b></span>
                      <span>• {t('relationsAdded')}: <b>{importStats.relations_added}</b></span>
                      <span>• {t('rulesAdded')}: <b>{importStats.inference_rules_added}</b></span>
                      <span>• {t('factsAdded')}: <b>{importStats.facts_added}</b></span>
                      <span>• Personas: <b>{importStats.personas_added}</b></span>
                      <span>• Lang rules: <b>{importStats.language_rules_updated ? 'Updated' : 'No change'}</b></span>
                    </div>
                  </div>
                )}

                {dbMessage && (
                  <div className={`p-2 rounded text-xs border ${
                    dbMessage.type === 'success' 
                      ? 'bg-emerald-950-60 border-emerald-800 text-emerald' 
                      : 'bg-red-950-60 border-red-800 text-red'
                  }`}>
                    {dbMessage.text}
                  </div>
                )}

                <div className="border-t border-slate-800 my-2"></div>

                {/* Delete specific world */}
                <h4 className="text-xs font-bold text-slate-400 font-mono uppercase tracking-wider">{t('deleteWorldTitle')}</h4>
                <div className="d-flex gap-2">
                  <select
                    value={worldToDelete}
                    onChange={(e) => setWorldToDelete(e.target.value)}
                    className="cyber-select py-1 px-2 text-xs flex-grow"
                  >
                    <option value="">-- Choose World --</option>
                    {Array.from(new Set([...(status.worlds || []), ...customWorlds, 'reality', 'khayali'])).map(w => (
                      <option key={w} value={w}>{w}</option>
                    ))}
                  </select>
                  <button
                    onClick={() => {
                      if (!worldToDelete) return;
                      handleClearDb('world', worldToDelete);
                      setWorldToDelete('');
                    }}
                    disabled={!worldToDelete}
                    className="cyber-btn py-1 px-3 text-xs text-red bg-red-950-20 hover-bg-red-900-40"
                    style={{ borderColor: 'rgba(239, 68, 68, 0.3)' }}
                  >
                    <Trash2 style={{ width: '14px', height: '14px' }} />
                    <span>{t('deleteWorldBtn')}</span>
                  </button>
                </div>

                <div className="border-t border-slate-800 my-2"></div>

                {/* Danger Zone */}
                <h4 className="text-xs font-bold text-red font-mono uppercase tracking-wider d-flex align-center gap-1.5">
                  <ShieldAlert style={{ width: '14px', height: '14px' }} />
                  <span>{t('dangerZoneTitle')}</span>
                </h4>
                <div className="d-flex flex-column gap-2">
                  <button
                    onClick={() => handleClearDb('facts')}
                    className="w-full cyber-btn py-2 text-xs text-red bg-red-950-10 hover-bg-red-900-30 d-flex align-center justify-center gap-2"
                    style={{ borderColor: 'rgba(239, 68, 68, 0.4)' }}
                  >
                    <Trash2 style={{ width: '14px', height: '14px' }} />
                    <span>{t('clearFactsBtn')}</span>
                  </button>
                  <button
                    onClick={() => handleClearDb('all')}
                    className="w-full cyber-btn py-2 text-xs text-red bg-red-950-20 hover-bg-red-900-40 d-flex align-center justify-center gap-2"
                    style={{ borderColor: 'rgba(239, 68, 68, 0.6)' }}
                  >
                    <ShieldAlert style={{ width: '14px', height: '14px' }} />
                    <span>{t('clearAllBtn')}</span>
                  </button>
                </div>
              </div>
            )}

            {/* Tab: Sequential Cognitive Procedures */}
            {activeTab === 'procedural' && (
              <div className="d-flex flex-column gap-3 flex-grow overflow-y-auto max-h-450 pr-1">
                <h3 className="text-xs font-bold font-mono text-cyan uppercase tracking-wider">{t('proceduralTitle')}</h3>
                <p className="text-[11px] text-slate-400 mb-2">{t('proceduralSub')}</p>

                {/* Status Message */}
                {proceduralMessage && (
                  <div className={`p-2 rounded text-xs border ${
                    proceduralMessage.type === 'success' 
                      ? 'bg-emerald-950-60 border-emerald-800 text-emerald' 
                      : 'bg-red-950-60 border-red-800 text-red'
                  }`}>
                    {proceduralMessage.text}
                  </div>
                )}

                {/* 1. Existing Procedures List */}
                <div className="p-3 bg-slate-950-50 rounded border border-slate-800 d-flex flex-column gap-2 mb-2">
                  <h4 className="text-xs font-bold text-cyan font-mono uppercase tracking-wider">
                    {lang === 'ar' ? 'الإجراءات المسجلة' : 'Registered Procedures'}
                  </h4>
                  {Object.keys(procedures).length === 0 ? (
                    <div className="text-center text-xs text-slate-500 py-3">{t('noProcedures')}</div>
                  ) : (
                    <div className="d-flex flex-column gap-3 max-h-200 overflow-y-auto pr-1">
                      {Object.entries(procedures).map(([name, steps]) => (
                        <div key={name} className="p-2 bg-slate-900 rounded border border-slate-800 d-flex flex-column gap-1">
                          <div className="d-flex justify-between align-center border-b border-slate-800 pb-1 mb-1">
                            <span className="text-xs font-mono font-bold text-purple">{name}</span>
                            <button
                              onClick={() => handleDeleteProcedure(name)}
                              className="cyber-btn py-0.5 px-2 text-xs text-red hover-bg-red-950-40"
                              style={{ height: '20px', minWidth: 'auto', borderColor: 'rgba(239, 68, 68, 0.4)' }}
                            >
                              {t('deleteBtn')}
                            </button>
                          </div>
                          <ol className="list-decimal list-inside text-[11px] text-slate-300 d-flex flex-column gap-1 pl-1">
                            {steps.map((step, idx) => (
                              <li key={idx} className="font-medium">{step}</li>
                            ))}
                          </ol>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                {/* 2. Create Manually Form */}
                <div className="p-3 bg-slate-950-50 rounded border border-slate-800 d-flex flex-column gap-2">
                  <h4 className="text-xs font-bold text-cyan font-mono uppercase tracking-wider">
                    {t('addProcedureTitle')}
                  </h4>
                  <form onSubmit={handleSaveProcedure} className="d-flex flex-column gap-2">
                    <input
                      type="text"
                      placeholder={t('procedureNamePlaceholder')}
                      value={newProcedureName}
                      onChange={(e) => setNewProcedureName(e.target.value)}
                      className="cyber-input py-1.5 text-xs w-full"
                      required
                    />

                    {/* Steps Builder list */}
                    <div className="d-flex flex-column gap-1.5 my-1">
                      <span className="text-[10px] text-slate-400 font-mono font-bold">{t('stepsLabel')}</span>
                      {newProcedureSteps.length > 0 && (
                        <div className="d-flex flex-column gap-1 bg-slate-900 p-1.5 rounded border border-slate-800 max-h-120 overflow-y-auto">
                          {newProcedureSteps.map((s, idx) => (
                            <div key={idx} className="d-flex justify-between align-center text-[10px] text-slate-300 gap-2 border-b border-slate-950 pb-0.5">
                              <span className="text-left font-medium">{idx + 1}. {s}</span>
                              <button
                                type="button"
                                onClick={() => setNewProcedureSteps(prev => prev.filter((_, i) => i !== idx))}
                                className="text-red font-bold hover:text-rose-400 p-0.5 bg-none border-none cursor-pointer"
                              >
                                ✕
                              </button>
                            </div>
                          ))}
                        </div>
                      )}
                      <div className="d-flex gap-1.5">
                        <input
                          type="text"
                          placeholder={t('stepPlaceholder')}
                          value={newStepText}
                          onChange={(e) => setNewStepText(e.target.value)}
                          className="cyber-input py-1 px-2 text-xs flex-grow"
                        />
                        <button
                          type="button"
                          onClick={() => {
                            if (newStepText.trim()) {
                              setNewProcedureSteps(prev => [...prev, newStepText.trim()]);
                              setNewStepText('');
                            }
                          }}
                          className="cyber-btn py-1 px-3 text-xs"
                          style={{ minWidth: 'auto' }}
                        >
                          +
                        </button>
                      </div>
                    </div>

                    <button type="submit" className="cyber-btn py-1.5 text-xs mt-1 w-full">
                      <PlusCircle style={{ width: '14px', height: '14px' }} />
                      <span>{t('saveProcedureBtn')}</span>
                    </button>
                  </form>
                </div>

              </div>
            )}

          </div>

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
      {conflictData && (
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
      )}

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
