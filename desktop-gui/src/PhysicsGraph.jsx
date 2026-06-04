import React, { useRef, useEffect, useState } from 'react';
import { translations } from './translations';

const PhysicsGraph = ({ nodes = [], edges = [], activeNode = null, onNodeClick = null, lang = 'en' }) => {
  const t = (key) => {
    const langDict = translations[lang] || translations['en'];
    return langDict[key] || translations['en'][key] || key;
  };

  const canvasRef = useRef(null);
  const containerRef = useRef(null);
  
  // Physics states
  const [nodePositions, setNodePositions] = useState({});
  const [draggedNode, setDraggedNode] = useState(null);
  const [zoom, setZoom] = useState(1);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const [hoveredNode, setHoveredNode] = useState(null);
  
  const mouseRef = useRef({ x: 0, y: 0, isDown: false, startPan: { x: 0, y: 0 } });
  const nodePositionsRef = useRef({});
  const particlesRef = useRef([]);
  const alphaRef = useRef(1.0); // Simulated annealing factor

  // Sync incoming nodes to internal positions if they don't exist
  useEffect(() => {
    const newPositions = { ...nodePositionsRef.current };
    let changed = false;
    
    nodes.forEach(node => {
      if (!newPositions[node.id]) {
        const offset = 60;
        const cx = canvasRef.current ? canvasRef.current.width / 2 : 400;
        const cy = canvasRef.current ? canvasRef.current.height / 2 : 300;
        newPositions[node.id] = {
          x: cx + (Math.random() - 0.5) * offset * 2,
          y: cy + (Math.random() - 0.5) * offset * 2,
          vx: 0,
          vy: 0,
          id: node.id,
          type: node.type,
          category: node.category
        };
        changed = true;
      }
    });

    // Remove obsolete nodes
    Object.keys(newPositions).forEach(id => {
      if (!nodes.some(n => n.id === id)) {
        delete newPositions[id];
        changed = true;
      }
    });

    if (changed || Object.keys(nodePositionsRef.current).length === 0) {
      nodePositionsRef.current = newPositions;
      setNodePositions(newPositions);
    }
    alphaRef.current = 1.0; // Re-heat layout when nodes change
  }, [nodes]);

  // Handle active particle spawning along edges
  useEffect(() => {
    const activeParticles = [];
    edges.forEach((edge, index) => {
      const count = 1 + (index % 2);
      for (let i = 0; i < count; i++) {
        activeParticles.push({
          source: edge.source,
          target: edge.target,
          progress: Math.random(),
          speed: 0.003 + Math.random() * 0.005,
          color: edge.relation === 'is_a' ? '#8b5cf6' : '#00f0ff',
          size: 2 + Math.random() * 3
        });
      }
    });
    particlesRef.current = activeParticles;
    alphaRef.current = 1.0; // Re-heat layout
  }, [edges]);

  // Re-heat layout on zoom change
  useEffect(() => {
    alphaRef.current = Math.max(alphaRef.current, 0.85);
  }, [zoom]);

  // Main animation and physics simulation loop
  useEffect(() => {
    let animationId;
    
    const updatePhysicsAndDraw = () => {
      const canvas = canvasRef.current;
      if (!canvas) return;
      const ctx = canvas.getContext('2d');
      const width = canvas.width;
      const height = canvas.height;

      const positions = nodePositionsRef.current;
      const nodeKeys = Object.keys(positions);

      const nodeDegrees = {};
      const nodeOutDegrees = {};
      nodeKeys.forEach(id => {
        nodeDegrees[id] = 0;
        nodeOutDegrees[id] = 0;
      });
      edges.forEach(edge => {
        if (nodeDegrees[edge.source] !== undefined) {
          nodeDegrees[edge.source]++;
          nodeOutDegrees[edge.source]++;
        }
        if (nodeDegrees[edge.target] !== undefined) {
          nodeDegrees[edge.target]++;
        }
      });
      
      const scaleMultiplier = zoom < 1 ? (1 / zoom) : 1;
      const k = 100 * scaleMultiplier; // Spring rest length
      const cRepulsion = 6000 * scaleMultiplier * scaleMultiplier;
      const cSpring = 0.08;
      const damping = 0.85;
      const gravity = 0.06 / scaleMultiplier;

      const isStable = alphaRef.current < 0.008 && !draggedNode;

      if (!isStable) {
        // Repulsion force
        for (let i = 0; i < nodeKeys.length; i++) {
          const nodeA = positions[nodeKeys[i]];
          for (let j = i + 1; j < nodeKeys.length; j++) {
            const nodeB = positions[nodeKeys[j]];
            
            const dx = nodeB.x - nodeA.x;
            const dy = nodeB.y - nodeA.y;
            const distSq = dx * dx + dy * dy + 0.1;
            const dist = Math.sqrt(distSq);
            
            const maxRepelDist = 320 * scaleMultiplier;
            if (dist < maxRepelDist) {
              const force = cRepulsion / distSq;
              const fx = (dx / dist) * force;
              const fy = (dy / dist) * force;
              
              nodeA.vx -= fx * alphaRef.current;
              nodeA.vy -= fy * alphaRef.current;
              nodeB.vx += fx * alphaRef.current;
              nodeB.vy += fy * alphaRef.current;
            }
          }
        }

        // Spring force
        edges.forEach(edge => {
          const nodeA = positions[edge.source];
          const nodeB = positions[edge.target];
          if (nodeA && nodeB) {
            const dx = nodeB.x - nodeA.x;
            const dy = nodeB.y - nodeA.y;
            const dist = Math.sqrt(dx * dx + dy * dy) + 0.1;
            
            const force = cSpring * (dist - k);
            const fx = (dx / dist) * force;
            const fy = (dy / dist) * force;
            
            nodeA.vx += fx * alphaRef.current;
            nodeA.vy += fy * alphaRef.current;
            nodeB.vx -= fx * alphaRef.current;
            nodeB.vy -= fy * alphaRef.current;
          }
        });

        // Apply forces
        nodeKeys.forEach(id => {
          const node = positions[id];
          if (node.id === draggedNode) {
            node.vx = 0;
            node.vy = 0;
            return;
          }

          const cx = width / 2;
          const cy = height / 2;
          node.vx += (cx - node.x) * gravity * alphaRef.current;
          node.vy += (cy - node.y) * gravity * alphaRef.current;

          node.x += node.vx;
          node.y += node.vy;
          node.vx *= damping;
          node.vy *= damping;

          // Soft boundaries
          const distFromCx = node.x - cx;
          const distFromCy = node.y - cy;
          if (Math.abs(distFromCx) > 2000) node.vx -= distFromCx * 0.001;
          if (Math.abs(distFromCy) > 2000) node.vy -= distFromCy * 0.001;
        });

        if (draggedNode) {
          alphaRef.current = Math.max(alphaRef.current * 0.98, 0.25);
        } else {
          alphaRef.current = alphaRef.current * 0.985;
        }
      }

      // Draw
      ctx.clearRect(0, 0, width, height);
      ctx.save();
      ctx.translate(pan.x, pan.y);
      ctx.scale(zoom, zoom);

      // Edges
      edges.forEach(edge => {
        const fromNode = positions[edge.source];
        const toNode = positions[edge.target];
        if (fromNode && toNode) {
          ctx.beginPath();
          ctx.moveTo(fromNode.x, fromNode.y);
          ctx.lineTo(toNode.x, toNode.y);
          
          const isTaxonomy = edge.relation === 'is_a';
          ctx.strokeStyle = isTaxonomy ? 'rgba(139, 92, 246, 0.4)' : 'rgba(0, 240, 255, 0.3)';
          ctx.lineWidth = isTaxonomy ? 2 : 1.5;
          ctx.stroke();

          // Edge labels
          const midX = (fromNode.x + toNode.x) / 2;
          const midY = (fromNode.y + toNode.y) / 2;
          
          ctx.save();
          ctx.font = '9px Tajawal, sans-serif';
          const textWidth = ctx.measureText(edge.relation).width;
          ctx.fillStyle = '#030712';
          ctx.fillRect(midX - textWidth/2 - 4, midY - 6, textWidth + 8, 12);
          
          ctx.fillStyle = isTaxonomy ? '#a78bfa' : '#67e8f9';
          ctx.textAlign = 'center';
          ctx.textBaseline = 'middle';
          ctx.fillText(edge.relation, midX, midY);
          ctx.restore();
        }
      });

      // Synaptic Pulses (Particles)
      const particles = particlesRef.current;
      particles.forEach(p => {
        const fromNode = positions[p.source];
        const toNode = positions[p.target];
        if (fromNode && toNode) {
          p.progress += p.speed;
          if (p.progress >= 1) p.progress = 0;
          
          const px = fromNode.x + (toNode.x - fromNode.x) * p.progress;
          const py = fromNode.y + (toNode.y - fromNode.y) * p.progress;

          ctx.beginPath();
          ctx.arc(px, py, p.size, 0, Math.PI * 2);
          ctx.fillStyle = p.color;
          ctx.shadowBlur = 10;
          ctx.shadowColor = p.color;
          ctx.fill();
          ctx.shadowBlur = 0;
        }
      });

      // Nodes
      nodeKeys.forEach(id => {
        const node = positions[id];
        const isActive = activeNode === node.id;
        const isHovered = hoveredNode === node.id;
        
        const deg = nodeDegrees[node.id] || 0;
        const outDeg = nodeOutDegrees[node.id] || 0;

        const isIsolated = deg === 0;
        const isTerminal = deg > 0 && outDeg === 0;

        const baseRadius = 15 + Math.min(20, deg * 2.5);
        const radius = isActive ? (baseRadius + 6) : (isHovered ? (baseRadius + 3) : baseRadius);

        let fillColor = '#090d1f';
        let strokeColor = '#00f0ff';
        let labelColor = '#f8fafc';
        let glowColor = strokeColor;

        if (isIsolated) {
          fillColor = '#1c1202';
          strokeColor = '#f59e0b';
          glowColor = '#f59e0b';
          labelColor = '#fbbf24';
        } else if (isTerminal) {
          fillColor = '#200414';
          strokeColor = '#ec4899';
          glowColor = '#ec4899';
          labelColor = '#fbcfe8';
        } else {
          const isTaxonomy = node.id.includes('_') || node.type === 'class';
          if (isTaxonomy) {
            fillColor = '#3b0764';
            strokeColor = '#8b5cf6';
            glowColor = '#8b5cf6';
            labelColor = '#ddd6fe';
          } else {
            fillColor = '#090d1f';
            strokeColor = '#00f0ff';
            glowColor = '#00f0ff';
            labelColor = '#c8f9ff';
          }
        }

        ctx.beginPath();
        ctx.arc(node.x, node.y, radius, 0, Math.PI * 2);
        
        if (isActive) {
          ctx.shadowBlur = 22;
          ctx.shadowColor = glowColor;
        } else if (isHovered) {
          ctx.shadowBlur = 14;
          ctx.shadowColor = glowColor;
        } else if (deg >= 4) {
          ctx.shadowBlur = 8;
          ctx.shadowColor = glowColor;
        }

        ctx.fillStyle = fillColor;
        ctx.fill();
        
        ctx.strokeStyle = strokeColor;
        ctx.lineWidth = isActive ? 3 : 1.5;
        ctx.stroke();
        
        ctx.shadowBlur = 0;

        // Label
        ctx.font = isActive ? 'bold 11px Tajawal, sans-serif' : '10px Tajawal, sans-serif';
        ctx.fillStyle = isActive ? '#ffffff' : labelColor;
        ctx.textAlign = 'center';
        ctx.textBaseline = 'top';
        ctx.fillText(node.label || node.id, node.x, node.y + radius + 6);
      });

      ctx.restore();
      animationId = requestAnimationFrame(updatePhysicsAndDraw);
    };

    animationId = requestAnimationFrame(updatePhysicsAndDraw);
    return () => cancelAnimationFrame(animationId);
  }, [edges, activeNode, draggedNode, pan, zoom, hoveredNode]);

  // Handle Resize
  useEffect(() => {
    const canvas = canvasRef.current;
    const container = containerRef.current;
    if (!canvas || !container) return;

    const resizeObserver = new ResizeObserver((entries) => {
      for (let entry of entries) {
        const { width, height } = entry.contentRect;
        canvas.width = width;
        canvas.height = height || 450;
      }
    });

    resizeObserver.observe(container);
    return () => resizeObserver.disconnect();
  }, []);

  const getCanvasCoords = (e) => {
    const rect = canvasRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    return {
      x: (x - pan.x) / zoom,
      y: (y - pan.y) / zoom
    };
  };

  const handleMouseDown = (e) => {
    alphaRef.current = 1.0;
    const coords = getCanvasCoords(e);
    const positions = nodePositionsRef.current;
    
    let clickedNodeId = null;
    Object.keys(positions).forEach(id => {
      const node = positions[id];
      const dist = Math.sqrt(Math.pow(node.x - coords.x, 2) + Math.pow(node.y - coords.y, 2));
      if (dist < 22) clickedNodeId = id;
    });

    if (clickedNodeId) {
      setDraggedNode(clickedNodeId);
      if (onNodeClick) onNodeClick(clickedNodeId);
    } else {
      mouseRef.current.isDown = true;
      mouseRef.current.startPan = { x: e.clientX - pan.x, y: e.clientY - pan.y };
    }
  };

  const handleMouseMove = (e) => {
    const coords = getCanvasCoords(e);
    const positions = nodePositionsRef.current;

    let hoverId = null;
    Object.keys(positions).forEach(id => {
      const node = positions[id];
      const dist = Math.sqrt(Math.pow(node.x - coords.x, 2) + Math.pow(node.y - coords.y, 2));
      if (dist < 22) hoverId = id;
    });
    setHoveredNode(hoverId);

    if (draggedNode && positions[draggedNode]) {
      alphaRef.current = 1.0;
      positions[draggedNode].x = coords.x;
      positions[draggedNode].y = coords.y;
    } else if (mouseRef.current.isDown) {
      setPan({
        x: e.clientX - mouseRef.current.startPan.x,
        y: e.clientY - mouseRef.current.startPan.y
      });
    }
  };

  const handleMouseUp = () => {
    alphaRef.current = 1.0;
    setDraggedNode(null);
    mouseRef.current.isDown = false;
  };

  const handleWheel = (e) => {
    e.preventDefault();
    const zoomFactor = 1.05;
    if (e.deltaY < 0) {
      setZoom(prev => Math.min(prev * zoomFactor, 3));
    } else {
      setZoom(prev => Math.max(prev / zoomFactor, 0.4));
    }
  };

  return (
    <div 
      ref={containerRef} 
      style={{ width: '100%', height: '100%', position: 'relative', cursor: draggedNode ? 'grabbing' : (hoveredNode ? 'pointer' : 'grab') }}
    >
      <canvas
        ref={canvasRef}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
        onWheel={handleWheel}
        style={{ display: 'block', width: '100%', height: '100%' }}
      />
      <div style={{ position: 'absolute', left: '10px', top: '10px', display: 'flex', gap: '5px' }}>
        <button 
          onClick={() => { setZoom(1); setPan({ x: 0, y: 0 }); }}
          className="cyber-btn-secondary" 
          style={{ padding: '4px 10px', fontSize: '11px', borderRadius: '4px' }}
        >
          {t('resetPerspective')}
        </button>
      </div>
      
      {/* Legend Overlay */}
      <div 
        style={{ 
          position: 'absolute', 
          right: '10px', 
          bottom: '10px', 
          display: 'flex', 
          flexDirection: 'column', 
          gap: '6px', 
          backgroundColor: 'rgba(7, 9, 19, 0.85)', 
          backdropFilter: 'blur(8px)', 
          border: '1px solid rgba(0, 240, 255, 0.15)', 
          borderRadius: '8px', 
          padding: '8px 12px', 
          fontSize: '11px', 
          color: '#e2e8f0', 
          pointerEvents: 'none',
          boxShadow: '0 4px 12px rgba(0,0,0,0.5)',
          direction: lang === 'ar' ? 'rtl' : 'ltr',
          zIndex: 10
        }}
      >
        <div style={{ fontWeight: 'bold', borderBottom: '1px solid rgba(255,255,255,0.1)', paddingBottom: '4px', marginBottom: '2px', color: '#00f0ff' }}>
          {t('graphLegendTitle')}
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#00f0ff', boxShadow: '0 0 6px #00f0ff' }}></span>
          <span>{t('legendActiveNode')}</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#8b5cf6', boxShadow: '0 0 6px #8b5cf6' }}></span>
          <span>{t('legendSuperClass')}</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#ec4899', boxShadow: '0 0 6px #ec4899' }}></span>
          <span>{t('legendLeafNode')}</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#f59e0b', boxShadow: '0 0 6px #f59e0b' }}></span>
          <span>{t('legendIsolateNode')}</span>
        </div>
        <div style={{ fontSize: '9px', color: '#94a3b8', borderTop: '1px solid rgba(255,255,255,0.05)', paddingTop: '4px', marginTop: '2px' }}>
          {t('legendScaleNote')}
        </div>
      </div>
    </div>
  );
};

export default PhysicsGraph;
