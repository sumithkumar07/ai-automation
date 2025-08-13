// 🚀 ENHANCED API CLIENT
// Zero UI disruption - Pure backend integration layer

import api from './api'

class EnhancedApiClient {
  constructor() {
    this.baseClient = api
    this.enhancementsAvailable = false
    this.systemStatus = null
    this.checkEnhancementsAvailability()
  }

  async checkEnhancementsAvailability() {
    try {
      const response = await this.baseClient.get('/api/enhanced/system-status')
      this.enhancementsAvailable = response.data?.overall_status === 'fully_operational'
      this.systemStatus = response.data
      console.log('✅ Enhanced systems available:', this.enhancementsAvailable)
    } catch (error) {
      this.enhancementsAvailable = false
      console.log('ℹ️ Enhanced systems not available, using standard features')
    }
  }

  // =======================================
  // 🤖 MULTI-AGENT AI METHODS
  // =======================================

  async startMultiAgentConversation(message, sessionId = null) {
    if (!this.enhancementsAvailable) {
      // Fallback to regular AI chat
      return this.baseClient.post('/api/ai/chat', { message })
    }

    try {
      const response = await this.baseClient.post('/api/ai/multi-agent/conversation', {
        message,
        session_id: sessionId
      })
      
      return {
        ...response.data,
        enhanced: true,
        fallback: false
      }
    } catch (error) {
      // Graceful fallback
      console.warn('Multi-agent conversation failed, using fallback:', error)
      const fallbackResponse = await this.baseClient.post('/api/ai/chat', { message })
      return {
        ...fallbackResponse.data,
        enhanced: false,
        fallback: true
      }
    }
  }

  async enhanceConversation(conversationHistory, userContext = {}) {
    if (!this.enhancementsAvailable) {
      return { enhanced: false, message: 'Enhancement not available' }
    }

    try {
      const response = await this.baseClient.post('/api/ai/enhance-conversation', {
        conversation_history: conversationHistory,
        user_context: userContext
      })
      return response.data
    } catch (error) {
      console.warn('Conversation enhancement failed:', error)
      return { enhanced: false, error: error.message }
    }
  }

  // =======================================
  // 🔗 ENHANCED INTEGRATIONS METHODS
  // =======================================

  async getEnhancedIntegrations() {
    if (!this.enhancementsAvailable) {
      // Fallback to regular integrations
      return this.baseClient.get('/api/integrations')
    }

    try {
      const [enhancedResponse, regularResponse] = await Promise.allSettled([
        this.baseClient.get('/api/integrations/enhanced/all'),
        this.baseClient.get('/api/integrations')
      ])

      if (enhancedResponse.status === 'fulfilled') {
        return {
          ...enhancedResponse.value.data,
          enhanced: true,
          legacy_count: regularResponse.status === 'fulfilled' ? 
            regularResponse.value.data?.integrations?.length || 0 : 0
        }
      }

      // Fallback to regular integrations
      return regularResponse.status === 'fulfilled' ? 
        { ...regularResponse.value.data, enhanced: false } : 
        { integrations: [], enhanced: false }

    } catch (error) {
      console.warn('Enhanced integrations failed, using fallback:', error)
      return this.baseClient.get('/api/integrations')
    }
  }

  async searchEnhancedIntegrations(query, category = null) {
    if (!this.enhancementsAvailable) {
      // Basic filtering on regular integrations
      const integrations = await this.baseClient.get('/api/integrations')
      const filtered = integrations.data.integrations?.filter(integration => 
        integration.name.toLowerCase().includes(query.toLowerCase())
      ) || []
      return { results: filtered, enhanced: false }
    }

    try {
      const response = await this.baseClient.get('/api/integrations/enhanced/search', {
        params: { query, category }
      })
      return { ...response.data, enhanced: true }
    } catch (error) {
      console.warn('Enhanced integration search failed:', error)
      return { results: [], enhanced: false, error: error.message }
    }
  }

  // =======================================
  // ⚡ PERFORMANCE MONITORING METHODS
  // =======================================

  async recordWebVitals(vitalsData) {
    if (!this.enhancementsAvailable) {
      // Just log to console if enhancements not available
      console.log('Web Vitals (not recorded):', vitalsData)
      return { recorded: false, reason: 'enhancements_not_available' }
    }

    try {
      const response = await this.baseClient.post('/api/performance/web-vitals/record', vitalsData)
      return { ...response.data, recorded: true }
    } catch (error) {
      console.warn('Web Vitals recording failed:', error)
      return { recorded: false, error: error.message }
    }
  }

