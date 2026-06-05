import React from 'react';
import { RefreshCw } from 'lucide-react';
import PhysicsGraph from '../PhysicsGraph';

export default function GraphVisualizer({
  graphData = { nodes: [], edges: [] },
  activeNode,
  setActiveNode,
  sourceConcept,
  setSourceConcept,
  targetConcept,
  setTargetConcept,
  fetchGraph,
  lang
}) {
  return (
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
  );
}
