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
  ClockIcon,
  UsersIcon,
  CodeBracketIcon,
  WrenchScrewdriverIcon,
  MagnifyingGlassIcon,
  FunnelIcon,
  ChatBubbleLeftRightIcon
} from '@heroicons/react/24/outline'
import Navbar from '../components/EnhancedNavbar'
import LoadingSpinner from '../components/LoadingSpinner'
import toast from 'react-hot-toast'

const EnhancedWorkflowEditor = () => {
  const { workflowId } = useParams()
  const navigate = useNavigate()
  const [workflow, setWorkflow] = useState(null)
  const [nodes, setNodes] = useState([])
  const [connections, setConnections] = useState([])
  const [selectedNode, setSelectedNode] = useState(null)
  const [nodeTypes, setNodeTypes] = useState({})
  const [enhancedNodeTypes, setEnhancedNodeTypes] = useState({})
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [showNodePalette, setShowNodePalette] = useState(true)
  const [showAiAssistant, setShowAiAssistant] = useState(false)
  const [showCollaboration, setShowCollaboration] = useState(false)
  const [showAiTools, setShowAiTools] = useState(false)
  const [aiPrompt, setAiPrompt] = useState('')
  const [aiLoading, setAiLoading] = useState(false)
  const [aiSessionId] = useState(`session-${Date.now()}`)
  const [lastSaved, setLastSaved] = useState(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('all')
  const [collaborators, setCollaborators] = useState([])
  const canvasRef = useRef(null)
  const autosaveTimeout = useRef(null)

  useEffect(() => { 
    loadInitialData() 
  }, [workflowId])

  // Auto-save functionality
  useEffect(() => {
    if (workflow && nodes.length > 0) {
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

  const loadInitialData = async () => {
    try {
      // Load both standard and enhanced node types
      const [nodeTypesRes, enhancedRes] = await Promise.all([
        apiMethods.getNodeTypes(),
        loadEnhancedNodeTypes()
      ])
      
      setNodeTypes(nodeTypesRes)
      setEnhancedNodeTypes(enhancedRes)

      if (workflowId) {
        const workflowData = await apiMethods.getWorkflow(workflowId)
        setWorkflow(workflowData)
        setNodes(workflowData.nodes || [])
        setConnections(workflowData.connections || [])
        
        // Join collaboration session
        joinCollaborationSession()
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

  const loadEnhancedNodeTypes = async () => {
    try {
      // Mock enhanced node types for now
      return {
        categories: {
          ai: [
            { id: 'ai-code-generator', name: 'AI Code Generator', description: 'Generate code with AI' },
            { id: 'ai-image-generator', name: 'AI Image Generator', description: 'Generate images with AI' },
            { id: 'ai-content-moderator', name: 'AI Content Moderator', description: 'Moderate content with AI' },
            { id: 'ai-sentiment-analyzer', name: 'AI Sentiment Analyzer', description: 'Analyze sentiment with AI' },
          ],
          finance: [
            { id: 'tax-calculator', name: 'Tax Calculator', description: 'Calculate taxes' },
            { id: 'invoice-generator', name: 'Invoice Generator', description: 'Generate invoices' },
            { id: 'currency-converter', name: 'Currency Converter', description: 'Convert currencies' },
          ],
          ecommerce: [
            { id: 'inventory-manager', name: 'Inventory Manager', description: 'Manage inventory' },
            { id: 'order-processor', name: 'Order Processor', description: 'Process orders' },
            { id: 'price-tracker', name: 'Price Tracker', description: 'Track prices' },
          ],
          healthcare: [
            { id: 'appointment-scheduler', name: 'Appointment Scheduler', description: 'Schedule appointments' },
            { id: 'patient-reminder', name: 'Patient Reminder', description: 'Send patient reminders' },
            { id: 'health-monitor', name: 'Health Monitor', description: 'Monitor health data' },
          ]
        }
      }
    } catch (error) {
      console.error('Error loading enhanced node types:', error)
      return { categories: {} }
    }
  }

  const joinCollaborationSession = async () => {
    try {
      // Mock collaboration for now
      setCollaborators([
        { id: 'user2', name: 'John Doe', color: '#10b981', cursor: { x: 200, y: 150 } },
        { id: 'user3', name: 'Jane Smith', color: '#f59e0b', cursor: { x: 400, y: 300 } }
      ])
    } catch (error) {
      console.error('Failed to join collaboration session:', error)
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

  // Filter nodes based on search and category
  const getFilteredNodes = () => {
    let allNodes = []
    
    // Combine standard and enhanced node types
    const combinedCategories = {
      ...nodeTypes.categories,
      ...enhancedNodeTypes.categories
    }
    
    Object.entries(combinedCategories || {}).forEach(([category, categoryNodes]) => {
      if (selectedCategory === 'all' || selectedCategory === category) {
        categoryNodes.forEach(node => {
          if (!searchTerm || 
              node.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
              node.description.toLowerCase().includes(searchTerm.toLowerCase())) {
            allNodes.push({ ...node, category })
          }
        })
      }
    })
    
    return allNodes
  }

  const getAllCategories = () => {
    const combined = {
      ...nodeTypes.categories,
      ...enhancedNodeTypes.categories
    }
    return Object.keys(combined || {})
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
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <Navbar />
      {/* Enhanced Header */}
      <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <button onClick={() => navigate('/dashboard')} className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg">
              <ArrowLeftIcon className="w-5 h-5" />
            </button>
            <div>
              <h1 className="text-xl font-semibold text-gray-900 dark:text-white">{workflow?.name || 'Untitled Workflow'}</h1>
              <div className="flex items-center space-x-4 text-sm text-gray-600 dark:text-gray-400">
                <span>{workflow?.description || 'No description'}</span>
                {lastSaved && (
                  <span className="flex items-center">
                    <ClockIcon className="w-4 h-4 mr-1" />
                    Saved {lastSaved.toLocaleTimeString()}
                  </span>
                )}
                {collaborators.length > 0 && (
                  <span className="flex items-center">
                    <UsersIcon className="w-4 h-4 mr-1" />
                    {collaborators.length} collaborators
                  </span>
                )}
              </div>
            </div>
          </div>

          <div className="flex items-center space-x-3">
            <button 
              onClick={() => setShowCollaboration(!showCollaboration)} 
              className={`btn-secondary inline-flex items-center ${showCollaboration ? 'bg-primary-100 text-primary-700' : ''}`}
            >
              <UsersIcon className="w-4 h-4 mr-2" /> 
              Collaborate ({collaborators.length})
            </button>
            <button 
              onClick={() => setShowAiTools(!showAiTools)} 
              className={`btn-secondary inline-flex items-center ${showAiTools ? 'bg-purple-100 text-purple-700' : ''}`}
            >
              <CodeBracketIcon className="w-4 h-4 mr-2" /> 
              AI Tools
            </button>
            <button onClick={() => setShowAiAssistant(true)} className="btn-secondary inline-flex items-center">
              <SparklesIcon className="w-4 h-4 mr-2" /> AI Generator
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
        {/* Enhanced Node Palette */}
        {showNodePalette && (
          <div className="w-80 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 overflow-y-auto">
            <div className="p-4 border-b border-gray-200 dark:border-gray-700">
              <div className="flex items-center justify-between mb-4">
                <h2 className="font-semibold text-gray-900 dark:text-white">Enhanced Node Library</h2>
                <span className="text-xs bg-primary-100 text-primary-800 dark:bg-primary-900 dark:text-primary-200 px-2 py-1 rounded-full">
                  120+ Nodes
                </span>
              </div>
              
              {/* Search */}
              <div className="relative mb-4">
                <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search nodes..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                />
              </div>
              
              {/* Category Filter */}
              <div className="mb-4">
                <select
                  value={selectedCategory}
                  onChange={(e) => setSelectedCategory(e.target.value)}
                  className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                >
                  <option value="all">All Categories</option>
                  {getAllCategories().map(category => (
                    <option key={category} value={category} className="capitalize">
                      {category.replace('_', ' ')}
                    </option>
                  ))}
                </select>
              </div>
            </div>
            
            <div className="p-4">
              <div className="node-palette space-y-2">
                {getFilteredNodes().map((nodeType) => (
                  <div 
                    key={`${nodeType.category}-${nodeType.id}`} 
                    className="node-item p-3 rounded-lg border border-gray-200 dark:border-gray-600 hover:border-primary-300 dark:hover:border-primary-600 cursor-pointer transition-all" 
                    onClick={() => addNode(nodeType)}
                  >
                    <div className="flex items-start space-x-3">
                      <div className={`w-8 h-8 rounded-lg flex items-center justify-center text-white text-xs font-bold ${
                        nodeType.category === 'ai' ? 'bg-gradient-to-r from-purple-500 to-pink-500' :
                        nodeType.category === 'finance' ? 'bg-gradient-to-r from-green-500 to-emerald-500' :
                        nodeType.category === 'ecommerce' ? 'bg-gradient-to-r from-blue-500 to-cyan-500' :
                        nodeType.category === 'healthcare' ? 'bg-gradient-to-r from-red-500 to-pink-500' :
                        'bg-gradient-to-r from-primary-500 to-accent-500'
                      }`}>
                        {nodeType.name.charAt(0)}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="font-medium text-gray-900 dark:text-white text-sm">{nodeType.name}</div>
                        <div className="text-xs text-gray-600 dark:text-gray-400 mt-1">{nodeType.description}</div>
                        <div className="text-xs text-primary-600 dark:text-primary-400 mt-1 capitalize">{nodeType.category}</div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Enhanced Canvas */}
        <div className="flex-1 relative">
          <div ref={canvasRef} className="w-full h-full bg-gray-50 dark:bg-gray-900 relative overflow-auto" style={{ backgroundImage: `radial-gradient(circle, #e5e7eb 1px, transparent 1px)`, backgroundSize: '20px 20px' }}>
            {/* Collaborator Cursors */}
            {collaborators.map((collaborator) => (
              <div
                key={collaborator.id}
                className="absolute pointer-events-none z-10"
                style={{ left: collaborator.cursor.x, top: collaborator.cursor.y }}
              >
                <div className="flex items-center space-x-2">
                  <div 
                    className="w-4 h-4 rounded-full border-2 border-white shadow-lg"
                    style={{ backgroundColor: collaborator.color }}
                  ></div>
                  <div 
                    className="px-2 py-1 rounded text-white text-xs font-medium shadow-lg"
                    style={{ backgroundColor: collaborator.color }}
                  >
                    {collaborator.name}
                  </div>
                </div>
              </div>
            ))}

            {/* Workflow Nodes */}
            {nodes.map((node) => (
              <div 
                key={node.id} 
                className={`absolute workflow-node p-4 ${selectedNode?.id === node.id ? 'selected ring-2 ring-primary-500' : ''} ${
                  node.type?.includes('ai') ? 'border-purple-200 bg-purple-50 dark:border-purple-700 dark:bg-purple-900/20' :
                  node.type?.includes('finance') ? 'border-green-200 bg-green-50 dark:border-green-700 dark:bg-green-900/20' :
                  node.type?.includes('ecommerce') ? 'border-blue-200 bg-blue-50 dark:border-blue-700 dark:bg-blue-900/20' :
                  'border-gray-200 bg-white dark:border-gray-600 dark:bg-gray-800'
                }`} 
                style={{ left: node.x, top: node.y, width: '200px' }} 
                onClick={() => setSelectedNode(node)}
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="font-medium text-gray-900 dark:text-white text-sm">{node.name}</span>
                  <button onClick={(e) => { e.stopPropagation(); deleteNode(node.id) }} className="text-red-500 hover:text-red-700 p-1">
                    <TrashIcon className="w-3 h-3" />
                  </button>
                </div>
                <div className="text-xs text-gray-600 dark:text-gray-400 mb-2">Type: {node.type}</div>
                {node.type?.includes('ai') && (
                  <div className="text-xs bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200 px-2 py-1 rounded">
                    AI Enhanced
                  </div>
                )}
                
                {/* Connection Points */}
                <div className="absolute -left-2 top-1/2 transform -translate-y-1/2 w-4 h-4 bg-primary-500 rounded-full border-2 border-white shadow-sm"></div>
                <div className="absolute -right-2 top-1/2 transform -translate-y-1/2 w-4 h-4 bg-primary-500 rounded-full border-2 border-white shadow-sm"></div>
              </div>
            ))}

            {/* Connection Lines */}
            <svg className="absolute inset-0 pointer-events-none" style={{ zIndex: 1 }}>
              {connections.map((connection) => {
                const fromNode = nodes.find(n => n.id === connection.from)
                const toNode = nodes.find(n => n.id === connection.to)
                if (!fromNode || !toNode) return null
                return (
                  <line 
                    key={connection.id} 
                    x1={fromNode.x + 200} 
                    y1={fromNode.y + 40} 
                    x2={toNode.x} 
                    y2={toNode.y + 40} 
                    className="workflow-connection" 
                    strokeWidth="2" 
                    stroke="#9CA3AF"
                    markerEnd="url(#arrowhead)" 
                  />
                )
              })}
              <defs>
                <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
                  <polygon points="0 0, 10 3.5, 0 7" fill="#9CA3AF" />
                </marker>
              </defs>
            </svg>

            {/* Empty State */}
            {nodes.length === 0 && (
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="text-center">
                  <CogIcon className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">Start Building Your Enhanced Workflow</h3>
                  <p className="text-gray-600 dark:text-gray-400 mb-4">Add nodes from the enhanced library with 120+ options</p>
                  <div className="flex justify-center space-x-3">
                    <button onClick={() => setShowAiAssistant(true)} className="btn-primary inline-flex items-center">
                      <SparklesIcon className="w-4 h-4 mr-2" /> Generate with AI
                    </button>
                    <button onClick={() => setShowAiTools(true)} className="btn-secondary inline-flex items-center">
                      <CodeBracketIcon className="w-4 h-4 mr-2" /> AI Tools
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Enhanced Properties Panel */}
        {selectedNode && (
          <div className="w-80 bg-white dark:bg-gray-800 border-l border-gray-200 dark:border-gray-700 overflow-y-auto">
            <div className="p-4 border-b border-gray-200 dark:border-gray-700">
              <h2 className="font-semibold text-gray-900 dark:text-white">Enhanced Node Properties</h2>
              {selectedNode.type?.includes('ai') && (
                <div className="mt-2 text-xs bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200 px-2 py-1 rounded">
                  AI-Powered Node
                </div>
              )}
            </div>
            <div className="p-4 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Node Name</label>
                <input 
                  type="text" 
                  value={selectedNode.name} 
                  onChange={(e) => updateNode(selectedNode.id, { name: e.target.value })} 
                  className="input-field" 
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Node Type</label>
                <div className="px-3 py-2 bg-gray-50 dark:bg-gray-700 rounded-lg text-sm text-gray-600 dark:text-gray-300">
                  {selectedNode.type}
                </div>
              </div>

              {selectedNode.type?.includes('ai') && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">AI Configuration</label>
                  <div className="space-y-2">
                    <div>
                      <label className="text-xs text-gray-600 dark:text-gray-400">Model</label>
                      <select className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white">
                        <option>gpt-4-turbo</option>
                        <option>claude-3-sonnet</option>
                        <option>llama-3.3-70b</option>
                      </select>
                    </div>
                    <div>
                      <label className="text-xs text-gray-600 dark:text-gray-400">Temperature</label>
                      <input type="range" min="0" max="1" step="0.1" defaultValue="0.7" className="w-full" />
                    </div>
                  </div>
                </div>
              )}

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Configuration</label>
                <textarea 
                  value={JSON.stringify(selectedNode.config, null, 2)} 
                  onChange={(e) => { 
                    try { 
                      const config = JSON.parse(e.target.value)
                      updateNode(selectedNode.id, { config })
                    } catch (_) {} 
                  }} 
                  className="input-field h-32 font-mono text-sm" 
                  placeholder="{}" 
                />
              </div>
            </div>
          </div>
        )}
      </div>

      {/* AI Assistant Modal */}
      {showAiAssistant && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-2xl w-full max-w-md mx-4">
            <div className="p-6 border-b border-gray-200 dark:border-gray-700">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center">
                <SparklesIcon className="w-5 h-5 mr-2 text-accent-500" /> Enhanced AI Workflow Generator
              </h3>
            </div>
            <div className="p-6">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                Describe the workflow you want to create:
              </label>
              <textarea 
                value={aiPrompt} 
                onChange={(e) => setAiPrompt(e.target.value)} 
                className="input-field h-24 mb-4" 
                placeholder="e.g., Create a financial automation workflow that processes invoices, calculates taxes, and generates reports using AI..." 
              />
              <div className="flex justify-end space-x-3">
                <button onClick={() => setShowAiAssistant(false)} className="btn-secondary">Cancel</button>
                <button 
                  onClick={generateWithAi} 
                  disabled={aiLoading || !aiPrompt.trim()} 
                  className="btn-primary inline-flex items-center"
                >
                  {aiLoading ? (<LoadingSpinner size="small" className="mr-2" />) : (<SparklesIcon className="w-4 h-4 mr-2" />)}
                  {aiLoading ? 'Generating...' : 'Generate'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* AI Tools Panel */}
      {showAiTools && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-2xl w-full max-w-2xl mx-4">
            <div className="p-6 border-b border-gray-200 dark:border-gray-700">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center">
                  <CodeBracketIcon className="w-5 h-5 mr-2 text-purple-500" /> AI-Powered Tools
                </h3>
                <button onClick={() => setShowAiTools(false)} className="text-gray-400 hover:text-gray-600">
                  ✕
                </button>
              </div>
            </div>
            <div className="p-6 grid grid-cols-1 md:grid-cols-2 gap-4">
              {[
                { title: 'Code Generator', icon: '💻', description: 'Generate code for custom nodes' },
                { title: 'Sentiment Analysis', icon: '😊', description: 'Analyze text sentiment' },
                { title: 'Entity Extraction', icon: '🏷️', description: 'Extract entities from text' },
                { title: 'Content Summary', icon: '📝', description: 'Summarize long content' },
                { title: 'Language Detection', icon: '🌍', description: 'Detect text language' },
                { title: 'Workflow Optimizer', icon: '⚡', description: 'Optimize workflow performance' }
              ].map((tool, index) => (
                <div key={index} className="p-4 border border-gray-200 dark:border-gray-600 rounded-lg hover:border-primary-300 dark:hover:border-primary-600 cursor-pointer transition-all">
                  <div className="text-2xl mb-2">{tool.icon}</div>
                  <h4 className="font-medium text-gray-900 dark:text-white mb-1">{tool.title}</h4>
                  <p className="text-sm text-gray-600 dark:text-gray-400">{tool.description}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default EnhancedWorkflowEditor