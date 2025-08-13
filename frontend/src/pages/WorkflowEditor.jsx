import React, { useState, useEffect, useCallback, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { apiMethods } from '../utils/api'
import { 
  BookmarkIcon,
  PlayIcon,
  ArrowLeftIcon,
  PlusIcon,
  TrashIcon,
  CogIcon,
  SparklesIcon,
  EyeIcon,
  ClockIcon
} from '@heroicons/react/24/outline'
import Navbar from '../components/Navbar'
import LoadingSpinner from '../components/LoadingSpinner'
import toast from 'react-hot-toast'

const WorkflowEditor = () => {
  const { workflowId } = useParams()
  const navigate = useNavigate()
  const [workflow, setWorkflow] = useState(null)
  const [nodes, setNodes] = useState([])
  const [connections, setConnections] = useState([])
  const [selectedNode, setSelectedNode] = useState(null)
  const [nodeTypes, setNodeTypes] = useState({})
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [showNodePalette, setShowNodePalette] = useState(true)
  const [showAiAssistant, setShowAiAssistant] = useState(false)
  const [aiPrompt, setAiPrompt] = useState('')
  const [aiLoading, setAiLoading] = useState(false)
  const [aiSessionId] = useState(`session-${Date.now()}`)
  const [lastSaved, setLastSaved] = useState(null)
  const canvasRef = useRef(null)
  const autosaveTimeout = useRef(null)

  useEffect(() => { 
    loadInitialData() 
  }, [workflowId])

  // Auto-save functionality
  useEffect(() => {
    if (workflow && nodes.length > 0) {
      // Clear existing timeout
      if (autosaveTimeout.current) {
        clearTimeout(autosaveTimeout.current)
      }
      
      // Set new timeout for auto-save
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
      }, 2000) // Auto-save after 2 seconds of inactivity
    }

    return () => {
      if (autosaveTimeout.current) {
        clearTimeout(autosaveTimeout.current)
      }
    }
  }, [nodes, connections, workflow, workflowId])

  const loadInitialData = async () => {
    try {
      const nodeTypesRes = await apiMethods.getNodeTypes()
      setNodeTypes(nodeTypesRes)

      if (workflowId) {
        const workflowData = await apiMethods.getWorkflow(workflowId)
        setWorkflow(workflowData)
        setNodes(workflowData.nodes || [])
        setConnections(workflowData.connections || [])
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
  }

  const addNode = useCallback((nodeType) => {
    const newNode = { 
      id: `node-${Date.now()}`, 
      type: nodeType.id, 
      name: nodeType.name, 
      x: Math.random() * 400 + 100, 
      y: Math.random() * 300 + 100, 
      config: {} 
    }
    setNodes(prev => [...prev, newNode])
    setSelectedNode(newNode)
  }, [])

  const updateNode = useCallback((nodeId, updates) => {
    setNodes(prev => prev.map(node => node.id === nodeId ? { ...node, ...updates } : node))
  }, [])

  const deleteNode = useCallback((nodeId) => {
    setNodes(prev => prev.filter(node => node.id !== nodeId))
    setConnections(prev => prev.filter(conn => conn.from !== nodeId && conn.to !== nodeId))
    if (selectedNode?.id === nodeId) setSelectedNode(null)
  }, [selectedNode])

  const connectNodes = useCallback((fromNodeId, toNodeId) => {
    const newConnection = { 
      id: `conn-${Date.now()}`, 
      from: fromNodeId, 
      to: toNodeId, 
      fromPort: 'output', 
      toPort: 'input' 
    }
    setConnections(prev => [...prev, newConnection])
  }, [])

  const saveWorkflow = async () => {
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
      } else {
        const newWorkflow = await apiMethods.createWorkflow(workflowData)
        navigate(`/editor/${newWorkflow.id}`, { replace: true })
        toast.success('Workflow created successfully!')
      }
      setLastSaved(new Date())
    } catch (error) {
      console.error('Error saving workflow:', error)
      toast.error('Failed to save workflow')
    } finally {
      setSaving(false)
    }
  }

  const executeWorkflow = async () => {
    if (!workflowId) { 
      toast.error('Please save the workflow before executing') 
      return 
    }
    try {
      const idempotencyKey = `execute-${workflowId}-${Date.now()}`
      const result = await apiMethods.executeWorkflow(workflowId, idempotencyKey)
      toast.success(`Workflow execution started! ID: ${result.execution_id}`)
    } catch (error) {
      console.error('Error executing workflow:', error)
      toast.error('Failed to execute workflow')
    }
  }

  const generateWithAi = async () => {
    if (!aiPrompt.trim()) return
    setAiLoading(true)
    try {
      const response = await apiMethods.generateWorkflow(aiPrompt, true, aiSessionId)
      
      if (response.type === 'workflow' && response.data) {
        const aiWorkflow = response.data
        setNodes(aiWorkflow.nodes || [])
        setConnections(aiWorkflow.connections || [])
        setWorkflow(prev => ({ 
          ...prev, 
          name: aiWorkflow.name || prev.name, 
          description: aiWorkflow.description || prev.description 
        }))
        toast.success('Workflow generated successfully!')
      } else if (response.type === 'suggestion') {
        toast.info('AI provided workflow suggestions')
        console.log('AI Response:', response.data)
      }
    } catch (error) {
      console.error('Error generating workflow:', error)
      toast.error('Failed to generate workflow with AI')
    } finally {
      setAiLoading(false)
      setAiPrompt('')
      setShowAiAssistant(false)
    }
  }

  if (loading) {
    return (
      <div>
        <Navbar />
        <div className="flex items-center justify-center h-96">
          <LoadingSpinner size="large" />
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <button onClick={() => navigate('/dashboard')} className="p-2 hover:bg-gray-100 rounded-lg">
              <ArrowLeftIcon className="w-5 h-5" />
            </button>
            <div>
              <h1 className="text-xl font-semibold text-gray-900">{workflow?.name || 'Untitled Workflow'}</h1>
              <div className="flex items-center space-x-4 text-sm text-gray-600">
                <span>{workflow?.description || 'No description'}</span>
                {lastSaved && (
                  <span className="flex items-center">
                    <ClockIcon className="w-4 h-4 mr-1" />
                    Saved {lastSaved.toLocaleTimeString()}
                  </span>
                )}
              </div>
            </div>
          </div>

          <div className="flex items-center space-x-3">
            <button onClick={() => setShowAiAssistant(true)} className="btn-secondary inline-flex items-center">
              <SparklesIcon className="w-4 h-4 mr-2" /> AI Assistant
            </button>
            <button onClick={executeWorkflow} disabled={!workflowId} className="btn-accent inline-flex items-center disabled:opacity-50 disabled:cursor-not-allowed">
              <PlayIcon className="w-4 h-4 mr-2" /> Execute
            </button>
            <button onClick={saveWorkflow} disabled={saving} className="btn-primary inline-flex items-center">
              {saving ? (<LoadingSpinner size="small" className="mr-2" />) : (<BookmarkIcon className="w-4 h-4 mr-2" />)}
              {saving ? 'Saving...' : 'Save'}
            </button>
          </div>
        </div>
      </div>

      <div className="flex h-screen">
        {showNodePalette && (
          <div className="w-80 bg-white border-r border-gray-200 overflow-y-auto">
            <div className="p-4 border-b border-gray-200">
              <h2 className="font-semibold text-gray-900">Node Library</h2>
              <p className="text-sm text-gray-600">Click nodes to add to canvas</p>
            </div>
            <div className="p-4 space-y-6">
              {Object.entries(nodeTypes.categories || {}).map(([category, categoryNodes]) => (
                <div key={category}>
                  <h3 className="font-medium text-gray-900 mb-3 capitalize">{category.replace('_', ' ')}</h3>
                  <div className="node-palette">
                    {categoryNodes.map((nodeType) => (
                      <div key={nodeType.id} className="node-item" onClick={() => addNode(nodeType)}>
                        <div className="w-8 h-8 bg-gradient-to-r from-primary-500 to-accent-500 rounded-lg flex items-center justify-center">
                          <span className="text-white text-xs font-bold">{nodeType.name.charAt(0)}</span>
                        </div>
                        <div>
                          <div className="font-medium text-gray-900">{nodeType.name}</div>
                          <div className="text-xs text-gray-600">{nodeType.description}</div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="flex-1 relative">
          <div ref={canvasRef} className="w-full h-full bg-gray-50 relative overflow-auto" style={{ backgroundImage: `radial-gradient(circle, #e5e7eb 1px, transparent 1px)`, backgroundSize: '20px 20px' }}>
            {nodes.map((node) => (
              <div key={node.id} className={`absolute workflow-node p-4 ${selectedNode?.id === node.id ? 'selected' : ''}`} style={{ left: node.x, top: node.y, width: '200px' }} onClick={() => setSelectedNode(node)}>
                <div className="flex items-center justify-between mb-2">
                  <span className="font-medium text-gray-900">{node.name}</span>
                  <button onClick={(e) => { e.stopPropagation(); deleteNode(node.id) }} className="text-red-500 hover:text-red-700">
                    <TrashIcon className="w-4 h-4" />
                  </button>
                </div>
                <div className="text-sm text-gray-600">Type: {node.type}</div>
                <div className="absolute -left-2 top-1/2 transform -translate-y-1/2 w-4 h-4 bg-primary-500 rounded-full border-2 border-white"></div>
                <div className="absolute -right-2 top-1/2 transform -translate-y-1/2 w-4 h-4 bg-primary-500 rounded-full border-2 border-white"></div>
              </div>
            ))}

            <svg className="absolute inset-0 pointer-events-none" style={{ zIndex: 1 }}>
              {connections.map((connection) => {
                const fromNode = nodes.find(n => n.id === connection.from)
                const toNode = nodes.find(n => n.id === connection.to)
                if (!fromNode || !toNode) return null
                return (
                  <line key={connection.id} x1={fromNode.x + 200} y1={fromNode.y + 40} x2={toNode.x} y2={toNode.y + 40} className="workflow-connection" strokeWidth="2" markerEnd="url(#arrowhead)" />
                )
              })}
              <defs>
                <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
                  <polygon points="0 0, 10 3.5, 0 7" fill="#9CA3AF" />
                </marker>
              </defs>
            </svg>

            {nodes.length === 0 && (
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="text-center">
                  <CogIcon className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">Start Building Your Workflow</h3>
                  <p className="text-gray-600 mb-4">Add nodes from the palette to create your automation</p>
                  <button onClick={() => setShowAiAssistant(true)} className="btn-primary inline-flex items-center">
                    <SparklesIcon className="w-4 h-4 mr-2" /> Generate with AI
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>

        {selectedNode && (
          <div className="w-80 bg-white border-l border-gray-200 overflow-y-auto">
            <div className="p-4 border-b border-gray-200">
              <h2 className="font-semibold text-gray-900">Node Properties</h2>
            </div>
            <div className="p-4 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Node Name</label>
                <input type="text" value={selectedNode.name} onChange={(e) => updateNode(selectedNode.id, { name: e.target.value })} className="input-field" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Node Type</label>
                <div className="px-3 py-2 bg-gray-50 rounded-lg text-sm text-gray-600">{selectedNode.type}</div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Configuration</label>
                <textarea value={JSON.stringify(selectedNode.config, null, 2)} onChange={(e) => { try { const config = JSON.parse(e.target.value); updateNode(selectedNode.id, { config }) } catch (_) {} }} className="input-field h-32 font-mono text-sm" placeholder="{}" />
              </div>
            </div>
          </div>
        )}
      </div>

      {showAiAssistant && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl shadow-2xl w-full max-w-md mx-4">
            <div className="p-6 border-b border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900 flex items-center">
                <SparklesIcon className="w-5 h-5 mr-2 text-accent-500" /> AI Workflow Generator
              </h3>
            </div>
            <div className="p-6">
              <label className="block text-sm font-medium text-gray-700 mb-3">Describe the workflow you want to create:</label>
              <textarea value={aiPrompt} onChange={(e) => setAiPrompt(e.target.value)} className="input-field h-24 mb-4" placeholder="e.g., Send an email when a new file is uploaded to Dropbox..." />
              <div className="flex justify-end space-x-3">
                <button onClick={() => setShowAiAssistant(false)} className="btn-secondary">Cancel</button>
                <button onClick={generateWithAi} disabled={aiLoading || !aiPrompt.trim()} className="btn-primary inline-flex items-center">
                  {aiLoading ? (<LoadingSpinner size="small" className="mr-2" />) : (<SparklesIcon className="w-4 h-4 mr-2" />)}
                  {aiLoading ? 'Generating...' : 'Generate'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default WorkflowEditor