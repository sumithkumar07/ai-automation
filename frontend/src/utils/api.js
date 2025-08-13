import axios from 'axios'
import toast from 'react-hot-toast'

// Create axios instance with base configuration
const api = axios.create({
  baseURL: import.meta.env.VITE_BACKEND_URL || 'http://localhost:8001',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    
    // Add request ID for tracking
    config.headers['X-Request-ID'] = Math.random().toString(36).substr(2, 9)
    
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor to handle errors globally
api.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    // Handle different error scenarios
    if (error.response) {
      const { status, data } = error.response
      
      switch (status) {
        case 401:
          // Unauthorized - clear auth and redirect to login
          localStorage.removeItem('token')
          localStorage.removeItem('user')
          delete axios.defaults.headers.common['Authorization']
          // Use React Router for navigation instead of hard redirect
          if (typeof window !== 'undefined' && window.location.pathname !== '/auth') {
            window.location.pathname = '/auth'
          }
          break
          
        case 403:
          toast.error('Access forbidden')
          break
          
        case 429:
          // Rate limited
          const retryAfter = error.response.headers['retry-after']
          toast.error(`Rate limit exceeded. Please try again in ${retryAfter || 60} seconds.`)
          break
          
        case 500:
          toast.error(data?.detail || 'Server error occurred')
          break
          
        default:
          toast.error(data?.detail || `Error: ${status}`)
      }
    } else if (error.request) {
      // Network error
      toast.error('Network error. Please check your connection.')
    } else {
      // Something else happened
      toast.error('An unexpected error occurred')
    }
    
    return Promise.reject(error)
  }
)

