import React, { useState, useEffect } from 'react'
import { apiMethods } from '../utils/api'
import { 
  SparklesIcon,
  LightBulbIcon,
  ChartBarIcon,
  UserGroupIcon,
  BeakerIcon,
  EyeIcon,
  EyeSlashIcon
} from '@heroicons/react/24/outline'

/**
 * OptionalEnhancements Component
 * 
 * This component provides optional UI enhancements that are HIDDEN BY DEFAULT
 * and only appear when users explicitly enable them in settings.
 * 
 * Core Principle: ZERO UI DISRUPTION
 * - All enhancements are invisible until enabled
 * - Graceful fallback if backend features are unavailable
 * - Preserves existing UI/UX completely
 */

const OptionalEnhancements = ({ 
  children, 
  userId, 
  dashboardStats = {}, 
  className = "" 
}) => {
  const [userPreferences, setUserPreferences] = useState({})
  const [enhancementData, setEnhancementData] = useState({})
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (userId) {
      loadUserPreferences()
    }
  }, [userId])

  const loadUserPreferences = async () => {
    try {
      const response = await apiMethods.getEnhancementFeatures()
      if (response.success && response.data.features) {
        // Extract user preferences from the features data
        const preferences = {}
        Object.values(response.data.features).forEach(phase => {
          Object.entries(phase.features || {}).forEach(([key, feature]) => {
            preferences[key] = feature.enabled
          })
        })
        setUserPreferences(preferences)
        
        // Load enhancement data if any features are enabled
        if (Object.values(preferences).some(enabled => enabled)) {
          loadEnhancementData()
        }
      }
    } catch (error) {
      console.error('Error loading user preferences:', error)
      // Fail silently - no disruption to existing UI
    }
  }

  const loadEnhancementData = async () => {
    try {
      setLoading(true)
      const data = {}
      
      // Load AI suggestions if enabled
      if (userPreferences.ai_smart_suggestions) {
        try {
          const suggestions = await apiMethods.getSmartSuggestions()
          if (suggestions.success) {
            data.aiSuggestions = suggestions.suggestions
          }
        } catch (error) {
          console.warn('AI suggestions failed to load:', error)
        }
      }
      
      // Load predictive insights if enabled
      if (userPreferences.ai_predictive_analytics) {
        try {
          const insights = await apiMethods.getAIInsights()
          if (insights.success) {
            data.predictiveInsights = insights.insights
          }
        } catch (error) {
          console.warn('Predictive insights failed to load:', error)
        }
      }
      
      // Load collaboration features if enabled
      if (userPreferences.enterprise_workspaces) {
        try {
          const workspaces = await apiMethods.getUserWorkspaces()
          if (workspaces.success) {
            data.workspaces = workspaces.data.workspaces || []
          }
        } catch (error) {
          console.warn('Workspaces failed to load:', error)
        }
      }
      
      // Load advanced analytics if enabled
      if (userPreferences.advanced_analytics) {
        try {
          const analytics = await apiMethods.getAdvancedAnalytics({
            time_range: '30d',
            include_predictions: true
          })
          if (analytics.success) {
            data.advancedAnalytics = analytics.analytics
          }
        } catch (error) {
          console.warn('Advanced analytics failed to load:', error)
        }
      }
      
      setEnhancementData(data)
    } catch (error) {
      console.error('Error loading enhancement data:', error)
      // Fail silently - no disruption to existing UI
    } finally {
      setLoading(false)
    }
  }

  // AI Suggestions Widget (Phase 2)
  const AISuggestionsWidget = () => {
    if (!userPreferences.ai_smart_suggestions || !enhancementData.aiSuggestions) {
      return null
    }

    return (
      <div className="bg-gradient-to-r from-purple-50 to-pink-50 border border-purple-200 rounded-lg p-4 mb-4">
        <div className="flex items-center space-x-2 mb-3">
          <SparklesIcon className="w-5 h-5 text-purple-600" />
          <h3 className="font-semibold text-purple-900">AI Smart Suggestions</h3>
        </div>
        <div className="space-y-2">
          {enhancementData.aiSuggestions.slice(0, 3).map((suggestion, index) => (
            <div key={index} className="text-sm bg-white/60 rounded p-3">
              <div className="font-medium text-purple-800">{suggestion.title}</div>
              <div className="text-purple-600 text-xs mt-1">{suggestion.description}</div>
              <div className="text-xs text-purple-500 mt-1">
                ⏱️ Saves ~{suggestion.potential_time_savings}min • {suggestion.complexity_level}
              </div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  // Predictive Insights Widget (Phase 2)
  const PredictiveInsightsWidget = () => {
    if (!userPreferences.ai_predictive_analytics || !enhancementData.predictiveInsights) {
      return null
    }

    return (
      <div className="bg-gradient-to-r from-blue-50 to-cyan-50 border border-blue-200 rounded-lg p-4 mb-4">
        <div className="flex items-center space-x-2 mb-3">
          <ChartBarIcon className="w-5 h-5 text-blue-600" />
          <h3 className="font-semibold text-blue-900">Predictive Insights</h3>
        </div>
        <div className="space-y-2">
          {enhancementData.predictiveInsights.slice(0, 2).map((insight, index) => (
            <div key={index} className="text-sm bg-white/60 rounded p-3">
              <div className="font-medium text-blue-800">{insight.title}</div>
              <div className="text-blue-600 text-xs mt-1">{insight.description}</div>
              <div className="flex items-center justify-between mt-2">
                <span className="text-xs text-blue-500">
                  Confidence: {Math.round(insight.confidence_score * 100)}%
                </span>
                <span className={`text-xs px-2 py-1 rounded ${
                  insight.impact_level === 'high' ? 'bg-red-100 text-red-600' :
                  insight.impact_level === 'medium' ? 'bg-yellow-100 text-yellow-600' :
                  'bg-green-100 text-green-600'
                }`}>
                  {insight.impact_level} impact
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  // Collaboration Widget (Phase 3)
  const CollaborationWidget = () => {
    if (!userPreferences.enterprise_workspaces || !enhancementData.workspaces?.length) {
      return null
    }

    return (
      <div className="bg-gradient-to-r from-green-50 to-teal-50 border border-green-200 rounded-lg p-4 mb-4">
        <div className="flex items-center space-x-2 mb-3">
          <UserGroupIcon className="w-5 h-5 text-green-600" />
          <h3 className="font-semibold text-green-900">Team Workspaces</h3>
        </div>
        <div className="space-y-2">
          {enhancementData.workspaces.slice(0, 3).map((workspace, index) => (
            <div key={index} className="text-sm bg-white/60 rounded p-3">
              <div className="font-medium text-green-800">{workspace.name}</div>
              <div className="text-green-600 text-xs mt-1">
                {workspace.members?.length || 0} members • {workspace.user_role}
              </div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  // Advanced Analytics Widget (Phase 4)
  const AdvancedAnalyticsWidget = () => {
    if (!userPreferences.advanced_analytics || !enhancementData.advancedAnalytics) {
      return null
    }

    const analytics = enhancementData.advancedAnalytics
    
    return (
      <div className="bg-gradient-to-r from-indigo-50 to-purple-50 border border-indigo-200 rounded-lg p-4 mb-4">
        <div className="flex items-center space-x-2 mb-3">
          <ChartBarIcon className="w-5 h-5 text-indigo-600" />
          <h3 className="font-semibold text-indigo-900">Advanced Analytics</h3>
        </div>
        <div className="grid grid-cols-2 gap-3">
          {analytics.performance_trends && (
            <div className="text-sm bg-white/60 rounded p-3">
              <div className="font-medium text-indigo-800">Performance Trend</div>
              <div className="text-lg font-bold text-indigo-600">
                {analytics.performance_trends.trend === 'improving' ? '📈' : '📊'} 
                {analytics.performance_trends.trend}
              </div>
            </div>
          )}
          {analytics.productivity_insights && (
            <div className="text-sm bg-white/60 rounded p-3">
              <div className="font-medium text-indigo-800">Productivity Score</div>
              <div className="text-lg font-bold text-indigo-600">
                {Math.round(analytics.productivity_insights.productivity_score)}%
              </div>
            </div>
          )}
        </div>
      </div>
    )
  }

  // Future Tech Widget (Phase 5)
  const FutureTechWidget = () => {
    const hasFutureTech = userPreferences.iot_integration || 
                         userPreferences.blockchain_verification || 
                         userPreferences.custom_ai_models

    if (!hasFutureTech) {
      return null
    }

    return (
      <div className="bg-gradient-to-r from-orange-50 to-red-50 border border-orange-200 rounded-lg p-4 mb-4">
        <div className="flex items-center space-x-2 mb-3">
          <BeakerIcon className="w-5 h-5 text-orange-600" />
          <h3 className="font-semibold text-orange-900">Future Technologies</h3>
        </div>
        <div className="text-sm space-y-2">
          {userPreferences.iot_integration && (
            <div className="bg-white/60 rounded p-2">
              <span className="text-orange-800">🔗 IoT Integration Available</span>
            </div>
          )}
          {userPreferences.blockchain_verification && (
            <div className="bg-white/60 rounded p-2">
              <span className="text-orange-800">🔐 Blockchain Verification Active</span>
            </div>
          )}
          {userPreferences.custom_ai_models && (
            <div className="bg-white/60 rounded p-2">
              <span className="text-orange-800">🤖 Custom AI Models Ready</span>
            </div>
          )}
        </div>
      </div>
    )
  }

  // Main render - only show enhancements if user has enabled any features
  const hasAnyEnhancementsEnabled = Object.values(userPreferences).some(enabled => enabled)

  return (
    <div className={className}>
      {/* Original children - ALWAYS rendered first, unchanged */}
      {children}
      
      {/* Optional enhancements - ONLY if user has enabled them */}
      {hasAnyEnhancementsEnabled && (
        <div className="mt-6 space-y-4">
          {/* Enhancement indicator - very subtle */}
          <div className="flex items-center justify-between text-xs text-gray-500 border-t pt-4">
            <span>Enhanced features active</span>
            <div className="flex items-center space-x-1">
              <EyeIcon className="w-3 h-3" />
              <span>Optional enhancements</span>
            </div>
          </div>
          
          {/* Enhancement widgets */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <div>
              <AISuggestionsWidget />
              <PredictiveInsightsWidget />
            </div>
            <div>
              <CollaborationWidget />
              <AdvancedAnalyticsWidget />
              <FutureTechWidget />
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default OptionalEnhancements