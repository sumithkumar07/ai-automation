import React, { useState, useEffect, useMemo, lazy, Suspense } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { useAccessibility } from '../components/AccessibilityProvider'
import { apiMethods } from '../utils/api'
import { PerformanceMonitor, usePerformanceTracker } from '../components/PerformanceMonitor'
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
  SparklesIcon,
  RocketLaunchIcon,
  BoltIcon,
  TrendingUpIcon,
  CalendarIcon,
  FireIcon,
  PuzzlePieceIcon
} from '@heroicons/react/24/outline'
import EnhancedNavbar from '../components/EnhancedNavbar'
import LoadingSpinner from '../components/LoadingSpinner'
import SmartTooltip, { InfoTooltip } from '../components/SmartTooltip'
import EnhancedAIAssistant from '../components/EnhancedAIAssistant'
import toast from 'react-hot-toast'

// Lazy load charts for better performance
const LineChart = lazy(() => import('recharts').then(module => ({ default: module.LineChart })))
const Line = lazy(() => import('recharts').then(module => ({ default: module.Line })))
const XAxis = lazy(() => import('recharts').then(module => ({ default: module.XAxis })))
const YAxis = lazy(() => import('recharts').then(module => ({ default: module.YAxis })))
const CartesianGrid = lazy(() => import('recharts').then(module => ({ default: module.CartesianGrid })))
const Tooltip = lazy(() => import('recharts').then(module => ({ default: module.Tooltip })))
const ResponsiveContainer = lazy(() => import('recharts').then(module => ({ default: module.ResponsiveContainer })))
const BarChart = lazy(() => import('recharts').then(module => ({ default: module.BarChart })))
const Bar = lazy(() => import('recharts').then(module => ({ default: module.Bar })))

// Memoized components for performance
const MetricCard = React.memo(({ title, value, icon: Icon, color, trend, description }) => (
  <PerformanceMonitor name="MetricCard">
    <div className="metric-card card p-6 relative overflow-hidden">
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center space-x-2">
            <p className="text-sm font-medium text-gray-600">{title}</p>
            {description && <InfoTooltip content={description} />}
          </div>
          <p className={`text-3xl font-bold ${color}`}>{value}</p>
          {trend && (
            <div className={`flex items-center text-sm mt-1 ${trend > 0 ? 'text-green-600' : 'text-red-600'}`}>
              <TrendingUpIcon className={`w-4 h-4 mr-1 ${trend < 0 ? 'rotate-180' : ''}`} />
              {Math.abs(trend)}%
            </div>
          )}
        </div>
        <div className={`w-12 h-12 rounded-lg flex items-center justify-center bg-gradient-to-br ${color === 'text-green-600' ? 'from-green-400 to-green-600' : color === 'text-red-600' ? 'from-red-400 to-red-600' : 'from-primary-400 to-primary-600'}`}>
          <Icon className="w-6 h-6 text-white" />
        </div>
      </div>
      {/* Subtle animation */}
      <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white to-transparent opacity-0 hover:opacity-10 transition-opacity duration-300 transform -skew-x-12" />
    </div>
  </PerformanceMonitor>
))

