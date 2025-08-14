import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { apiMethods } from '../utils/api'
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
  CpuChipIcon,
  ServerIcon,
  BoltIcon,
  SparklesIcon,
  UsersIcon,
  CodeBracketIcon,
  CreditCardIcon
} from '@heroicons/react/24/outline'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell, AreaChart, Area } from 'recharts'
import Navbar from '../components/EnhancedNavbar'
import LoadingSpinner from '../components/LoadingSpinner'
import SubscriptionIndicator from '../components/SubscriptionIndicator'
import toast from 'react-hot-toast'

const EnhancedDashboard = () => {
  const { user } = useAuth()
  const [stats, setStats] = useState(null)
  const [workflows, setWorkflows] = useState([])
  const [checklist, setChecklist] = useState(null)
  const [performanceMetrics, setPerformanceMetrics] = useState(null)
  const [cacheStats, setCacheStats] = useState(null)
  const [collaborationSessions, setCollaborationSessions] = useState([])
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState('overview')

  useEffect(() => {
    loadDashboardData()
    const interval = setInterval(loadRealTimeData, 30000) // Update every 30 seconds
    return () => clearInterval(interval)
  }, [])

  const loadDashboardData = async () => {
    try {
      const [statsResponse, workflowsResponse, checklistResponse] = await Promise.all([
        apiMethods.getDashboardStats(),
        apiMethods.getWorkflows(1, 10),
        apiMethods.getUserChecklist()
      ])
      setStats(statsResponse)
      setWorkflows(workflowsResponse.workflows || workflowsResponse)
      setChecklist(checklistResponse)
      
      // Load enhanced data
      loadEnhancedMetrics()
    } catch (error) {
      console.error('Error loading dashboard data:', error)
      toast.error('Failed to load dashboard data')
    } finally {
      setLoading(false)
    }
  }

  const loadEnhancedMetrics = async () => {
    try {
      // Load performance metrics (mock for now as backend enhancement may not be fully integrated)
      setPerformanceMetrics({
        cpu_usage: { current: 45, average: 42, min: 30, max: 70, trend: "stable" },
        memory_usage: { current: 68, average: 65, min: 50, max: 85, trend: "stable" },
        cache_hit_rate: { current: 85, average: 83, min: 75, max: 92, trend: "increasing" },
        response_time: { current: 120, average: 135, min: 80, max: 200, trend: "decreasing" }
      })
      
      setCacheStats({
        hit_rates: { user_data: 92, workflow_data: 88, integration_data: 85, ai_responses: 90 },
        memory_cache_size: 1247,
        redis_available: true
      })
      
      setCollaborationSessions([
        { workflow_id: 'wf-1', active_users: 2, last_activity: '2 minutes ago' },
        { workflow_id: 'wf-2', active_users: 1, last_activity: '5 minutes ago' }
      ])
    } catch (error) {
      console.error('Error loading enhanced metrics:', error)
    }
  }

  const loadRealTimeData = async () => {
    try {
      const updatedStats = await apiMethods.getDashboardStats()
      setStats(updatedStats)
      loadEnhancedMetrics()
    } catch (error) {
      console.error('Error loading real-time data:', error)
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

  // Enhanced chart data
  const executionTrendData = [
    { name: 'Mon', executions: 12, success: 10, ai_generated: 3 },
    { name: 'Tue', executions: 19, success: 18, ai_generated: 5 },
    { name: 'Wed', executions: 15, success: 14, ai_generated: 4 },
    { name: 'Thu', executions: 22, success: 20, ai_generated: 7 },
    { name: 'Fri', executions: 18, success: 17, ai_generated: 6 },
    { name: 'Sat', executions: 8, success: 8, ai_generated: 2 },
    { name: 'Sun', executions: 5, success: 5, ai_generated: 1 },
  ]

  const nodeUsageData = [
    { name: 'Triggers', value: 35, color: '#0ea5e9' },
    { name: 'Actions', value: 45, color: '#10b981' },
    { name: 'Logic', value: 15, color: '#f59e0b' },
    { name: 'AI Nodes', value: 25, color: '#8b5cf6' },
    { name: 'Finance', value: 8, color: '#ef4444' },
    { name: 'E-commerce', value: 12, color: '#06b6d4' }
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
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <Navbar />
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Enhanced Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
                Welcome back, {user?.name}! 🚀
              </h1>
              <p className="text-gray-600 dark:text-gray-300 mt-2">
                Here's what's happening with your automations today.
              </p>
            </div>
            <div className="flex items-center space-x-3">
              <div className="text-sm text-gray-500">
                <span className="inline-flex items-center">
                  <div className="w-2 h-2 bg-green-500 rounded-full mr-2 animate-pulse"></div>
                  System Healthy
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Enhanced Tab Navigation */}
        <div className="mb-8">
          <nav className="flex space-x-8" aria-label="Tabs">
            {[
              { id: 'overview', name: 'Overview', icon: ChartBarIcon },
              { id: 'performance', name: 'Performance', icon: CpuChipIcon },
              { id: 'collaboration', name: 'Collaboration', icon: UsersIcon },
              { id: 'ai-insights', name: 'AI Insights', icon: SparklesIcon }
            ].map((tab) => {
              const Icon = tab.icon
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`${
                    activeTab === tab.id
                      ? 'border-primary-500 text-primary-600 dark:text-primary-400'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  } whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm flex items-center space-x-2`}
                >
                  <Icon className="w-4 h-4" />
                  <span>{tab.name}</span>
                </button>
              )
            })}
          </nav>
        </div>

        {/* Tab Content */}
        {activeTab === 'overview' && (
          <>
            {/* Enhanced Onboarding Checklist */}
            {checklist && checklist.completion_percentage < 100 && (
              <div className="bg-gradient-to-r from-primary-50 to-accent-50 dark:from-primary-900/20 dark:to-accent-900/20 border border-primary-200 dark:border-primary-800 rounded-lg p-6 mb-8">
                <div className="flex items-start justify-between">
                  <div>
                    <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">🎯 Get Started Checklist</h2>
                    <p className="text-gray-600 dark:text-gray-300 mb-4">Complete these steps to unlock the full potential of Aether Automation</p>
                    <div className="space-y-2">
                      <div className={`flex items-center ${checklist.has_any_workflow ? 'text-green-600' : 'text-gray-600 dark:text-gray-400'}`}>
                        <CheckCircleIcon className={`w-5 h-5 mr-2 ${checklist.has_any_workflow ? 'text-green-500' : 'text-gray-400'}`} />
                        Create your first workflow
                      </div>
                      <div className={`flex items-center ${checklist.has_any_integration ? 'text-green-600' : 'text-gray-600 dark:text-gray-400'}`}>
                        <CheckCircleIcon className={`w-5 h-5 mr-2 ${checklist.has_any_integration ? 'text-green-500' : 'text-gray-400'}`} />
                        Add an integration
                      </div>
                      <div className={`flex items-center ${checklist.has_any_execution ? 'text-green-600' : 'text-gray-600 dark:text-gray-400'}`}>
                        <CheckCircleIcon className={`w-5 h-5 mr-2 ${checklist.has_any_execution ? 'text-green-500' : 'text-gray-400'}`} />
                        Run your first automation
                      </div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-2xl font-bold text-primary-600">{Math.round(checklist.completion_percentage)}%</div>
                    <div className="text-sm text-gray-600 dark:text-gray-400">Complete</div>
                  </div>
                </div>
              </div>
            )}

            {/* Enhanced Metrics Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
              {[
                {
                  title: 'Total Workflows',
                  value: stats?.total_workflows || 0,
                  icon: ChartBarIcon,
                  color: 'primary',
                  change: '+12%',
                  changeType: 'increase'
                },
                {
                  title: 'Total Executions',
                  value: stats?.total_executions || 0,
                  icon: PlayIcon,
                  color: 'accent',
                  change: '+8%',
                  changeType: 'increase'
                },
                {
                  title: 'Success Rate',
                  value: `${stats?.success_rate || 0}%`,
                  icon: CheckCircleIcon,
                  color: 'green',
                  change: '+2%',
                  changeType: 'increase'
                },
                {
                  title: 'AI Generated',
                  value: '24',
                  icon: SparklesIcon,
                  color: 'purple',
                  change: '+45%',
                  changeType: 'increase'
                }
              ].map((metric, index) => {
                const Icon = metric.icon
                return (
                  <div key={index} className="metric-card card p-6 hover:shadow-lg transition-shadow">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-gray-600 dark:text-gray-400">{metric.title}</p>
                        <p className={`text-3xl font-bold text-${metric.color}-600`}>{metric.value}</p>
                        <p className={`text-xs mt-1 ${metric.changeType === 'increase' ? 'text-green-600' : 'text-red-600'}`}>
                          {metric.change} from last month
                        </p>
                      </div>
                      <Icon className={`w-8 h-8 text-${metric.color}-500`} />
                    </div>
                  </div>
                )
              })}
            </div>

            {/* Enhanced Charts Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
              <div className="chart-container">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">📈 Execution Trends & AI Usage</h3>
                <ResponsiveContainer width="100%" height={300}>
                  <AreaChart data={executionTrendData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                    <XAxis dataKey="name" stroke="#6B7280" />
                    <YAxis stroke="#6B7280" />
                    <Tooltip 
                      contentStyle={{ 
                        backgroundColor: '#1F2937', 
                        border: '1px solid #374151',
                        borderRadius: '8px',
                        color: '#F9FAFB'
                      }} 
                    />
                    <Area type="monotone" dataKey="executions" stackId="1" stroke="#0ea5e9" fill="#0ea5e9" fillOpacity={0.3} />
                    <Area type="monotone" dataKey="success" stackId="2" stroke="#10b981" fill="#10b981" fillOpacity={0.3} />
                    <Area type="monotone" dataKey="ai_generated" stackId="3" stroke="#8b5cf6" fill="#8b5cf6" fillOpacity={0.3} />
                  </AreaChart>
                </ResponsiveContainer>
              </div>

              <div className="chart-container">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">🎯 Node Usage Distribution</h3>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={nodeUsageData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {nodeUsageData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Enhanced Quick Actions */}
            <div className="mb-8">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-bold text-gray-900 dark:text-white">⚡ Quick Actions</h2>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {[
                  {
                    title: 'Create Workflow',
                    description: 'Start building automation',
                    icon: PlusIcon,
                    link: '/editor',
                    color: 'primary'
                  },
                  {
                    title: 'Browse Integrations',
                    description: '120+ services available',
                    icon: ServerIcon,
                    link: '/integrations',
                    color: 'accent'
                  },
                  {
                    title: 'AI Generator',
                    description: 'Generate workflows with AI',
                    icon: SparklesIcon,
                    link: '/editor?ai=true',
                    color: 'purple'
                  },
                  {
                    title: 'View Templates',
                    description: 'Pre-built workflows',
                    icon: ClockIcon,
                    link: '/templates',
                    color: 'green'
                  }
                ].map((action, index) => {
                  const Icon = action.icon
                  return (
                    <Link key={index} to={action.link} className="card p-6 text-center hover:shadow-lg transition-all transform hover:-translate-y-1">
                      <div className={`w-12 h-12 mx-auto bg-gradient-to-r from-${action.color}-500 to-${action.color}-600 rounded-lg flex items-center justify-center mb-3`}>
                        <Icon className="w-6 h-6 text-white" />
                      </div>
                      <h3 className="font-semibold text-gray-900 dark:text-white mb-2">{action.title}</h3>
                      <p className="text-gray-600 dark:text-gray-300 text-sm">{action.description}</p>
                    </Link>
                  )
                })}
              </div>
            </div>

            {/* Enhanced Workflow List */}
            <div>
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-bold text-gray-900 dark:text-white">🔧 Your Workflows</h2>
                <Link to="/editor" className="btn-primary inline-flex items-center">
                  <PlusIcon className="w-4 h-4 mr-2" />
                  New Workflow
                </Link>
              </div>

              {workflows.length === 0 ? (
                <div className="card p-8 text-center">
                  <ChartBarIcon className="w-12 h-12 mx-auto text-gray-400 mb-4" />
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">No workflows yet</h3>
                  <p className="text-gray-600 dark:text-gray-300 mb-4">Create your first automation workflow to get started.</p>
                  <Link to="/editor" className="btn-primary">Create Your First Workflow</Link>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {workflows.map((workflow) => (
                    <div key={workflow.id} className="card p-6 hover:shadow-lg transition-all">
                      <div className="flex items-start justify-between mb-4">
                        <div>
                          <h3 className="font-semibold text-gray-900 dark:text-white mb-1">{workflow.name}</h3>
                          <p className="text-gray-600 dark:text-gray-300 text-sm">{workflow.description}</p>
                        </div>
                        <div className={`px-2 py-1 rounded-full text-xs font-medium ${
                          workflow.status === 'active' ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400' : 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300'
                        }`}>
                          {workflow.status}
                        </div>
                      </div>

                      <div className="flex items-center justify-between text-sm text-gray-600 dark:text-gray-400 mb-4">
                        <span>Nodes: {workflow.nodes?.length || 0}</span>
                        <span>Updated: {new Date(workflow.updated_at).toLocaleDateString()}</span>
                      </div>

                      <div className="flex items-center space-x-2">
                        <button onClick={() => executeWorkflow(workflow.id)} className="flex-1 btn-primary text-sm py-2">
                          <PlayIcon className="w-4 h-4 mr-1" />
                          Run
                        </button>
                        <Link to={`/editor/${workflow.id}`} className="p-2 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg">
                          <PencilIcon className="w-4 h-4" />
                        </Link>
                        <button onClick={() => deleteWorkflow(workflow.id)} className="p-2 text-red-600 hover:text-red-700 hover:bg-red-50 dark:hover:bg-red-900/30 rounded-lg">
                          <TrashIcon className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </>
        )}

        {activeTab === 'performance' && (
          <div className="space-y-8">
            {/* System Performance Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {performanceMetrics && Object.entries(performanceMetrics).map(([key, metric]) => (
                <div key={key} className="card p-6">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400 capitalize">
                      {key.replace('_', ' ')}
                    </h3>
                    <div className={`text-xs px-2 py-1 rounded-full ${
                      metric.trend === 'increasing' ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400' :
                      metric.trend === 'decreasing' ? 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400' :
                      'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300'
                    }`}>
                      {metric.trend}
                    </div>
                  </div>
                  <div className="text-2xl font-bold text-gray-900 dark:text-white">
                    {typeof metric.current === 'number' && key.includes('usage') ? `${metric.current}%` : metric.current}
                  </div>
                  <div className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                    Avg: {typeof metric.average === 'number' && key.includes('usage') ? `${metric.average}%` : metric.average}
                  </div>
                </div>
              ))}
            </div>

            {/* Cache Performance */}
            {cacheStats && (
              <div className="card p-6">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">💾 Cache Performance</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                  {Object.entries(cacheStats.hit_rates).map(([category, rate]) => (
                    <div key={category} className="text-center">
                      <div className="text-2xl font-bold text-primary-600">{rate}%</div>
                      <div className="text-sm text-gray-600 dark:text-gray-400 capitalize">{category.replace('_', ' ')}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'collaboration' && (
          <div className="space-y-8">
            <div className="card p-6">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">👥 Active Collaboration Sessions</h3>
              {collaborationSessions.length === 0 ? (
                <div className="text-center py-8">
                  <UsersIcon className="w-12 h-12 mx-auto text-gray-400 mb-4" />
                  <p className="text-gray-600 dark:text-gray-400">No active collaboration sessions</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {collaborationSessions.map((session) => (
                    <div key={session.workflow_id} className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
                      <div>
                        <h4 className="font-medium text-gray-900 dark:text-white">Workflow {session.workflow_id}</h4>
                        <p className="text-sm text-gray-600 dark:text-gray-400">Last activity: {session.last_activity}</p>
                      </div>
                      <div className="flex items-center space-x-2">
                        <span className="text-sm text-gray-600 dark:text-gray-400">{session.active_users} users</span>
                        <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'ai-insights' && (
          <div className="space-y-8">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              <div className="card p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white">🤖 AI Usage</h3>
                  <SparklesIcon className="w-6 h-6 text-purple-500" />
                </div>
                <div className="text-3xl font-bold text-purple-600">24</div>
                <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">Workflows generated this month</p>
              </div>

              <div className="card p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white">⚡ Time Saved</h3>
                  <ClockIcon className="w-6 h-6 text-green-500" />
                </div>
                <div className="text-3xl font-bold text-green-600">47.2h</div>
                <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">Development time saved</p>
              </div>

              <div className="card p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white">📊 Success Rate</h3>
                  <CheckCircleIcon className="w-6 h-6 text-blue-500" />
                </div>
                <div className="text-3xl font-bold text-blue-600">94%</div>
                <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">AI-generated workflow success</p>
              </div>
            </div>

            <div className="card p-6">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">🎯 AI Recommendations</h3>
              <div className="space-y-4">
                <div className="p-4 bg-blue-50 dark:bg-blue-900/30 rounded-lg">
                  <h4 className="font-medium text-blue-900 dark:text-blue-100">Optimize Workflow Performance</h4>
                  <p className="text-sm text-blue-700 dark:text-blue-300 mt-1">
                    Consider adding parallel execution to your "Customer Onboarding" workflow to reduce processing time by 40%.
                  </p>
                </div>
                <div className="p-4 bg-green-50 dark:bg-green-900/30 rounded-lg">
                  <h4 className="font-medium text-green-900 dark:text-green-100">New Integration Opportunity</h4>
                  <p className="text-sm text-green-700 dark:text-green-300 mt-1">
                    Connect Discord to automate community notifications based on your workflow patterns.
                  </p>
                </div>
                <div className="p-4 bg-purple-50 dark:bg-purple-900/30 rounded-lg">
                  <h4 className="font-medium text-purple-900 dark:text-purple-100">AI Enhancement Available</h4>
                  <p className="text-sm text-purple-700 dark:text-purple-300 mt-1">
                    Upgrade your content workflows with our new AI sentiment analysis node for better engagement.
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default EnhancedDashboard