// Enhanced Performance Monitor Component
import React, { useState, useEffect, useRef } from 'react'
import {
  CpuChipIcon,
  ServerIcon,
  ChartBarIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  ClockIcon,
  BoltIcon,
  WifiIcon,
  CircleStackIcon,
  CloudIcon
} from '@heroicons/react/24/outline'
import { LineChart, Line, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'
import { enhancedApiMethods, handleApiError } from '../utils/enhancedApi'

// Hook for performance monitoring
export const useResourceMonitor = () => {
  const [metrics, setMetrics] = useState({
    memory: { used: 0, total: 0 },
    cpu: { usage: 0 },
    network: { down: 0, up: 0 },
    renderTime: 0
  })

  useEffect(() => {
    const observer = new PerformanceObserver((list) => {
      const entries = list.getEntries()
      entries.forEach((entry) => {
        if (entry.entryType === 'measure' && entry.name === 'React render') {
          setMetrics(prev => ({ ...prev, renderTime: entry.duration }))
        }
      })
    })

    observer.observe({ entryTypes: ['measure'] })

    // Monitor memory usage
    const updateMemoryMetrics = () => {
      if ('memory' in performance) {
        const memInfo = performance.memory
        setMetrics(prev => ({
          ...prev,
          memory: {
            used: memInfo.usedJSHeapSize / 1024 / 1024, // MB
            total: memInfo.totalJSHeapSize / 1024 / 1024 // MB
          }
        }))
      }
    }

    // Mock CPU and network metrics (in a real app, these would come from APIs)
    const updateSystemMetrics = () => {
      setMetrics(prev => ({
        ...prev,
        cpu: { usage: Math.random() * 100 },
        network: {
          down: Math.random() * 10,
          up: Math.random() * 2
        }
      }))
    }

    const interval = setInterval(() => {
      updateMemoryMetrics()
      updateSystemMetrics()
    }, 5000)

    updateMemoryMetrics()
    
    return () => {
      observer.disconnect()
      clearInterval(interval)
    }
  }, [])

  return metrics
}

// Performance logging utilities
export const initWebVitalsTracking = () => {
  if (typeof window === 'undefined') return

  // Core Web Vitals tracking
  const observeWebVitals = () => {
    // Largest Contentful Paint (LCP)
    new PerformanceObserver((entryList) => {
      const entries = entryList.getEntries()
      const lastEntry = entries[entries.length - 1]
      console.log('LCP:', lastEntry.startTime)
    }).observe({ entryTypes: ['largest-contentful-paint'] })

    // First Input Delay (FID)
    new PerformanceObserver((entryList) => {
      const entries = entryList.getEntries()
      entries.forEach((entry) => {
        console.log('FID:', entry.processingStart - entry.startTime)
      })
    }).observe({ entryTypes: ['first-input'] })

    // Cumulative Layout Shift (CLS)
    let clsValue = 0
    new PerformanceObserver((entryList) => {
      for (const entry of entryList.getEntries()) {
        if (!entry.hadRecentInput) {
          clsValue += entry.value
        }
      }
      console.log('CLS:', clsValue)
    }).observe({ entryTypes: ['layout-shift'] })
  }

  if (document.readyState === 'complete') {
    observeWebVitals()
  } else {
    window.addEventListener('load', observeWebVitals)
  }
}

export const logBundleSize = () => {
  if (typeof window === 'undefined') return

  // Log resource loading performance
  window.addEventListener('load', () => {
    const resources = performance.getEntriesByType('resource')
    let totalSize = 0
    let jsSize = 0
    let cssSize = 0

    resources.forEach((resource) => {
      if (resource.transferSize) {
        totalSize += resource.transferSize
        if (resource.name.includes('.js')) {
          jsSize += resource.transferSize
        } else if (resource.name.includes('.css')) {
          cssSize += resource.transferSize
        }
      }
    })

    console.log(`Bundle sizes - Total: ${(totalSize / 1024).toFixed(2)}KB, JS: ${(jsSize / 1024).toFixed(2)}KB, CSS: ${(cssSize / 1024).toFixed(2)}KB`)
  })
}

const PerformanceMonitor = ({ isOpen, onClose }) => {
  const [systemHealth, setSystemHealth] = useState(null)
  const [integrationHealth, setIntegrationHealth] = useState(null)
  const [performanceAnalysis, setPerformanceAnalysis] = useState(null)
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState('system')
  const [realTimeData, setRealTimeData] = useState([])
  const resourceMetrics = useResourceMonitor()
  const intervalRef = useRef()

  useEffect(() => {
    if (isOpen) {
      loadPerformanceData()
      startRealTimeMonitoring()
    } else {
      stopRealTimeMonitoring()
    }

    return () => stopRealTimeMonitoring()
  }, [isOpen])

  const loadPerformanceData = async () => {
    setLoading(true)
    try {
      const [systemResult, integrationResult, performanceResult] = await Promise.all([
        enhancedApiMethods.getSystemHealth(),
        enhancedApiMethods.getIntegrationHealth(),
        enhancedApiMethods.getPerformanceAnalysis()
      ])

      setSystemHealth(systemResult)
      setIntegrationHealth(integrationResult)
      setPerformanceAnalysis(performanceResult)
    } catch (error) {
      handleApiError(error)
    } finally {
      setLoading(false)
    }
  }

  const startRealTimeMonitoring = () => {
    intervalRef.current = setInterval(() => {
      const newDataPoint = {
        timestamp: new Date().toLocaleTimeString(),
        cpu: resourceMetrics.cpu.usage,
        memory: (resourceMetrics.memory.used / resourceMetrics.memory.total) * 100 || 0,
        response_time: Math.random() * 500 + 100, // Mock response time
        throughput: Math.random() * 100 + 50 // Mock throughput
      }
      
      setRealTimeData(prev => {
        const updated = [...prev, newDataPoint]
        return updated.slice(-20) // Keep last 20 data points
      })
    }, 2000)
  }

  const stopRealTimeMonitoring = () => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current)
    }
  }

  const getHealthStatus = (value, thresholds) => {
    if (value >= thresholds.critical) return { status: 'critical', color: 'red' }
    if (value >= thresholds.warning) return { status: 'warning', color: 'yellow' }
    return { status: 'healthy', color: 'green' }
  }

  const renderSystemMetrics = () => {
    if (!systemHealth?.metrics) return null

    return (
      <div className="space-y-6">
        {/* Real-time Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white dark:bg-gray-700 p-6 rounded-lg border border-gray-200 dark:border-gray-600">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
              <CpuChipIcon className="w-5 h-5 mr-2 text-blue-500" />
              Real-time Performance
            </h3>
            <ResponsiveContainer width="100%" height={250}>
              <AreaChart data={realTimeData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="timestamp" stroke="#6B7280" />
                <YAxis stroke="#6B7280" />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#1F2937',
                    border: '1px solid #374151',
                    borderRadius: '8px',
                    color: '#F9FAFB'
                  }}
                />
                <Area
                  type="monotone"
                  dataKey="cpu"
                  stackId="1"
                  stroke="#3B82F6"
                  fill="#3B82F6"
                  fillOpacity={0.3}
                  name="CPU %"
                />
                <Area
                  type="monotone"
                  dataKey="memory"
                  stackId="2"
                  stroke="#10B981"
                  fill="#10B981"
                  fillOpacity={0.3}
                  name="Memory %"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>

          <div className="bg-white dark:bg-gray-700 p-6 rounded-lg border border-gray-200 dark:border-gray-600">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
              <BoltIcon className="w-5 h-5 mr-2 text-purple-500" />
              Response Time & Throughput
            </h3>
            <ResponsiveContainer width="100%" height={250}>
              <LineChart data={realTimeData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="timestamp" stroke="#6B7280" />
                <YAxis stroke="#6B7280" />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#1F2937',
                    border: '1px solid #374151',
                    borderRadius: '8px',
                    color: '#F9FAFB'
                  }}
                />
                <Line
                  type="monotone"
                  dataKey="response_time"
                  stroke="#8B5CF6"
                  strokeWidth={2}
                  name="Response Time (ms)"
                />
                <Line
                  type="monotone"
                  dataKey="throughput"
                  stroke="#F59E0B"
                  strokeWidth={2}
                  name="Throughput"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* System Metrics Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {Object.entries(systemHealth.metrics).map(([key, metric]) => {
            const health = getHealthStatus(metric.value, {
              warning: metric.threshold_warning,
              critical: metric.threshold_critical
            })

            return (
              <div
                key={key}
                className="bg-white dark:bg-gray-700 p-4 rounded-lg border border-gray-200 dark:border-gray-600"
              >
                <div className="flex items-center justify-between mb-2">
                  <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    {metric.name}
                  </h4>
                  <div className={`w-3 h-3 rounded-full bg-${health.color}-500`}></div>
                </div>
                <div className="text-2xl font-bold text-gray-900 dark:text-white">
                  {metric.value.toFixed(1)}{metric.unit}
                </div>
                <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                  Status: {health.status}
                </div>
              </div>
            )
          })}
        </div>

        {/* Browser Performance */}
        <div className="bg-white dark:bg-gray-700 p-6 rounded-lg border border-gray-200 dark:border-gray-600">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
            <WifiIcon className="w-5 h-5 mr-2 text-green-500" />
            Browser Performance
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">
                {resourceMetrics.memory.used.toFixed(1)}MB
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400">
                Memory Used
              </div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">
                {resourceMetrics.renderTime.toFixed(1)}ms
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400">
                Render Time
              </div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">
                {resourceMetrics.cpu.usage.toFixed(1)}%
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400">
                CPU Usage
              </div>
            </div>
          </div>
        </div>
      </div>
    )
  }

  const renderIntegrationHealth = () => {
    if (!integrationHealth) return null

    const healthSummary = integrationHealth.integration_health_summary

    return (
      <div className="space-y-6">
        {/* Health Summary */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-white dark:bg-gray-700 p-4 rounded-lg border border-gray-200 dark:border-gray-600">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Total Integrations</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {healthSummary?.total_integrations || 0}
                </p>
              </div>
              <ServerIcon className="w-8 h-8 text-blue-500" />
            </div>
          </div>

          <div className="bg-white dark:bg-gray-700 p-4 rounded-lg border border-gray-200 dark:border-gray-600">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Healthy</p>
                <p className="text-2xl font-bold text-green-600">
                  {healthSummary?.healthy || 0}
                </p>
              </div>
              <CheckCircleIcon className="w-8 h-8 text-green-500" />
            </div>
          </div>

          <div className="bg-white dark:bg-gray-700 p-4 rounded-lg border border-gray-200 dark:border-gray-600">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Degraded</p>
                <p className="text-2xl font-bold text-yellow-600">
                  {healthSummary?.degraded || 0}
                </p>
              </div>
              <ExclamationTriangleIcon className="w-8 h-8 text-yellow-500" />
            </div>
          </div>

          <div className="bg-white dark:bg-gray-700 p-4 rounded-lg border border-gray-200 dark:border-gray-600">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Critical</p>
                <p className="text-2xl font-bold text-red-600">
                  {healthSummary?.critical || 0}
                </p>
              </div>
              <ExclamationTriangleIcon className="w-8 h-8 text-red-500" />
            </div>
          </div>
        </div>

        {/* Health Distribution Chart */}
        {healthSummary && (
          <div className="bg-white dark:bg-gray-700 p-6 rounded-lg border border-gray-200 dark:border-gray-600">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Integration Health Distribution
            </h3>
            <div className="flex items-center justify-center">
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={[
                      { name: 'Healthy', value: healthSummary.healthy, color: '#10B981' },
                      { name: 'Degraded', value: healthSummary.degraded, color: '#F59E0B' },
                      { name: 'Critical', value: healthSummary.critical, color: '#EF4444' }
                    ]}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                    outerRadius={100}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {[
                      { name: 'Healthy', value: healthSummary.healthy, color: '#10B981' },
                      { name: 'Degraded', value: healthSummary.degraded, color: '#F59E0B' },
                      { name: 'Critical', value: healthSummary.critical, color: '#EF4444' }
                    ].map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}
      </div>
    )
  }

  const renderPerformanceAnalysis = () => {
    if (!performanceAnalysis) return null

    return (
      <div className="space-y-6">
        {/* Performance Summary */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-white dark:bg-gray-700 p-4 rounded-lg border border-gray-200 dark:border-gray-600">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Health Score</p>
                <p className="text-2xl font-bold text-primary-600">
                  {performanceAnalysis.system_performance?.overall_health_score || 0}
                </p>
              </div>
              <ChartBarIcon className="w-8 h-8 text-primary-500" />
            </div>
          </div>

          <div className="bg-white dark:bg-gray-700 p-4 rounded-lg border border-gray-200 dark:border-gray-600">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Avg Response</p>
                <p className="text-2xl font-bold text-blue-600">
                  {performanceAnalysis.system_performance?.avg_response_time || 0}ms
                </p>
              </div>
              <ClockIcon className="w-8 h-8 text-blue-500" />
            </div>
          </div>

          <div className="bg-white dark:bg-gray-700 p-4 rounded-lg border border-gray-200 dark:border-gray-600">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Success Rate</p>
                <p className="text-2xl font-bold text-green-600">
                  {performanceAnalysis.system_performance?.success_rate || 0}%
                </p>
              </div>
              <CheckCircleIcon className="w-8 h-8 text-green-500" />
            </div>
          </div>

          <div className="bg-white dark:bg-gray-700 p-4 rounded-lg border border-gray-200 dark:border-gray-600">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Executions (24h)</p>
                <p className="text-2xl font-bold text-purple-600">
                  {performanceAnalysis.system_performance?.total_executions_24h || 0}
                </p>
              </div>
              <BoltIcon className="w-8 h-8 text-purple-500" />
            </div>
          </div>
        </div>

        {/* Optimization Suggestions */}
        {performanceAnalysis.optimization_opportunities && (
          <div className="bg-white dark:bg-gray-700 p-6 rounded-lg border border-gray-200 dark:border-gray-600">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
              <BoltIcon className="w-5 h-5 mr-2 text-yellow-500" />
              Optimization Opportunities
            </h3>
            <div className="space-y-3">
              {performanceAnalysis.optimization_opportunities.map((suggestion, index) => (
                <div
                  key={index}
                  className="p-3 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg"
                >
                  <p className="text-yellow-800 dark:text-yellow-200">{suggestion}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    )
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-2xl w-full max-w-7xl max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="p-6 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center">
              <ChartBarIcon className="w-8 h-8 mr-3 text-primary-600" />
              Performance Monitor
            </h2>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
            >
              <span className="sr-only">Close</span>
              <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* Tabs */}
          <div className="flex space-x-1 bg-gray-100 dark:bg-gray-700 p-1 rounded-lg">
            {[
              { id: 'system', name: 'System Health', icon: CpuChipIcon },
              { id: 'integrations', name: 'Integrations', icon: ServerIcon },
              { id: 'performance', name: 'Performance', icon: ChartBarIcon }
            ].map((tab) => {
              const Icon = tab.icon
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex-1 flex items-center justify-center px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                    activeTab === tab.id
                      ? 'bg-white dark:bg-gray-600 text-primary-600 dark:text-primary-400 shadow-sm'
                      : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
                  }`}
                >
                  <Icon className="w-4 h-4 mr-2" />
                  {tab.name}
                </button>
              )
            })}
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {loading ? (
            <div className="flex items-center justify-center h-64">
              <LoadingSpinner size="large" />
            </div>
          ) : (
            <>
              {activeTab === 'system' && renderSystemMetrics()}
              {activeTab === 'integrations' && renderIntegrationHealth()}
              {activeTab === 'performance' && renderPerformanceAnalysis()}
            </>
          )}
        </div>
      </div>
    </div>
  )
}

export default PerformanceMonitor