const WorkflowCard = React.memo(({ workflow, onExecute, onDelete }) => {
  const [isExecuting, setIsExecuting] = useState(false)

  const handleExecute = async () => {
    setIsExecuting(true)
    try {
      await onExecute(workflow.id)
    } finally {
      setIsExecuting(false)
    }
  }

  return (
    <PerformanceMonitor name="WorkflowCard">
      <div className="card p-6 group hover:shadow-lg transition-all duration-300">
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1">
            <h3 className="font-semibold text-gray-900 mb-1 group-hover:text-primary-600 transition-colors">
              {workflow.name}
            </h3>
            <p className="text-gray-600 text-sm line-clamp-2">{workflow.description || 'No description'}</p>
          </div>
          <div className={`px-2 py-1 rounded-full text-xs font-medium shrink-0 ml-3 ${
            workflow.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
          }`}>
            {workflow.status}
          </div>
        </div>

        <div className="flex items-center justify-between text-sm text-gray-600 mb-4">
          <span className="flex items-center">
            <ChartBarIcon className="w-4 h-4 mr-1" />
            {workflow.nodes?.length || 0} nodes
          </span>
          <span className="flex items-center">
            <CalendarIcon className="w-4 h-4 mr-1" />
            {new Date(workflow.updated_at).toLocaleDateString()}
          </span>
        </div>

        <div className="flex items-center space-x-2">
          <SmartTooltip content="Execute workflow">
            <button 
              onClick={handleExecute}
              disabled={isExecuting}
              className="flex-1 btn-primary text-sm py-2 inline-flex items-center justify-center disabled:opacity-50"
            >
              {isExecuting ? (
                <LoadingSpinner size="small" className="mr-1" />
              ) : (
                <PlayIcon className="w-4 h-4 mr-1" />
              )}
              {isExecuting ? 'Running...' : 'Run'}
            </button>
          </SmartTooltip>
          
          <SmartTooltip content="Edit workflow">
            <Link 
              to={`/editor/${workflow.id}`} 
              className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
              aria-label={`Edit ${workflow.name}`}
            >
              <PencilIcon className="w-4 h-4" />
            </Link>
          </SmartTooltip>
          
          <SmartTooltip content="Delete workflow">
            <button 
              onClick={() => onDelete(workflow.id)}
              className="p-2 text-red-600 hover:text-red-700 hover:bg-red-50 rounded-lg transition-colors"
              aria-label={`Delete ${workflow.name}`}
            >
              <TrashIcon className="w-4 h-4" />
            </button>
          </SmartTooltip>
        </div>
      </div>
    </PerformanceMonitor>
  )
})