  async getPerformanceReport() {
    if (!this.enhancementsAvailable) {
      return { 
        available: false, 
        message: 'Enhanced performance monitoring not available' 
      }
    }

    try {
      const response = await this.baseClient.get('/api/performance/enhanced-report')
      return { ...response.data, available: true }
    } catch (error) {
      console.warn('Performance report failed:', error)
      return { available: false, error: error.message }
    }
  }

  // =======================================
  // 🎨 ACCESSIBILITY METHODS
  // =======================================

  async getAccessibilityAnalysis() {
    if (!this.enhancementsAvailable) {
      return { 
        available: false, 
        message: 'Enhanced accessibility analysis not available' 
      }
    }

    try {
      const response = await this.baseClient.get('/api/accessibility/compliance-analysis')
      return { ...response.data, available: true }
    } catch (error) {
      console.warn('Accessibility analysis failed:', error)
      return { available: false, error: error.message }
    }
  }

  async updateAccessibilityPreferences(preferences) {
    if (!this.enhancementsAvailable) {
      // Store in localStorage as fallback
      localStorage.setItem('accessibility_preferences', JSON.stringify(preferences))
      return { updated: false, stored_locally: true }
    }

    try {
      const response = await this.baseClient.post('/api/accessibility/preferences', preferences)
      return { ...response.data, updated: true }
    } catch (error) {
      console.warn('Accessibility preferences update failed:', error)
      // Fallback to localStorage
      localStorage.setItem('accessibility_preferences', JSON.stringify(preferences))
      return { updated: false, stored_locally: true, error: error.message }
    }
  }

  async getAccessibilityQuickFixes() {
    if (!this.enhancementsAvailable) {
      return { available: false, fixes: [] }
    }

    try {
      const response = await this.baseClient.get('/api/accessibility/quick-fixes')
      return { ...response.data, available: true }
    } catch (error) {
      console.warn('Accessibility quick fixes failed:', error)
      return { available: false, fixes: [], error: error.message }
    }
  }

  // =======================================
  // 🔧 UTILITY METHODS
  // =======================================

  getSystemStatus() {
    return {
      enhancementsAvailable: this.enhancementsAvailable,
      systemStatus: this.systemStatus,
      capabilities: {
        multiAgentAI: this.enhancementsAvailable,
        enhancedIntegrations: this.enhancementsAvailable,
        performanceMonitoring: this.enhancementsAvailable,
        accessibilityCompliance: this.enhancementsAvailable,
        webVitalsOptimization: this.enhancementsAvailable
      }
    }
  }

  async testEnhancementsConnection() {
    try {
      await this.checkEnhancementsAvailability()
      return {
        connected: this.enhancementsAvailable,
        status: this.systemStatus,
        timestamp: new Date().toISOString()
      }
    } catch (error) {
      return {
        connected: false,
        error: error.message,
        timestamp: new Date().toISOString()
      }
    }
  }

  // =======================================
  // 📊 ENHANCED DASHBOARD METHODS
  // =======================================

  async getEnhancedDashboardData() {
    if (!this.enhancementsAvailable) {
      // Return regular dashboard data
      return this.baseClient.get('/api/dashboard/stats')
    }

    try {
      // Get both regular and enhanced data
      const [regularData, enhancedData] = await Promise.allSettled([
        this.baseClient.get('/api/dashboard/stats'),
        Promise.all([
          this.getPerformanceReport(),
          this.getAccessibilityAnalysis(),
          this.baseClient.get('/api/ai/multi-agent/performance').catch(() => null)
        ])
      ])

      const baseData = regularData.status === 'fulfilled' ? regularData.value.data : {}
      
      if (enhancedData.status === 'fulfilled') {
        const [performanceReport, accessibilityAnalysis, aiPerformance] = enhancedData.value
        
        return {
          ...baseData,
          enhanced_features: {
            performance_report: performanceReport,
            accessibility_analysis: accessibilityAnalysis,
            ai_performance: aiPerformance,
            system_status: this.systemStatus
          },
          enhanced: true
        }
      }

      return { ...baseData, enhanced: false }

    } catch (error) {
      console.warn('Enhanced dashboard data failed:', error)
      return this.baseClient.get('/api/dashboard/stats')
    }
  }
}

// Create singleton instance
export const enhancedApiClient = new EnhancedApiClient()

// Export for use in components
export default enhancedApiClient