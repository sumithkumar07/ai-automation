import React, { useState, useEffect, useCallback, useRef, useMemo } from 'react'
import { useParams, useNavigate, useSearchParams } from 'react-router-dom'
import { apiMethods } from '../utils/api'
import { useAccessibility } from '../components/AccessibilityProvider'
import { PerformanceMonitor, usePerformanceTracker } from '../components/PerformanceMonitor'
import { 
  BookmarkIcon,
  PlayIcon,
  ArrowLeftIcon,
  PlusIcon,
  TrashIcon,
  CogIcon,
  SparklesIcon,
  EyeIcon,
  ClockIcon,
  DocumentDuplicateIcon,
  ShareIcon,
  CloudArrowUpIcon,
  BoltIcon,
  MagnifyingGlassIcon,
  Bars3Icon,
  XMarkIcon,
  InformationCircleIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline'
import EnhancedNavbar from '../components/EnhancedNavbar'
import LoadingSpinner from '../components/LoadingSpinner'
import SmartTooltip, { InfoTooltip } from '../components/SmartTooltip'
import EnhancedAIAssistant from '../components/EnhancedAIAssistant'
import toast from 'react-hot-toast'

// Memoized components for performance
const NodePalette = React.memo(({ nodeTypes, onAddNode, searchQuery, onSearchChange, isCollapsed, onToggleCollapse }) => (
  <PerformanceMonitor name="NodePalette">
    <div className={`bg-white border-r border-gray-200 transition-all duration-300 ${isCollapsed ? 'w-16' : 'w-80'} overflow-y-auto`}>
      <div className="p-4 border-b border-gray-200 flex items-center justify-between">
        <div className={`${isCollapsed ? 'hidden' : 'block'}`}>
          <h2 className="font-semibold text-gray-900">Node Library</h2>
          <p className="text-sm text-gray-600">50+ nodes across 4 categories</p>
        </div>
        <button
          onClick={onToggleCollapse}
          className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          aria-label={isCollapsed ? 'Expand node palette' : 'Collapse node palette'}
        >
          {isCollapsed ? <Bars3Icon className="w-5 h-5" /> : <XMarkIcon className="w-5 h-5" />}
        </button>
      </div>
      
      {!isCollapsed && (
        <>
          <div className="p-4 border-b border-gray-200">
            <div className="relative">
              <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search 50+ nodes..."
                value={searchQuery}
                onChange={(e) => onSearchChange(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              />
            </div>
          </div>
          
          <div className="p-4 space-y-6">
            {Object.entries(nodeTypes.categories || {}).map(([category, categoryNodes]) => {
              const filteredNodes = categoryNodes.filter(node => 
                node.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                node.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
                node.category?.toLowerCase().includes(searchQuery.toLowerCase())
              )
              
              if (filteredNodes.length === 0) return null
              
              // Separate basic and advanced nodes
              const basicNodes = filteredNodes.filter(node => node.category === 'basic' || !node.category)
              const advancedNodes = filteredNodes.filter(node => node.category === 'advanced')
              
              return (
                <div key={category}>
                  <h3 className="font-medium text-gray-900 mb-3 capitalize flex items-center">
                    {getCategoryIcon(category)}
                    <span className="ml-2">{category.replace('_', ' ')}</span>
                    <InfoTooltip content={`${filteredNodes.length} nodes available in this category`} />
                  </h3>
                  
                  {/* Basic Nodes */}
                  {basicNodes.length > 0 && (
                    <div className="mb-4">
                      <h4 className="text-xs uppercase tracking-wide text-gray-500 mb-2">Essential</h4>
                      <div className="node-palette">
                        {basicNodes.map((nodeType) => (
                          <SmartTooltip key={nodeType.id} content={nodeType.description} placement="right">
                            <div 
                              className="node-item group" 
                              onClick={() => onAddNode(nodeType)}
                              onKeyDown={(e) => {
                                if (e.key === 'Enter' || e.key === ' ') {
                                  e.preventDefault()
                                  onAddNode(nodeType)
                                }
                              }}
                              tabIndex="0"
                              role="button"
                              aria-label={`Add ${nodeType.name} node`}
                            >
                              <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-blue-600 rounded-lg flex items-center justify-center group-hover:scale-110 transition-transform">
                                <span className="text-white text-xs font-bold">{nodeType.name.charAt(0)}</span>
                              </div>
                              <div className="flex-1 min-w-0">
                                <div className="font-medium text-gray-900 truncate">{nodeType.name}</div>
                                <div className="text-xs text-gray-600 truncate">{nodeType.description}</div>
                              </div>
                            </div>
                          </SmartTooltip>
                        ))}
                      </div>
                    </div>
                  )}
                  
                  {/* Advanced Nodes */}
                  {advancedNodes.length > 0 && (
                    <div>
                      <h4 className="text-xs uppercase tracking-wide text-purple-600 mb-2 flex items-center">
                        <SparklesIcon className="w-3 h-3 mr-1" />
                        Advanced
                      </h4>
                      <div className="node-palette">
                        {advancedNodes.map((nodeType) => (
                          <SmartTooltip key={nodeType.id} content={`${nodeType.description} (Advanced)`} placement="right">
                            <div 
                              className="node-item group border-purple-200 hover:border-purple-400 hover:bg-purple-50" 
                              onClick={() => onAddNode(nodeType)}
                              onKeyDown={(e) => {
                                if (e.key === 'Enter' || e.key === ' ') {
                                  e.preventDefault()
                                  onAddNode(nodeType)
                                }
                              }}
                              tabIndex="0"
                              role="button"
                              aria-label={`Add ${nodeType.name} advanced node`}
                            >
                              <div className="w-8 h-8 bg-gradient-to-r from-purple-500 to-purple-600 rounded-lg flex items-center justify-center group-hover:scale-110 transition-transform relative">
                                <span className="text-white text-xs font-bold">{nodeType.name.charAt(0)}</span>
                                <SparklesIcon className="w-3 h-3 text-yellow-300 absolute -top-1 -right-1" />
                              </div>
                              <div className="flex-1 min-w-0">
                                <div className="font-medium text-gray-900 truncate flex items-center">
                                  {nodeType.name}
                                  <span className="ml-1 px-1 py-0.5 bg-purple-100 text-purple-700 text-xs rounded">Pro</span>
                                </div>
                                <div className="text-xs text-gray-600 truncate">{nodeType.description}</div>
                              </div>
                            </div>
                          </SmartTooltip>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )
            })}
            
            {/* Category Stats */}
            <div className="mt-6 p-3 bg-gray-50 rounded-lg">
              <h4 className="text-xs font-medium text-gray-700 mb-2">Node Library Stats</h4>
              <div className="text-xs text-gray-600 space-y-1">
                <div className="flex justify-between">
                  <span>Total Nodes:</span>
                  <span className="font-medium">{Object.values(nodeTypes.categories || {}).flat().length}</span>
                </div>
                <div className="flex justify-between">
                  <span>Categories:</span>
                  <span className="font-medium">{Object.keys(nodeTypes.categories || {}).length}</span>
                </div>
                <div className="flex justify-between">
                  <span>Advanced Nodes:</span>
                  <span className="font-medium text-purple-600">
                    {Object.values(nodeTypes.categories || {}).flat().filter(node => node.category === 'advanced').length}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  </PerformanceMonitor>
))

// Helper function to get category icons
const getCategoryIcon = (category) => {
  switch (category) {
    case 'triggers':
      return <BoltIcon className="w-4 h-4 text-green-600" />
    case 'actions':
      return <RocketLaunchIcon className="w-4 h-4 text-blue-600" />
    case 'logic':
      return <CogIcon className="w-4 h-4 text-orange-600" />
    case 'ai':
      return <SparklesIcon className="w-4 h-4 text-purple-600" />
    default:
      return <CogIcon className="w-4 h-4 text-gray-600" />
  }
}

const WorkflowCanvas = React.memo(({ nodes, connections, selectedNode, onNodeSelect, onNodeDelete, onNodeMove, canvasRef }) => {
  const [isDragging, setIsDragging] = useState(false)
  const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 })
  const [dragNodeId, setDragNodeId] = useState(null)

  const handleNodeMouseDown = useCallback((e, node) => {
    e.preventDefault()
    setIsDragging(true)
    setDragNodeId(node.id)
    
    const rect = canvasRef.current.getBoundingClientRect()
    setDragOffset({
      x: e.clientX - rect.left - node.x,
      y: e.clientY - rect.top - node.y
    })
    
    onNodeSelect(node)
  }, [canvasRef, onNodeSelect])

  const handleMouseMove = useCallback((e) => {
    if (!isDragging || !dragNodeId) return
    
    const rect = canvasRef.current.getBoundingClientRect()
    const newX = Math.max(0, Math.min(e.clientX - rect.left - dragOffset.x, rect.width - 200))
    const newY = Math.max(0, Math.min(e.clientY - rect.top - dragOffset.y, rect.height - 100))
    
    onNodeMove(dragNodeId, { x: newX, y: newY })
  }, [isDragging, dragNodeId, dragOffset, canvasRef, onNodeMove])

  const handleMouseUp = useCallback(() => {
    setIsDragging(false)
    setDragNodeId(null)
  }, [])

  useEffect(() => {
    if (isDragging) {
      document.addEventListener('mousemove', handleMouseMove)
      document.addEventListener('mouseup', handleMouseUp)
    }
    
    return () => {
      document.removeEventListener('mousemove', handleMouseMove)
      document.removeEventListener('mouseup', handleMouseUp)
    }
  }, [isDragging, handleMouseMove, handleMouseUp])

  return (
    <div 
      ref={canvasRef} 
      className="flex-1 h-full bg-gray-50 relative overflow-hidden"
      style={{ 
        backgroundImage: `radial-gradient(circle, #e5e7eb 1px, transparent 1px)`, 
        backgroundSize: '20px 20px' 
      }}
      role="main"
      aria-label="Workflow canvas"
    >
      {/* Grid lines for better alignment */}
      <svg className="absolute inset-0 pointer-events-none" style={{ zIndex: 0 }}>
        <defs>
          <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
            <path d="M 20 0 L 0 0 0 20" fill="none" stroke="#e5e7eb" strokeWidth="0.5"/>
          </pattern>
        </defs>
        <rect width="100%" height="100%" fill="url(#grid)" />
      </svg>

      {/* Workflow Nodes */}
      {nodes.map((node) => (
        <div 
          key={node.id} 
          className={`absolute workflow-node p-4 group ${selectedNode?.id === node.id ? 'selected ring-2 ring-primary-500' : ''}`} 
          style={{ left: node.x, top: node.y, width: '200px', minHeight: '80px' }}
          onMouseDown={(e) => handleNodeMouseDown(e, node)}
          onClick={() => onNodeSelect(node)}
          onKeyDown={(e) => {
            if (e.key === 'Delete' || e.key === 'Backspace') {
              e.preventDefault()
              onNodeDelete(node.id)
            }
          }}
          tabIndex="0"
          role="button"
          aria-label={`${node.name} node`}
          aria-selected={selectedNode?.id === node.id}
        >
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center space-x-2 flex-1 min-w-0">
              <div className="w-6 h-6 bg-gradient-to-r from-primary-500 to-accent-500 rounded flex items-center justify-center shrink-0">
                <span className="text-white text-xs font-bold">{node.name.charAt(0)}</span>
              </div>
              <span className="font-medium text-gray-900 truncate">{node.name}</span>
            </div>
            <SmartTooltip content="Delete node">
              <button 
                onClick={(e) => { 
                  e.stopPropagation() 
                  onNodeDelete(node.id) 
                }} 
                className="opacity-0 group-hover:opacity-100 text-red-500 hover:text-red-700 p-1 rounded transition-all"
                aria-label={`Delete ${node.name} node`}
              >
                <TrashIcon className="w-4 h-4" />
              </button>
            </SmartTooltip>
          </div>
          
          <div className="text-sm text-gray-600 mb-2">
            <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
              {node.type}
            </span>
          </div>
          
          {/* Node configuration preview */}
          {Object.keys(node.config || {}).length > 0 && (
            <div className="text-xs text-gray-500 truncate">
              {Object.keys(node.config).length} config{Object.keys(node.config).length > 1 ? 's' : ''}
            </div>
          )}
          
          {/* Connection points */}
          <div className="absolute -left-2 top-1/2 transform -translate-y-1/2 w-4 h-4 bg-primary-500 rounded-full border-2 border-white shadow-sm" />
          <div className="absolute -right-2 top-1/2 transform -translate-y-1/2 w-4 h-4 bg-primary-500 rounded-full border-2 border-white shadow-sm" />
        </div>
      ))}

      {/* Connections */}
      <svg className="absolute inset-0 pointer-events-none" style={{ zIndex: 1 }}>
        {connections.map((connection) => {
          const fromNode = nodes.find(n => n.id === connection.from)
          const toNode = nodes.find(n => n.id === connection.to)
          if (!fromNode || !toNode) return null

          const fromX = fromNode.x + 200
          const fromY = fromNode.y + 40
          const toX = toNode.x
          const toY = toNode.y + 40
          
          // Create curved connection
          const midX = (fromX + toX) / 2
          const curve = Math.abs(toX - fromX) * 0.3
          
          return (
            <g key={connection.id}>
              <path
                d={`M ${fromX} ${fromY} C ${midX + curve} ${fromY}, ${midX - curve} ${toY}, ${toX} ${toY}`}
                stroke="#6b7280"
                strokeWidth="2"
                fill="none"
                markerEnd="url(#arrowhead)"
                className="workflow-connection hover:stroke-primary-500 transition-colors"
              />
            </g>
          )
        })}
        
        <defs>
          <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
            <polygon points="0 0, 10 3.5, 0 7" fill="#6b7280" />
          </marker>
        </defs>
      </svg>

      {/* Empty state */}
      {nodes.length === 0 && (
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="text-center max-w-md">
            <CogIcon className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Start Building Your Workflow</h3>
            <p className="text-gray-600 mb-6">
              Add nodes from the palette on the left or use AI to generate a complete workflow from your description.
            </p>
            <div className="flex flex-col sm:flex-row gap-3 justify-center">
              <button className="btn-primary inline-flex items-center">
                <SparklesIcon className="w-4 h-4 mr-2" />
                Generate with AI
              </button>
              <button className="btn-secondary inline-flex items-center">
                <PlusIcon className="w-4 h-4 mr-2" />
                Add First Node
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
})

const PropertyPanel = React.memo(({ selectedNode, onUpdateNode, isCollapsed, onToggleCollapse }) => {
  const [configText, setConfigText] = useState('')
  const [validationError, setValidationError] = useState('')

  useEffect(() => {
    if (selectedNode) {
      setConfigText(JSON.stringify(selectedNode.config || {}, null, 2))
      setValidationError('')
    }
  }, [selectedNode])

  const handleConfigChange = (value) => {
    setConfigText(value)
    try {
      const config = JSON.parse(value)
      onUpdateNode(selectedNode.id, { config })
      setValidationError('')
    } catch (error) {
      setValidationError('Invalid JSON configuration')
    }
  }

  if (!selectedNode) {
    return (
      <div className={`bg-white border-l border-gray-200 transition-all duration-300 ${isCollapsed ? 'w-16' : 'w-80'} overflow-y-auto`}>
        <div className="p-4 border-b border-gray-200 flex items-center justify-between">
          {!isCollapsed && <h2 className="font-semibold text-gray-900">Properties</h2>}
          <button
            onClick={onToggleCollapse}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            aria-label={isCollapsed ? 'Expand property panel' : 'Collapse property panel'}
          >
            {isCollapsed ? <Bars3Icon className="w-5 h-5" /> : <XMarkIcon className="w-5 h-5" />}
          </button>
        </div>
        {!isCollapsed && (
          <div className="p-4 text-center text-gray-500">
            <InformationCircleIcon className="w-8 h-8 mx-auto mb-2 text-gray-300" />
            <p className="text-sm">Select a node to view its properties</p>
          </div>
        )}
      </div>
    )
  }

  return (
    <PerformanceMonitor name="PropertyPanel">
      <div className={`bg-white border-l border-gray-200 transition-all duration-300 ${isCollapsed ? 'w-16' : 'w-80'} overflow-y-auto`}>
        <div className="p-4 border-b border-gray-200 flex items-center justify-between">
          {!isCollapsed && (
            <div>
              <h2 className="font-semibold text-gray-900">Node Properties</h2>
              <p className="text-sm text-gray-600 truncate">{selectedNode.name}</p>
            </div>
          )}
          <button
            onClick={onToggleCollapse}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            aria-label={isCollapsed ? 'Expand property panel' : 'Collapse property panel'}
          >
            {isCollapsed ? <Bars3Icon className="w-5 h-5" /> : <XMarkIcon className="w-5 h-5" />}
          </button>
        </div>
        
        {!isCollapsed && (
          <div className="p-4 space-y-4">
            <div className="form-group">
              <label className="form-label">Node Name</label>
              <input 
                type="text" 
                value={selectedNode.name} 
                onChange={(e) => onUpdateNode(selectedNode.id, { name: e.target.value })} 
                className="input-field" 
                placeholder="Enter node name"
              />
            </div>
            
            <div className="form-group">
              <label className="form-label">Node Type</label>
              <div className="px-3 py-2 bg-gray-50 rounded-lg text-sm text-gray-600 border">
                {selectedNode.type}
              </div>
            </div>
            
            <div className="form-group">
              <label className="form-label flex items-center">
                Configuration
                <InfoTooltip content="JSON configuration for this node. Must be valid JSON." />
              </label>
              <textarea 
                value={configText}
                onChange={(e) => handleConfigChange(e.target.value)}
                className={`input-field h-32 font-mono text-sm ${validationError ? 'border-red-300 focus:border-red-500 focus:ring-red-500' : ''}`}
                placeholder="{}"
                spellCheck="false"
              />
              {validationError && (
                <div className="form-error flex items-center">
                  <ExclamationTriangleIcon className="w-4 h-4 mr-1" />
                  {validationError}
                </div>
              )}
            </div>
            
            <div className="form-group">
              <label className="form-label">Position</label>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="text-xs text-gray-500">X</label>
                  <input 
                    type="number" 
                    value={Math.round(selectedNode.x)}
                    onChange={(e) => onUpdateNode(selectedNode.id, { x: parseInt(e.target.value) || 0 })}
                    className="input-field text-sm"
                  />
                </div>
                <div>
                  <label className="text-xs text-gray-500">Y</label>
                  <input 
                    type="number" 
                    value={Math.round(selectedNode.y)}
                    onChange={(e) => onUpdateNode(selectedNode.id, { y: parseInt(e.target.value) || 0 })}
                    className="input-field text-sm"
                  />
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </PerformanceMonitor>
  )
})

const EnhancedWorkflowEditor = () => {
  const { workflowId } = useParams()
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const { announceToScreenReader } = useAccessibility()
  const { trackOperation } = usePerformanceTracker('WorkflowEditor')
  
  // State management
  const [workflow, setWorkflow] = useState(null)
  const [nodes, setNodes] = useState([])
  const [connections, setConnections] = useState([])
  const [selectedNode, setSelectedNode] = useState(null)
  const [nodeTypes, setNodeTypes] = useState({})
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [lastSaved, setLastSaved] = useState(null)
  const [nodeSearchQuery, setNodeSearchQuery] = useState('')
  
  // UI state
  const [showAiAssistant, setShowAiAssistant] = useState(false)
  const [nodePaletteCollapsed, setNodePaletteCollapsed] = useState(false)
  const [propertyPanelCollapsed, setPropertyPanelCollapsed] = useState(false)
  const [aiPrompt, setAiPrompt] = useState('')
  const [aiLoading, setAiLoading] = useState(false)
  const [aiSessionId] = useState(`editor-${Date.now()}`)
  
  // Refs
  const canvasRef = useRef(null)
  const autosaveTimeout = useRef(null)

  // Load initial data
  useEffect(() => { 
    loadInitialData() 
  }, [workflowId])

  // Handle AI-generated workflow from URL params
  useEffect(() => {
    const aiWorkflow = searchParams.get('ai-workflow')
    if (aiWorkflow) {
      try {
        const workflowData = JSON.parse(decodeURIComponent(aiWorkflow))
        setNodes(workflowData.nodes || [])
        setConnections(workflowData.connections || [])
        setWorkflow(prev => ({ 
          ...prev, 
          name: workflowData.name || prev?.name || 'AI Generated Workflow',
          description: workflowData.description || prev?.description || 'Generated by AI'
        }))
        announceToScreenReader('AI generated workflow loaded successfully')
      } catch (error) {
        console.error('Failed to parse AI workflow:', error)
      }
    }
  }, [searchParams, announceToScreenReader])

  // Auto-save functionality
  useEffect(() => {
    if (workflow && (nodes.length > 0 || connections.length > 0)) {
      if (autosaveTimeout.current) {
        clearTimeout(autosaveTimeout.current)
      }
      
      autosaveTimeout.current = setTimeout(async () => {
        if (workflowId) {
          try {
            await apiMethods.autosaveWorkflow(workflowId, {
              nodes,
              connections,
              triggers: workflow.triggers || []
            })
            setLastSaved(new Date())
          } catch (error) {
            console.error('Auto-save failed:', error)
          }
        }
      }, 2000)
    }

    return () => {
      if (autosaveTimeout.current) {
        clearTimeout(autosaveTimeout.current)
      }
    }
  }, [nodes, connections, workflow, workflowId])

  const loadInitialData = trackOperation(async () => {
    try {
      const nodeTypesRes = await apiMethods.getNodeTypes()
      setNodeTypes(nodeTypesRes)

      if (workflowId) {
        const workflowData = await apiMethods.getWorkflow(workflowId)
        setWorkflow(workflowData)
        setNodes(workflowData.nodes || [])
        setConnections(workflowData.connections || [])
        announceToScreenReader(`Workflow ${workflowData.name} loaded successfully`)
      } else {
        setWorkflow({ 
          name: 'Untitled Workflow', 
          description: '', 
          nodes: [], 
          connections: [], 
          triggers: [] 
        })
      }
    } catch (error) {
      console.error('Error loading data:', error)
      toast.error('Failed to load workflow data')
    } finally {
      setLoading(false)
    }
  })

  const addNode = useCallback((nodeType) => {
    const newNode = { 
      id: `node-${Date.now()}`, 
      type: nodeType.id, 
      name: nodeType.name, 
      x: Math.max(50, Math.random() * (canvasRef.current?.clientWidth - 250) || 200), 
      y: Math.max(50, Math.random() * (canvasRef.current?.clientHeight - 150) || 200), 
      config: {} 
    }
    setNodes(prev => [...prev, newNode])
    setSelectedNode(newNode)
    announceToScreenReader(`Added ${nodeType.name} node to workflow`)
  }, [announceToScreenReader])

  const updateNode = useCallback((nodeId, updates) => {
    setNodes(prev => prev.map(node => 
      node.id === nodeId ? { ...node, ...updates } : node
    ))
    if (selectedNode?.id === nodeId) {
      setSelectedNode(prev => ({ ...prev, ...updates }))
    }
  }, [selectedNode])

  const deleteNode = useCallback((nodeId) => {
    const node = nodes.find(n => n.id === nodeId)
    setNodes(prev => prev.filter(node => node.id !== nodeId))
    setConnections(prev => prev.filter(conn => conn.from !== nodeId && conn.to !== nodeId))
    if (selectedNode?.id === nodeId) setSelectedNode(null)
    announceToScreenReader(`Deleted ${node?.name || 'node'} from workflow`)
  }, [nodes, selectedNode, announceToScreenReader])

  const moveNode = useCallback((nodeId, position) => {
    updateNode(nodeId, position)
  }, [updateNode])

  const saveWorkflow = trackOperation(async () => {
    if (!workflow) return
    setSaving(true)
    try {
      const workflowData = { 
        name: workflow.name, 
        description: workflow.description, 
        nodes, 
        connections, 
        triggers: workflow.triggers || [] 
      }
      
      if (workflowId) {
        await apiMethods.updateWorkflow(workflowId, workflowData)
        toast.success('Workflow saved successfully!')
        announceToScreenReader('Workflow saved successfully')
      } else {
        const newWorkflow = await apiMethods.createWorkflow(workflowData)
        navigate(`/editor/${newWorkflow.id}`, { replace: true })
        toast.success('Workflow created successfully!')
        announceToScreenReader('Workflow created successfully')
      }
      setLastSaved(new Date())
    } catch (error) {
      console.error('Error saving workflow:', error)
      toast.error('Failed to save workflow')
    } finally {
      setSaving(false)
    }
  })

  const executeWorkflow = trackOperation(async () => {
    if (!workflowId) { 
      toast.error('Please save the workflow before executing') 
      return 
    }
    try {
      const idempotencyKey = `execute-${workflowId}-${Date.now()}`
      const result = await apiMethods.executeWorkflow(workflowId, idempotencyKey)
      toast.success(`Workflow execution started! ID: ${result.execution_id}`)
      announceToScreenReader(`Workflow execution started with ID ${result.execution_id}`)
    } catch (error) {
      console.error('Error executing workflow:', error)
      toast.error('Failed to execute workflow')
    }
  })

  const handleAIWorkflowGenerated = (workflowData) => {
    setNodes(workflowData.nodes || [])
    setConnections(workflowData.connections || [])
    setWorkflow(prev => ({ 
      ...prev, 
      name: workflowData.name || prev.name, 
      description: workflowData.description || prev.description 
    }))
    setShowAiAssistant(false)
    announceToScreenReader('AI generated workflow applied successfully')
  }

  // Memoized filtered node types for search
  const filteredNodeTypes = useMemo(() => {
    if (!nodeSearchQuery) return nodeTypes
    
    const filtered = { categories: {} }
    Object.entries(nodeTypes.categories || {}).forEach(([category, nodes]) => {
      const filteredNodes = nodes.filter(node => 
        node.name.toLowerCase().includes(nodeSearchQuery.toLowerCase()) ||
        node.description.toLowerCase().includes(nodeSearchQuery.toLowerCase())
      )
      if (filteredNodes.length > 0) {
        filtered.categories[category] = filteredNodes
      }
    })
    return filtered
  }, [nodeTypes, nodeSearchQuery])

  if (loading) {
    return (
      <div>
        <EnhancedNavbar />
        <div className="flex items-center justify-center h-96" role="status" aria-label="Loading workflow editor">
          <LoadingSpinner size="large" />
        </div>
      </div>
    )
  }

  return (
    <PerformanceMonitor name="EnhancedWorkflowEditor">
      <div className="min-h-screen bg-gray-50">
        <EnhancedNavbar />
        
        {/* Header */}
        <div className="bg-white border-b border-gray-200 px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <SmartTooltip content="Back to dashboard">
                <button 
                  onClick={() => navigate('/dashboard')} 
                  className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                  aria-label="Back to dashboard"
                >
                  <ArrowLeftIcon className="w-5 h-5" />
                </button>
              </SmartTooltip>
              
              <div className="flex-1">
                <div className="flex items-center space-x-3">
                  <input
                    type="text"
                    value={workflow?.name || 'Untitled Workflow'}
                    onChange={(e) => setWorkflow(prev => ({ ...prev, name: e.target.value }))}
                    className="text-xl font-semibold text-gray-900 bg-transparent border-none focus:outline-none focus:ring-2 focus:ring-primary-500 rounded px-2 py-1"
                    aria-label="Workflow name"
                  />
                  {workflow?.status && (
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      workflow.status === 'active' ? 'bg-green-100 text-green-800' :
                      workflow.status === 'draft' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {workflow.status}
                    </span>
                  )}
                </div>
                
                <div className="flex items-center space-x-4 text-sm text-gray-600 mt-1">
                  <input
                    type="text"
                    value={workflow?.description || ''}
                    onChange={(e) => setWorkflow(prev => ({ ...prev, description: e.target.value }))}
                    placeholder="Add a description..."
                    className="bg-transparent border-none focus:outline-none focus:ring-2 focus:ring-primary-500 rounded px-2 py-1"
                    aria-label="Workflow description"
                  />
                  {lastSaved && (
                    <span className="flex items-center text-green-600">
                      <ClockIcon className="w-4 h-4 mr-1" />
                      Saved {lastSaved.toLocaleTimeString()}
                    </span>
                  )}
                  <span className="flex items-center">
                    <BoltIcon className="w-4 h-4 mr-1" />
                    {nodes.length} nodes
                  </span>
                </div>
              </div>
            </div>

            <div className="flex items-center space-x-3">
              <SmartTooltip content="Get AI help">
                <button 
                  onClick={() => setShowAiAssistant(true)} 
                  className="btn-secondary inline-flex items-center"
                  aria-label="Open AI Assistant"
                >
                  <SparklesIcon className="w-4 h-4 mr-2" /> 
                  AI Assistant
                </button>
              </SmartTooltip>
              
              <SmartTooltip content="Execute workflow">
                <button 
                  onClick={executeWorkflow} 
                  disabled={!workflowId}
                  className="btn-accent inline-flex items-center disabled:opacity-50 disabled:cursor-not-allowed"
                  aria-label="Execute workflow"
                >
                  <PlayIcon className="w-4 h-4 mr-2" /> 
                  Execute
                </button>
              </SmartTooltip>
              
              <SmartTooltip content="Save workflow">
                <button 
                  onClick={saveWorkflow} 
                  disabled={saving}
                  className="btn-primary inline-flex items-center disabled:opacity-50 disabled:cursor-not-allowed"
                  aria-label="Save workflow"
                >
                  {saving ? (
                    <LoadingSpinner size="small" className="mr-2" />
                  ) : (
                    <BookmarkIcon className="w-4 h-4 mr-2" />
                  )}
                  {saving ? 'Saving...' : 'Save'}
                </button>
              </SmartTooltip>
            </div>
          </div>
        </div>

        {/* Main Editor */}
        <div className="flex h-[calc(100vh-128px)]">
          <NodePalette
            nodeTypes={filteredNodeTypes}
            onAddNode={addNode}
            searchQuery={nodeSearchQuery}
            onSearchChange={setNodeSearchQuery}
            isCollapsed={nodePaletteCollapsed}
            onToggleCollapse={() => setNodePaletteCollapsed(!nodePaletteCollapsed)}
          />

          <WorkflowCanvas
            nodes={nodes}
            connections={connections}
            selectedNode={selectedNode}
            onNodeSelect={setSelectedNode}
            onNodeDelete={deleteNode}
            onNodeMove={moveNode}
            canvasRef={canvasRef}
          />

          <PropertyPanel
            selectedNode={selectedNode}
            onUpdateNode={updateNode}
            isCollapsed={propertyPanelCollapsed}
            onToggleCollapse={() => setPropertyPanelCollapsed(!propertyPanelCollapsed)}
          />
        </div>

        {/* AI Assistant Modal */}
        <EnhancedAIAssistant
          isOpen={showAiAssistant}
          onClose={() => setShowAiAssistant(false)}
          onWorkflowGenerated={handleAIWorkflowGenerated}
          sessionId={aiSessionId}
        />
      </div>
    </PerformanceMonitor>
  )
}

export default EnhancedWorkflowEditor