const EnhancedDashboard = () => {
  const { user } = useAuth()
  const { preferences, announceToScreenReader } = useAccessibility()
  const { trackOperation } = usePerformanceTracker('Dashboard')
  const [stats, setStats] = useState(null)
  const [workflows, setWorkflows] = useState([])
  const [checklist, setChecklist] = useState(null)
  const [loading, setLoading] = useState(true)
  const [showAIAssistant, setShowAIAssistant] = useState(false)
  const [aiSessionId] = useState(`dashboard-${Date.now()}`)
  const [insights, setInsights] = useState([])

  useEffect(() => {
    loadDashboardData()
  }, [])

  const loadDashboardData = trackOperation(async () => {
    try {
      const [statsResponse, workflowsResponse, checklistResponse] = await Promise.all([
        apiMethods.getDashboardStats(),
        apiMethods.getWorkflows(1, 12), // Load first 12 workflows
        apiMethods.getUserChecklist()
      ])
      setStats(statsResponse)
      setWorkflows(Array.isArray(workflowsResponse) ? workflowsResponse : workflowsResponse.workflows || [])
      setChecklist(checklistResponse)
      
      // Generate insights
      generateInsights(statsResponse, workflowsResponse)
      
      // Announce to screen readers
      announceToScreenReader(`Dashboard loaded. You have ${statsResponse.total_workflows} workflows with ${statsResponse.success_rate}% success rate.`)
    } catch (error) {
      console.error('Error loading dashboard data:', error)
      toast.error('Failed to load dashboard data')
    } finally {
      setLoading(false)
    }
  })

  const generateInsights = (statsData, workflowsData) => {
    const newInsights = []
    
    if (statsData.success_rate < 90) {
      newInsights.push({
        type: 'warning',
        title: 'Workflow Optimization Needed',
        message: `Your success rate is ${statsData.success_rate}%. Consider reviewing failed workflows.`,
        action: 'View Executions'
      })
    }

    if (statsData.total_workflows === 0) {
      newInsights.push({
        type: 'info',
        title: 'Get Started',
        message: 'Create your first workflow to begin automating your tasks.',
        action: 'Create Workflow'
      })
    }

    if (Array.isArray(workflowsData) ? workflowsData.length : (workflowsData.workflows?.length || 0) > 10) {
      newInsights.push({
        type: 'success',
        title: 'Power User!',
        message: 'You have multiple workflows running. Great job on automating!',
        action: 'View All'
      })
    }

    setInsights(newInsights)
  }

  const executeWorkflow = trackOperation(async (workflowId) => {
    try {
      const idempotencyKey = `execute-${workflowId}-${Date.now()}`
      await apiMethods.executeWorkflow(workflowId, idempotencyKey)
      toast.success('Workflow execution started!')
      announceToScreenReader('Workflow execution started successfully')
      loadDashboardData()
    } catch (error) {
      console.error('Error executing workflow:', error)
      toast.error('Failed to execute workflow')
    }
  })

  const deleteWorkflow = trackOperation(async (workflowId) => {
    if (!window.confirm('Are you sure you want to delete this workflow?')) return
    try {
      await apiMethods.deleteWorkflow(workflowId)
      toast.success('Workflow deleted successfully')
      announceToScreenReader('Workflow deleted successfully')
      loadDashboardData()
    } catch (error) {
      console.error('Error deleting workflow:', error)
      toast.error('Failed to delete workflow')
    }
  })

  const handleAIWorkflowGenerated = (workflowData) => {
    // Could redirect to editor with the generated workflow
    toast.success('AI generated workflow! Redirecting to editor...')
    // navigate(`/editor?ai-workflow=${encodeURIComponent(JSON.stringify(workflowData))}`)
  }

  // Memoized chart data
  const executionData = useMemo(() => [
    { name: 'Mon', executions: 12, success: 10, failed: 2 },
    { name: 'Tue', executions: 19, success: 18, failed: 1 },
    { name: 'Wed', executions: 15, success: 14, failed: 1 },
    { name: 'Thu', executions: 22, success: 20, failed: 2 },
    { name: 'Fri', executions: 18, success: 17, failed: 1 },
    { name: 'Sat', executions: 8, success: 8, failed: 0 },
    { name: 'Sun', executions: 5, success: 5, failed: 0 },
  ], [])

  const performanceData = useMemo(() => [
    { name: 'API Calls', value: 45, color: '#0ea5e9' },
    { name: 'Data Processing', value: 28, color: '#8b5cf6' },
    { name: 'Email Sending', value: 32, color: '#10b981' },
    { name: 'File Operations', value: 18, color: '#f59e0b' },
  ], [])

  if (loading) {
    return (
      <div>
        <EnhancedNavbar />
        <div className="flex items-center justify-center h-96" role="status" aria-label="Loading dashboard">
          <LoadingSpinner size="large" />
        </div>
      </div>
    )
  }

  return (
    <PerformanceMonitor name="EnhancedDashboard">
      <div className="min-h-screen bg-gray-50">
        <EnhancedNavbar />
        
        <main id="main-content" className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Welcome Section */}
          <div className="mb-8">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-3xl font-bold text-gray-900">
                  Welcome back, {user?.name}! 👋
                </h1>
                <p className="text-gray-600 mt-2">
                  Here's what's happening with your automations today.
                </p>
              </div>
              <div className="flex items-center space-x-3">
                <SmartTooltip content="Get AI help with your workflows">
                  <button
                    onClick={() => setShowAIAssistant(true)}
                    className="btn-secondary inline-flex items-center"
                    aria-label="Open AI Assistant"
                  >
                    <SparklesIcon className="w-4 h-4 mr-2" />
                    AI Assistant
                  </button>
                </SmartTooltip>
                <Link to="/editor" className="btn-primary inline-flex items-center">
                  <RocketLaunchIcon className="w-4 h-4 mr-2" />
                  Quick Create
                </Link>
              </div>
            </div>
          </div>

          {/* Insights Cards */}
          {insights.length > 0 && (
            <div className="mb-8">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Smart Insights</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {insights.map((insight, index) => (
                  <div
                    key={index}
                    className={`p-4 rounded-lg border-l-4 ${
                      insight.type === 'warning' ? 'bg-yellow-50 border-yellow-400' :
                      insight.type === 'error' ? 'bg-red-50 border-red-400' :
                      insight.type === 'success' ? 'bg-green-50 border-green-400' :
                      'bg-blue-50 border-blue-400'
                    }`}
                  >
                    <h3 className={`font-medium ${
                      insight.type === 'warning' ? 'text-yellow-800' :
                      insight.type === 'error' ? 'text-red-800' :
                      insight.type === 'success' ? 'text-green-800' :
                      'text-blue-800'
                    }`}>
                      {insight.title}
                    </h3>
                    <p className={`text-sm mt-1 ${
                      insight.type === 'warning' ? 'text-yellow-700' :
                      insight.type === 'error' ? 'text-red-700' :
                      insight.type === 'success' ? 'text-green-700' :
                      'text-blue-700'
                    }`}>
                      {insight.message}
                    </p>
                    {insight.action && (
                      <button className={`text-sm font-medium mt-2 ${
                        insight.type === 'warning' ? 'text-yellow-800 hover:text-yellow-900' :
                        insight.type === 'error' ? 'text-red-800 hover:text-red-900' :
                        insight.type === 'success' ? 'text-green-800 hover:text-green-900' :
                        'text-blue-800 hover:text-blue-900'
                      }`}>
                        {insight.action} →
                      </button>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Onboarding Checklist */}
          {checklist && checklist.completion_percentage < 100 && (
            <div className="bg-gradient-to-r from-primary-50 to-accent-50 border border-primary-200 rounded-lg p-6 mb-8">
              <div className="flex items-start justify-between">
                <div>
                  <h2 className="text-lg font-semibold text-gray-900 mb-2 flex items-center">
                    <FireIcon className="w-5 h-5 mr-2 text-primary-600" />
                    Get Started Checklist
                  </h2>
                  <p className="text-gray-600 mb-4">Complete these steps to unlock the full potential of Aether Automation</p>
                  <div className="space-y-2">
                    <div className={`flex items-center ${checklist.has_any_workflow ? 'text-green-600' : 'text-gray-600'}`}>
                      <CheckCircleIcon className={`w-5 h-5 mr-2 ${checklist.has_any_workflow ? 'text-green-500' : 'text-gray-400'}`} />
                      Create your first workflow
                      {checklist.has_any_workflow && <span className="ml-2 text-xs bg-green-100 text-green-800 px-2 py-1 rounded-full">✓ Done</span>}
                    </div>
                    <div className={`flex items-center ${checklist.has_any_integration ? 'text-green-600' : 'text-gray-600'}`}>
                      <CheckCircleIcon className={`w-5 h-5 mr-2 ${checklist.has_any_integration ? 'text-green-500' : 'text-gray-400'}`} />
                      Add an integration
                      {checklist.has_any_integration && <span className="ml-2 text-xs bg-green-100 text-green-800 px-2 py-1 rounded-full">✓ Done</span>}
                    </div>
                    <div className={`flex items-center ${checklist.has_any_execution ? 'text-green-600' : 'text-gray-600'}`}>
                      <CheckCircleIcon className={`w-5 h-5 mr-2 ${checklist.has_any_execution ? 'text-green-500' : 'text-gray-400'}`} />
                      Run your first automation
                      {checklist.has_any_execution && <span className="ml-2 text-xs bg-green-100 text-green-800 px-2 py-1 rounded-full">✓ Done</span>}
                    </div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-2xl font-bold text-primary-600">{Math.round(checklist.completion_percentage)}%</div>
                  <div className="text-sm text-gray-600">Complete</div>
                  <div className="w-16 h-2 bg-gray-200 rounded-full mt-2">
                    <div 
                      className="h-2 bg-gradient-to-r from-primary-500 to-accent-500 rounded-full transition-all duration-300"
                      style={{ width: `${checklist.completion_percentage}%` }}
                    />
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Metrics Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <MetricCard
              title="Total Workflows"
              value={stats?.total_workflows || 0}
              icon={ChartBarIcon}
              color="text-primary-600"
              trend={12}
              description="Number of workflows you've created"
            />
            <MetricCard
              title="Total Executions"
              value={stats?.total_executions || 0}
              icon={PlayIcon}
              color="text-accent-600"
              trend={8}
              description="Total workflow executions this month"
            />
            <MetricCard
              title="Success Rate"
              value={`${stats?.success_rate || 0}%`}
              icon={CheckCircleIcon}
              color="text-green-600"
              trend={5}
              description="Percentage of successful workflow executions"
            />
            <MetricCard
              title="Failed Executions"
              value={stats?.failed_executions || 0}
              icon={ExclamationTriangleIcon}
              color="text-red-600"
              trend={-15}
              description="Number of failed executions that need attention"
            />
          </div>

          {/* Charts Section */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
            <div className="chart-container">
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <TrendingUpIcon className="w-5 h-5 mr-2" />
                Execution Trends
                <InfoTooltip content="Daily workflow execution patterns over the last week" />
              </h3>
              <Suspense fallback={<LoadingSpinner />}>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={executionData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Line type="monotone" dataKey="executions" stroke="#0ea5e9" strokeWidth={2} name="Total" />
                    <Line type="monotone" dataKey="success" stroke="#10b981" strokeWidth={2} name="Success" />
                    <Line type="monotone" dataKey="failed" stroke="#ef4444" strokeWidth={2} name="Failed" />
                  </LineChart>
                </ResponsiveContainer>
              </Suspense>
            </div>

            <div className="chart-container">
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <BoltIcon className="w-5 h-5 mr-2" />
                Performance Breakdown
                <InfoTooltip content="Distribution of workflow types and their execution frequency" />
              </h3>
              <Suspense fallback={<LoadingSpinner />}>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={performanceData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="value" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </Suspense>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="mb-8">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-gray-900">Quick Actions</h2>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Link to="/editor" className="card p-6 text-center hover:shadow-lg transition-all duration-300 group">
                <div className="w-12 h-12 bg-gradient-to-r from-primary-500 to-accent-500 rounded-lg flex items-center justify-center mx-auto mb-3 group-hover:scale-110 transition-transform">
                  <PlusIcon className="w-6 h-6 text-white" />
                </div>
                <h3 className="font-semibold text-gray-900 mb-2">Create New Workflow</h3>
                <p className="text-gray-600 text-sm">Start building your automation from scratch</p>
              </Link>
              
              <Link to="/integrations" className="card p-6 text-center hover:shadow-lg transition-all duration-300 group">
                <div className="w-12 h-12 bg-gradient-to-r from-green-500 to-blue-500 rounded-lg flex items-center justify-center mx-auto mb-3 group-hover:scale-110 transition-transform">
                  <span className="text-white text-sm font-bold">45+</span>
                </div>
                <h3 className="font-semibold text-gray-900 mb-2">Browse Integrations</h3>
                <p className="text-gray-600 text-sm">Connect your favorite tools and services</p>
              </Link>
              
              <button 
                onClick={() => setShowAIAssistant(true)}
                className="card p-6 text-center hover:shadow-lg transition-all duration-300 group cursor-pointer"
              >
                <div className="w-12 h-12 bg-gradient-to-r from-purple-500 to-pink-500 rounded-lg flex items-center justify-center mx-auto mb-3 group-hover:scale-110 transition-transform">
                  <SparklesIcon className="w-6 h-6 text-white" />
                </div>
                <h3 className="font-semibold text-gray-900 mb-2">AI Assistant</h3>
                <p className="text-gray-600 text-sm">Get help creating workflows with AI</p>
              </button>
            </div>
          </div>

          {/* Workflows Section */}
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
                  <WorkflowCard
                    key={workflow.id}
                    workflow={workflow}
                    onExecute={executeWorkflow}
                    onDelete={deleteWorkflow}
                  />
                ))}
              </div>
            )}
          </div>
        </main>

        {/* AI Assistant Modal */}
        <EnhancedAIAssistant
          isOpen={showAIAssistant}
          onClose={() => setShowAIAssistant(false)}
          onWorkflowGenerated={handleAIWorkflowGenerated}
          sessionId={aiSessionId}
        />
      </div>
    </PerformanceMonitor>
  )
}

export default EnhancedDashboard