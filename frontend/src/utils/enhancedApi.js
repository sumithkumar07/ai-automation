/**
 * Enhanced API Client for GROQ-powered features
 * Minimal UI integration for enhanced backend systems
 */

import { apiMethods } from './api'

const enhancedApiMethods = {
  // Enhanced AI features using GROQ
  async getEnhancedDashboardInsights() {
    try {
      const response = await apiMethods.makeRequest('/api/ai/dashboard-insights', {
        method: 'GET'
      })
      return response
    } catch (error) {
      console.error('Enhanced dashboard insights error:', error)
      return { error: 'Failed to get AI insights', fallback: true }
    }
  },

  async getSmartSuggestions() {
    try {
      const response = await apiMethods.makeRequest('/api/ai/smart-suggestions', {
        method: 'POST'
      })
      return response
    } catch (error) {
      console.error('Smart suggestions error:', error)
      return { suggestions: [], error: 'AI suggestions unavailable' }
    }
  },

  async generateNaturalWorkflow(description) {
    try {
      const response = await apiMethods.makeRequest('/api/ai/generate-natural-workflow', {
        method: 'POST',
        body: JSON.stringify({ message: description })
      })
      return response
    } catch (error) {
      console.error('Natural workflow generation error:', error)
      return { error: 'Failed to generate workflow' }
    }
  },

  // Enhanced system status and performance
  async getEnhancedSystemStatus() {
    try {
      const response = await apiMethods.makeRequest('/api/enhanced/system-status', {
        method: 'GET'
      })
      return response
    } catch (error) {
      console.error('Enhanced system status error:', error)
      return { system_status: 'unavailable', error: error.message }
    }
  },

  async getPerformanceReport() {
    try {
      const response = await apiMethods.makeRequest('/api/enhanced/performance-report', {
        method: 'GET'
      })
      return response
    } catch (error) {
      console.error('Performance report error:', error)
      return { error: 'Performance report unavailable' }
    }
  },

  async optimizeGroqApi() {
    try {
      const response = await apiMethods.makeRequest('/api/enhanced/optimize-groq-api', {
        method: 'POST'
      })
      return response
    } catch (error) {
      console.error('GROQ API optimization error:', error)
      return { error: 'Optimization unavailable' }
    }
  },

  // Enhanced UX and accessibility features
  async getAccessibilityAnalysis() {
    try {
      const response = await apiMethods.makeRequest('/api/enhanced/accessibility-analysis', {
        method: 'GET'
      })
      return response
    } catch (error) {
      console.error('Accessibility analysis error:', error)
      return { error: 'Accessibility analysis unavailable' }
    }
  },

  async getUXPerformanceMetrics() {
    try {
      const response = await apiMethods.makeRequest('/api/enhanced/ux-performance', {
        method: 'GET'
      })
      return response
    } catch (error) {
      console.error('UX performance metrics error:', error)
      return { error: 'UX metrics unavailable' }
    }
  },

  async getPersonalizedRecommendations() {
    try {
      const response = await apiMethods.makeRequest('/api/enhanced/user-recommendations', {
        method: 'GET'
      })
      return response
    } catch (error) {
      console.error('Personalized recommendations error:', error)
      return { error: 'Recommendations unavailable' }
    }
  },

  async enhanceConversationQuality(conversationHistory, userContext = {}) {
    try {
      const response = await apiMethods.makeRequest('/api/enhanced/conversation-quality', {
        method: 'POST',
        body: JSON.stringify({
          conversation_history: conversationHistory,
          user_context: userContext
        })
      })
      return response
    } catch (error) {
      console.error('Conversation quality enhancement error:', error)
      return { error: 'Conversation enhancement unavailable' }
    }
  },

  async getFeatureDiscovery() {
    try {
      const response = await apiMethods.makeRequest('/api/enhanced/feature-discovery', {
        method: 'GET'
      })
      return response
    } catch (error) {
      console.error('Feature discovery error:', error)
      return { error: 'Feature discovery unavailable' }
    }
  },

  async testAllSystems() {
    try {
      const response = await apiMethods.makeRequest('/api/enhanced/test-all-systems', {
        method: 'POST'
      })
      return response
    } catch (error) {
      console.error('System testing error:', error)
      return { error: 'System testing unavailable' }
    }
  }
}

// Enhanced error handling for better user experience
const handleApiError = (error, fallbackMessage = 'An error occurred') => {
  console.error('API Error:', error)
  
  if (error.response) {
    const { status, data } = error.response
    switch (status) {
      case 429:
        return 'Rate limit exceeded. Please try again in a moment.'
      case 500:
        return data?.detail || 'Server error occurred'
      case 503:
        return 'Service temporarily unavailable'
      default:
        return data?.detail || fallbackMessage
    }
  } else if (error.request) {
    return 'Network error. Please check your connection.'
  } else {
    return error.message || fallbackMessage
  }
}

export { enhancedApiMethods, handleApiError }