// API methods with enhanced error handling
export const apiMethods = {
  // Auth
  async login(email, password) {
    const response = await api.post('/api/auth/login', { email, password })
    return response.data
  },

  async signup(name, email, password) {
    const response = await api.post('/api/auth/signup', { name, email, password })
    return response.data
  },

  // Dashboard
  async getDashboardStats() {
    const response = await api.get('/api/dashboard/stats')
    return response.data
  },

  async getUserChecklist() {
    const response = await api.get('/api/user/checklist')
    return response.data
  },

  // Workflows
  async getWorkflows(page = 1, limit = 20) {
    const response = await api.get(`/api/workflows?page=${page}&limit=${limit}`)
    return response.data
  },

  async createWorkflow(workflowData) {
    const response = await api.post('/api/workflows', workflowData)
    return response.data
  },

  async getWorkflow(workflowId) {
    const response = await api.get(`/api/workflows/${workflowId}`)
    return response.data
  },

  async updateWorkflow(workflowId, workflowData) {
    const response = await api.put(`/api/workflows/${workflowId}`, workflowData)
    return response.data
  },

  async deleteWorkflow(workflowId) {
    const response = await api.delete(`/api/workflows/${workflowId}`)
    return response.data
  },

  async autosaveWorkflow(workflowId, workflowData) {
    const response = await api.post(`/api/workflows/${workflowId}/autosave`, workflowData)
    return response.data
  },

  async executeWorkflow(workflowId, idempotencyKey = null) {
    const headers = {}
    if (idempotencyKey) {
      headers['idempotency-key'] = idempotencyKey
    }
    const response = await api.post(`/api/workflows/${workflowId}/execute`, {}, { headers })
    return response.data
  },

  // Integrations
  async getIntegrations(page = 1, limit = 20) {
    const response = await api.get(`/api/integrations?page=${page}&limit=${limit}`)
    return response.data
  },

  async getAvailableIntegrations() {
    const response = await api.get('/api/integrations/available')
    return response.data
  },

  async createIntegration(integrationData) {
    const response = await api.post('/api/integrations', integrationData)
    return response.data
  },

  async deleteIntegration(integrationId) {
    const response = await api.delete(`/api/integrations/${integrationId}`)
    return response.data
  },

  // =======================================
  // ENHANCEMENT FEATURES API METHODS - ALL PHASES
  // =======================================
  
  // Feature Management
  async getEnhancementFeatures() {
    const response = await api.get('/api/enhanced/features/available')
    return response.data
  },

  async updateEnhancementPreference(data) {
    const response = await api.post('/api/enhanced/features/preference', data)
    return response.data
  },

  // Phase 2: AI Intelligence & Automation
  async getAIInsights() {
    const response = await api.get('/api/enhanced/ai/dashboard-insights')
    return response.data
  },

  async getSmartSuggestions() {
    const response = await api.post('/api/enhanced/ai/smart-suggestions')
    return response.data
  },

  async generateAIWorkflow(prompt, complexity = 'intermediate', category = 'general') {
    const response = await api.post('/api/enhanced/ai/generate-workflow', {
      prompt,
      complexity,
      category
    })
    return response.data
  },

  async optimizeWorkflowWithAI(workflowId) {
    const response = await api.post(`/api/enhanced/ai/optimize-workflow/${workflowId}`)
    return response.data
  },

  // Phase 3: Enterprise Collaboration & Scale
  async getUserWorkspaces(organizationId = null) {
    const params = organizationId ? `?organization_id=${organizationId}` : ''
    const response = await api.get(`/api/enhanced/collaboration/workspaces${params}`)
    return response.data
  },

  async createTeamWorkspace(data) {
    const response = await api.post('/api/enhanced/collaboration/workspaces', data)
    return response.data
  },

  async getWorkspaceActivity(workspaceId, limit = 50) {
    const response = await api.get(`/api/enhanced/collaboration/workspaces/${workspaceId}/activity?limit=${limit}`)
    return response.data
  },

  async getWorkspaceAnalytics(workspaceId) {
    const response = await api.get(`/api/enhanced/collaboration/workspaces/${workspaceId}/analytics`)
    return response.data
  },

  // Phase 4: Next-Generation Platform Features
  async getAdvancedAnalytics(options = {}) {
    const response = await api.post('/api/enhanced/analytics/advanced', {
      time_range: options.time_range || '30d',
      metrics: options.metrics || [],
      include_predictions: options.include_predictions || false
    })
    return response.data
  },

  async getBusinessIntelligence() {
    const response = await api.get('/api/enhanced/analytics/business-intelligence')
    return response.data
  },

  // Phase 5: Innovation & Future Technologies
  async getFutureTechCapabilities() {
    const response = await api.get('/api/enhanced/future-tech/capabilities')
    return response.data
  },

  async getIoTIntegrationInfo() {
    const response = await api.get('/api/enhanced/future-tech/iot-devices')
    return response.data
  },

  async getBlockchainVerificationInfo() {
    const response = await api.get('/api/enhanced/future-tech/blockchain-verification')
    return response.data
  },

  async getQuantumProcessingInfo() {
    const response = await api.get('/api/enhanced/future-tech/quantum-processing')
    return response.data
  },

  // System Status
  async getEnhancementSystemStatus() {
    const response = await api.get('/api/enhanced/system/status')
    return response.data
  },

  async getEnhancementHealthCheck() {
    const response = await api.get('/api/enhanced/system/health')
    return response.data
  },

  // AI
  async chatWithAI(message, sessionId = null) {
    const response = await api.post('/api/ai/chat', { message, session_id: sessionId })
    return response.data
  },

  async generateWorkflow(prompt, structured = false, sessionId = null) {
    const response = await api.post('/api/ai/generate-workflow', { 
      prompt, 
      structured, 
      session_id: sessionId 
    })
    return response.data
  },

  // Nodes and Templates
  async getNodeTypes() {
    const response = await api.get('/api/nodes')
    return response.data
  },

  async getTemplates() {
    const response = await api.get('/api/templates')
    return response.data
  },

  async searchTemplates(query = '', category = '', difficulty = '') {
    const response = await api.get(`/api/templates/search?query=${query}&category=${category}&difficulty=${difficulty}`)
    return response.data
  },

  async deployTemplate(templateId) {
    const response = await api.post(`/api/templates/${templateId}/deploy`)
    return response.data
  },

  // Executions
  async getExecutionStatus(executionId) {
    const response = await api.get(`/api/executions/${executionId}`)
    return response.data
  },

  // Health
  async getHealth() {
    const response = await api.get('/api/health')
    return response.data
  }
}

export default api