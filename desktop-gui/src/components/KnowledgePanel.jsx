import React from 'react';
import { 
  PlusCircle, Moon, HelpCircle, Server, Zap, Trash2, ShieldAlert
} from 'lucide-react';

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

export default function KnowledgePanel({
  activeTab,
  setActiveTab,
  lang,
  t,
  status,
  customWorlds,

  // Teach tab props
  sourceConcept,
  setSourceConcept,
  targetConcept,
  setTargetConcept,
  selectedRelation,
  setSelectedRelation,
  teachWorld,
  setTeachWorld,
  teachConfidence,
  setTeachConfidence,
  teachModality,
  setTeachModality,
  teachMessage,
  newRelId,
  setNewRelId,
  newRelName,
  setNewRelName,
  newRelTransitive,
  setNewRelTransitive,
  newRelSymmetric,
  setNewRelSymmetric,
  newRelDecay,
  setNewRelDecay,
  relAddMessage,
  handleTeach,
  handleRegisterRelation,

  // Maintenance tab props
  sleepDepth,
  setSleepDepth,
  sleepCleanup,
  setSleepCleanup,
  sleepStats,
  isSleeping,
  curiosityQuestions,
  handleSleep,
  setChatInput,

  // DB tab props
  jsonInput,
  setJsonInput,
  importStats,
  dbMessage,
  worldToDelete,
  setWorldToDelete,
  handleImportJson,
  handleClearDb,

  // Procedural tab props
  procedures,
  newProcedureName,
  setNewProcedureName,
  newProcedureSteps,
  setNewProcedureSteps,
  newStepText,
  setNewStepText,
  proceduralMessage,
  handleSaveProcedure,
  handleDeleteProcedure
}) {
  return (
    <div className="glass-panel flex-grow d-flex flex-column p-4 min-h-380">
      
      {/* Tab: Teach Engine */}
      {activeTab === 'teach' && (
        <div className="d-flex flex-column gap-3 flex-grow">
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
                {Array.from(new Set([...(status.relations || []), ...RELATION_TYPES])).map(rel => {
                  const meta = status.relations_metadata?.find(r => r.id === rel);
                  const displayName = lang === 'ar' && meta?.name ? `${meta.name} (${rel})` : rel;
                  return (
                    <option key={rel} value={rel}>{displayName}</option>
                  );
                })}
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
  );
}
