import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { apiMethods } from '../utils/api'
import { enhancedApiMethods } from '../utils/enhancedApi'
import { 
  PlusIcon, 
  PlayIcon,
  ChartBarIcon,
  ClockIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  EyeIcon,
  PencilIcon,
  TrashIcon,
  CogIcon,
  SparklesIcon
} from '@heroicons/react/24/outline'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts'
import Navbar from '../components/Navbar'
import LoadingSpinner from '../components/LoadingSpinner'
import EnhancementSettings from '../components/EnhancementSettings'
import OptionalEnhancements from '../components/OptionalEnhancements'
import toast from 'react-hot-toast'

const Dashboard = () => {
  const { user } = useAuth()
  const [stats, setStats] = useState(null)
  const [workflows, setWorkflows] = useState([])
  const [checklist, setChecklist] = useState(null)
  const [loading, setLoading] = useState(true)
  const [showEnhancementSettings, setShowEnhancementSettings] = useState(false)
  const [aiInsights, setAiInsights] = useState(null)
  const [systemStatus, setSystemStatus] = useState(null)

  useEffect(() => {
    loadDashboardData()
  }, [])

  const loadDashboardData = async () => {
    try {
      const [statsResponse, workflowsResponse, checklistResponse] = await Promise.all([
        apiMethods.getDashboardStats(),
        apiMethods.getWorkflows(1, 10), // Load first 10 workflows
        apiMethods.getUserChecklist()
      ])
      setStats(statsResponse)
      setWorkflows(workflowsResponse.workflows || workflowsResponse)
      setChecklist(checklistResponse)
      
      // Load enhanced features silently in background
      loadEnhancedFeatures()
    } catch (error) {
      console.error('Error loading dashboard data:', error)
      toast.error('Failed to load dashboard data')
    } finally {
      setLoading(false)
    }
  }

  const loadEnhancedFeatures = async () => {
    try {
      // Load GROQ AI insights and system status in background
      const [aiResponse, statusResponse] = await Promise.all([
        enhancedApiMethods.getEnhancedDashboardInsights().catch(() => null),
        enhancedApiMethods.getEnhancedSystemStatus().catch(() => null)
      ])
      
      if (aiResponse && !aiResponse.error) {
        setAiInsights(aiResponse)
      }
      
      if (statusResponse && !statusResponse.error) {
        setSystemStatus(statusResponse)
      }
    } catch (error) {
      // Silently handle enhanced features errors to avoid disrupting main UI
      console.log('Enhanced features loading silently in background')
    }
  }

  const executeWorkflow = async (workflowId) => {
    try {
      const idempotencyKey = `execute-${workflowId}-${Date.now()}`
      await apiMethods.executeWorkflow(workflowId, idempotencyKey)
      toast.success('Workflow execution started!')
      loadDashboardData()
    } catch (error) {
      console.error('Error executing workflow:', error)
      toast.error('Failed to execute workflow')
    }
  }

  const deleteWorkflow = async (workflowId) => {
    if (!window.confirm('Are you sure you want to delete this workflow?')) return
    try {
      await apiMethods.deleteWorkflow(workflowId)
      toast.success('Workflow deleted successfully')
      loadDashboardData()
    } catch (error) {
      console.error('Error deleting workflow:', error)
      toast.error('Failed to delete workflow')
    }
  }

  const executionData = [
    { name: 'Mon', executions: 12, success: 10 },
    { name: 'Tue', executions: 19, success: 18 },
    { name: 'Wed', executions: 15, success: 14 },
    { name: 'Thu', executions: 22, success: 20 },
    { name: 'Fri', executions: 18, success: 17 },
    { name: 'Sat', executions: 8, success: 8 },
    { name: 'Sun', executions: 5, success: 5 },
  ]

  const performanceData = [
    { name: 'API Calls', value: 45 },
    { name: 'Data Processing', value: 28 },
    { name: 'Email Sending', value: 32 },
    { name: 'File Operations', value: 18 },
  ]

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
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                Welcome back, {user?.name}!
              </h1>
              <p className="text-gray-600 mt-2">
                Here's what's happening with your automations today.
              </p>
            </div>
            
            {/* Enhancement Settings Button - Very subtle, hidden by default */}
            <div className="flex items-center space-x-3">
              <button
                onClick={() => setShowEnhancementSettings(true)}
                className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors group"
                title="Enhancement Settings"
              >
                <SparklesIcon className="w-5 h-5 opacity-50 group-hover:opacity-100" />
              </button>
            </div>
          </div>
        </div>

        {/* Wrap everything in OptionalEnhancements for zero UI disruption */}
        <OptionalEnhancements 
          userId={user?.id} 
          dashboardStats={stats}
          className="space-y-8"
        >
            {/* Enhanced AI Insights - Only shown when available */}
            {aiInsights && aiInsights.ai_provider && (
              <div className="bg-gradient-to-r from-blue-50 to-purple-50 border border-blue-200 rounded-lg p-4 mb-6">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="text-sm font-medium text-gray-700">
                    🤖 AI Insights
                    <span className="ml-2 text-xs text-blue-600 bg-blue-100 px-2 py-1 rounded">
                      Powered by {aiInsights.ai_provider === 'groq_llama_3.1_8b' ? 'GROQ Llama 3.1 8B' : 'AI'}
                    </span>
                  </h3>
                  {aiInsights.cost_optimized && (
                    <span className="text-xs text-green-600">Cost Optimized</span>
                  )}
                </div>
                <div className="grid grid-cols-3 gap-4 text-xs">
                  <div className="text-center">
                    <div className="font-medium text-blue-600">
                      {aiInsights.insights?.metrics?.ai_confidence_score || 'High'}
                    </div>
                    <div className="text-gray-500">AI Confidence</div>
                  </div>
                  <div className="text-center">
                    <div className="font-medium text-purple-600">
                      {aiInsights.insights?.metrics?.optimization_potential || 'Medium'}
                    </div>
                    <div className="text-gray-500">Optimization</div>
                  </div>
                  <div className="text-center">
                    <div className="font-medium text-green-600">
                      {aiInsights.insights?.metrics?.predicted_time_savings || '2'} hrs
                    </div>
                    <div className="text-gray-500">Time Savings</div>
                  </div>
                </div>
              </div>
            )}

            {/* System Status - Only shown when enhanced system is active */}
            {systemStatus && systemStatus.system_status === 'fully_operational' && (
              <div className="mb-4">
                <div className="flex items-center text-xs text-green-600 bg-green-50 px-3 py-1 rounded-full inline-flex">
                  <div className="w-2 h-2 bg-green-500 rounded-full mr-2 animate-pulse"></div>
                  Enhanced System Active: GROQ AI + Performance Optimization
                </div>
              </div>
            )}
          {checklist && checklist.completion_percentage < 100 && (
            <div className="bg-gradient-to-r from-primary-50 to-accent-50 border border-primary-200 rounded-lg p-6 mb-8">
              <div className="flex items-start justify-between">
                <div>
                  <h2 className="text-lg font-semibold text-gray-900 mb-2">Get Started Checklist</h2>
                  <p className="text-gray-600 mb-4">Complete these steps to unlock the full potential of Aether Automation</p>
                  <div className="space-y-2">
                    <div className={`flex items-center ${checklist.has_any_workflow ? 'text-green-600' : 'text-gray-600'}`}>
                      <CheckCircleIcon className={`w-5 h-5 mr-2 ${checklist.has_any_workflow ? 'text-green-500' : 'text-gray-400'}`} />
                      Create your first workflow
                    </div>
                    <div className={`flex items-center ${checklist.has_any_integration ? 'text-green-600' : 'text-gray-600'}`}>
                      <CheckCircleIcon className={`w-5 h-5 mr-2 ${checklist.has_any_integration ? 'text-green-500' : 'text-gray-400'}`} />
                      Add an integration
                    </div>
                    <div className={`flex items-center ${checklist.has_any_execution ? 'text-green-600' : 'text-gray-600'}`}>
                      <CheckCircleIcon className={`w-5 h-5 mr-2 ${checklist.has_any_execution ? 'text-green-500' : 'text-gray-400'}`} />
                      Run your first automation
                    </div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-2xl font-bold text-primary-600">{Math.round(checklist.completion_percentage)}%</div>
                  <div className="text-sm text-gray-600">Complete</div>
                </div>
              </div>
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div className="metric-card card p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Total Workflows</p>
                  <p className="text-3xl font-bold text-gray-900">{stats?.total_workflows || 0}</p>
                </div>
                <ChartBarIcon className="w-8 h-8 text-primary-500" />
              </div>
            </div>

            <div className="metric-card card p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Total Executions</p>
                  <p className="text-3xl font-bold text-gray-900">{stats?.total_executions || 0}</p>
                </div>
                <PlayIcon className="w-8 h-8 text-accent-500" />
              </div>
            </div>

            <div className="metric-card card p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Success Rate</p>
                  <p className="text-3xl font-bold text-green-600">{stats?.success_rate || 0}%</p>
                </div>
                <CheckCircleIcon className="w-8 h-8 text-green-500" />
              </div>
            </div>

            <div className="metric-card card p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Failed Executions</p>
                  <p className="text-3xl font-bold text-red-600">{stats?.failed_executions || 0}</p>
                </div>
                <ExclamationTriangleIcon className="w-8 h-8 text-red-500" />
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
            <div className="chart-container">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Execution Trends</h3>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={executionData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Line type="monotone" dataKey="executions" stroke="#0ea5e9" strokeWidth={2} />
                  <Line type="monotone" dataKey="success" stroke="#10b981" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </div>

            <div className="chart-container">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Performance Breakdown</h3>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={performanceData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="value" fill="#8b5cf6" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="mb-8">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-gray-900">Quick Actions</h2>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Link to="/editor" className="card p-6 text-center hover:shadow-lg transition-shadow">
                <PlusIcon className="w-8 h-8 mx-auto text-primary-500 mb-3" />
                <h3 className="font-semibold text-gray-900 mb-2">Create New Workflow</h3>
                <p className="text-gray-600 text-sm">Start building your automation from scratch</p>
              </Link>
              <Link to="/integrations" className="card p-6 text-center hover:shadow-lg transition-shadow">
                <div className="w-8 h-8 mx-auto bg-gradient-to-r from-accent-500 to-primary-500 rounded-lg flex items-center justify-center mb-3">
                  <span className="text-white text-sm font-bold">45+</span>
                </div>
                <h3 className="font-semibold text-gray-900 mb-2">Browse Integrations</h3>
                <p className="text-gray-600 text-sm">Connect your favorite tools and services</p>
              </Link>
              <div className="card p-6 text-center hover:shadow-lg transition-shadow cursor-pointer">
                <ClockIcon className="w-8 h-8 mx-auto text-green-500 mb-3" />
                <h3 className="font-semibold text-gray-900 mb-2">View Templates</h3>
                <p className="text-gray-600 text-sm">Get started with pre-built workflows</p>
              </div>
            </div>
          </div>

          <div>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-gray-900">Your Workflows</h2>
              <Link to="/editor" className="btn-primary inline-flex items-center">
                <PlusIcon className="w-4 h-4 mr-2" />
                New Workflow
              </Link>
            </div>

            {workflows.length === 0 ? (
              <div className="card p-8 text-center">
                <ChartBarIcon className="w-12 h-12 mx-auto text-gray-400 mb-4" />
                <h3 className="text-lg font-semibold text-gray-900 mb-2">No workflows yet</h3>
                <p className="text-gray-600 mb-4">Create your first automation workflow to get started.</p>
                <Link to="/editor" className="btn-primary">Create Your First Workflow</Link>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {workflows.map((workflow) => (
                  <div key={workflow.id} className="card p-6">
                    <div className="flex items-start justify-between mb-4">
                      <div>
                        <h3 className="font-semibold text-gray-900 mb-1">{workflow.name}</h3>
                        <p className="text-gray-600 text-sm">{workflow.description}</p>
                      </div>
                      <div className={`px-2 py-1 rounded-full text-xs font-medium ${
                        workflow.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                      }`}>
                        {workflow.status}
                      </div>
                    </div>

                    <div className="flex items-center justify-between text-sm text-gray-600 mb-4">
                      <span>Nodes: {workflow.nodes?.length || 0}</span>
                      <span>Updated: {new Date(workflow.updated_at).toLocaleDateString()}</span>
                    </div>

                    <div className="flex items-center space-x-2">
                      <button onClick={() => executeWorkflow(workflow.id)} className="flex-1 btn-primary text-sm py-2">
                        <PlayIcon className="w-4 h-4 mr-1" />
                        Run
                      </button>
                      <Link to={`/editor/${workflow.id}`} className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg">
                        <PencilIcon className="w-4 h-4" />
                      </Link>
                      <button onClick={() => deleteWorkflow(workflow.id)} className="p-2 text-red-600 hover:text-red-700 hover:bg-red-50 rounded-lg">
                        <TrashIcon className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </OptionalEnhancements>

        {/* Enhancement Settings Modal - Hidden by default */}
        <EnhancementSettings 
          isOpen={showEnhancementSettings}
          onClose={() => setShowEnhancementSettings(false)}
        />
      </div>
    </div>
  )
}

export default Dashboard