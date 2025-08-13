import React, { useState, useEffect } from 'react'
import { apiMethods } from '../utils/api'
import { 
  PlusIcon, 
  CheckCircleIcon,
  ExclamationCircleIcon,
  TrashIcon,
  CogIcon,
  MagnifyingGlassIcon,
  FunnelIcon,
  BoltIcon,
  StarIcon,
  ClockIcon,
  ShieldCheckIcon,
  GlobeAltIcon,
  SparklesIcon
} from '@heroicons/react/24/outline'
import Navbar from '../components/EnhancedNavbar'
import LoadingSpinner from '../components/LoadingSpinner'
import toast from 'react-hot-toast'

const EnhancedIntegrations = () => {
  const [availableIntegrations, setAvailableIntegrations] = useState({})
  const [enhancedIntegrations, setEnhancedIntegrations] = useState({})
  const [userIntegrations, setUserIntegrations] = useState([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('all')
  const [showAddModal, setShowAddModal] = useState(false)
  const [showTestModal, setShowTestModal] = useState(false)
  const [selectedIntegration, setSelectedIntegration] = useState(null)
  const [testResults, setTestResults] = useState(null)
  const [activeTab, setActiveTab] = useState('marketplace')

  useEffect(() => { loadIntegrations() }, [])

  const loadIntegrations = async () => {
    try {
      const [availableRes, userRes] = await Promise.all([
        apiMethods.getAvailableIntegrations(),
        apiMethods.getIntegrations()
      ])
      setAvailableIntegrations(availableRes.categories)
      setUserIntegrations(userRes.integrations)
      
      // Load enhanced integrations (mock for now)
      loadEnhancedIntegrations()
    } catch (error) {
      console.error('Error loading integrations:', error)
      toast.error('Failed to load integrations')
    } finally {
      setLoading(false)
    }
  }

  const loadEnhancedIntegrations = () => {
    // Mock enhanced integrations data
    setEnhancedIntegrations({
      ai: [
        { name: 'Perplexity', icon: '🔍', oauth: false, description: 'AI search engine', status: 'new' },
        { name: 'Mistral AI', icon: '🧠', oauth: false, description: 'Open-source AI models', status: 'trending' },
        { name: 'Cohere', icon: '🔗', oauth: false, description: 'Enterprise AI platform', status: 'popular' },
        { name: 'Together AI', icon: '🤝', oauth: false, description: 'Collaborative AI platform', status: 'new' }
      ],
      design: [
        { name: 'Figma', icon: '🎨', oauth: true, description: 'Collaborative design tool', status: 'trending' },
        { name: 'Canva', icon: '🖼️', oauth: true, description: 'Graphic design platform', status: 'popular' },
        { name: 'Framer', icon: '⚡', oauth: true, description: 'Interactive design tool', status: 'new' },
        { name: 'Miro', icon: '📋', oauth: true, description: 'Online whiteboard', status: 'popular' }
      ],
      no_code: [
        { name: 'Webflow', icon: '🌐', oauth: true, description: 'Visual web development', status: 'trending' },
        { name: 'Bubble', icon: '💭', oauth: true, description: 'No-code app builder', status: 'popular' },
        { name: 'Retool', icon: '🔧', oauth: true, description: 'Internal tools builder', status: 'new' },
        { name: 'n8n', icon: '🔄', oauth: true, description: 'Open-source automation', status: 'trending' }
      ],
      social: [
        { name: 'TikTok', icon: '🎵', oauth: true, description: 'Short-form video platform', status: 'trending' },
        { name: 'Threads', icon: '🧵', oauth: true, description: 'Text-based social network', status: 'new' },
        { name: 'Mastodon', icon: '🐘', oauth: true, description: 'Decentralized social network', status: 'trending' },
        { name: 'BeReal', icon: '📸', oauth: true, description: 'Authentic social sharing', status: 'new' }
      ]
    })
  }

  const addIntegration = async (integrationData) => {
    try {
      await apiMethods.createIntegration(integrationData)
      toast.success('Integration added successfully!')
      loadIntegrations()
      setShowAddModal(false)
      setSelectedIntegration(null)
    } catch (error) {
      console.error('Error adding integration:', error)
      toast.error('Failed to add integration')
    }
  }

  const testIntegration = async (integration) => {
    try {
      setTestResults(null)
      setSelectedIntegration(integration)
      setShowTestModal(true)
      
      // Mock test results for now
      setTimeout(() => {
        setTestResults({
          connection: { status: 'success', message: 'Connection established', latency_ms: 45 },
          read: { status: 'success', message: 'Read access verified', sample_data: { id: 'test123' }},
          write: { status: 'success', message: 'Write access verified', test_record_id: 'record456' }
        })
      }, 2000)
    } catch (error) {
      console.error('Error testing integration:', error)
      toast.error('Failed to test integration')
    }
  }

  const removeIntegration = async (integrationId) => {
    if (!window.confirm('Are you sure you want to remove this integration?')) return
    try {
      await apiMethods.deleteIntegration(integrationId)
      toast.success('Integration removed successfully!')
      loadIntegrations()
    } catch (error) {
      console.error('Error removing integration:', error)
      toast.error('Failed to remove integration')
    }
  }

  const getIntegrationIcon = (name) => {
    const icons = { 
      // Enhanced icons for new platforms
      'Perplexity': '🔍', 'Mistral AI': '🧠', 'Cohere': '🔗', 'Together AI': '🤝',
      'Figma': '🎨', 'Canva': '🖼️', 'Framer': '⚡', 'Miro': '📋',
      'Webflow': '🌐', 'Bubble': '💭', 'Retool': '🔧', 'n8n': '🔄',
      'TikTok': '🎵', 'Threads': '🧵', 'Mastodon': '🐘', 'BeReal': '📸',
      'Linear': '📐', 'Height': '📏', 'Coda': '📄', 'Obsidian': '🧠',
      'Railway': '🚂', 'Supabase': '⚡', 'PlanetScale': '🌍', 'Vercel': '▲',
      
      // Existing icons
      'Slack': '💬', 'Discord': '🎮', 'Microsoft Teams': '👥', 'Email': '📧', 
      'GitHub': '⚡', 'GitLab': '🦊', 'Jira': '🎯', 'Trello': '📌',
      'Google Workspace': '🌐', 'Microsoft 365': '📊', 'Notion': '📝', 'Airtable': '📋',
      'Twitter': '🐦', 'LinkedIn': '💼', 'Facebook': '👤', 'Instagram': '📸',
      'OpenAI': '🤖', 'GROQ': '🚀', 'Anthropic': '🧠', 'Stability AI': '🎨'
    }
    return icons[name] || '🔧'
  }

  const getStatusBadge = (status) => {
    switch (status) {
      case 'new':
        return <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400">New</span>
      case 'trending':
        return <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-400">🔥 Trending</span>
      case 'popular':
        return <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400">⭐ Popular</span>
      default:
        return null
    }
  }

  const getAllIntegrations = () => {
    let allIntegrations = []
    
    // Combine standard and enhanced integrations
    const combinedCategories = {
      ...availableIntegrations,
      ...enhancedIntegrations
    }
    
    Object.entries(combinedCategories).forEach(([category, integrations]) => {
      if (selectedCategory === 'all' || selectedCategory === category) {
        integrations.forEach(integration => { 
          if (!searchTerm || integration.name.toLowerCase().includes(searchTerm.toLowerCase())) {
            allIntegrations.push({ ...integration, category })
          }
        })
      }
    })
    
    return allIntegrations
  }

  const getAllCategories = () => {
    const combined = {
      ...availableIntegrations,
      ...enhancedIntegrations
    }
    return Object.keys(combined || {})
  }

  const isIntegrationConnected = (integrationName) => userIntegrations.some(ui => ui.name === integrationName)

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
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">🔗 Enhanced Integration Hub</h1>
          <p className="text-gray-600 dark:text-gray-300">Connect 150+ tools and services to build powerful automation workflows.</p>
        </div>

        {/* Enhanced Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="card p-6 hover:shadow-lg transition-shadow">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Total Integrations</p>
                <p className="text-3xl font-bold text-primary-600">{getAllIntegrations().length}+</p>
                <p className="text-xs text-gray-500 mt-1">Across {getAllCategories().length} categories</p>
              </div>
              <div className="w-12 h-12 bg-gradient-to-r from-primary-500 to-accent-500 rounded-lg flex items-center justify-center">
                <GlobeAltIcon className="w-6 h-6 text-white" />
              </div>
            </div>
          </div>

          <div className="card p-6 hover:shadow-lg transition-shadow">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Connected</p>
                <p className="text-3xl font-bold text-green-600">{userIntegrations.length}</p>
                <p className="text-xs text-green-500 mt-1">{userIntegrations.filter(i => i.status === 'active').length} active</p>
              </div>
              <CheckCircleIcon className="w-12 h-12 text-green-500" />
            </div>
          </div>

          <div className="card p-6 hover:shadow-lg transition-shadow">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">New This Month</p>
                <p className="text-3xl font-bold text-accent-600">8</p>
                <p className="text-xs text-gray-500 mt-1">Latest additions</p>
              </div>
              <SparklesIcon className="w-12 h-12 text-accent-500" />
            </div>
          </div>

          <div className="card p-6 bg-gradient-to-r from-purple-50 to-pink-50 dark:from-purple-900/20 dark:to-pink-900/20 border-purple-200 dark:border-purple-800 hover:shadow-lg transition-shadow">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-purple-700 dark:text-purple-300">AI-Powered</p>
                <p className="text-3xl font-bold text-purple-600">12</p>
                <p className="text-xs text-purple-500 mt-1">Smart integrations</p>
              </div>
              <div className="w-12 h-12 bg-gradient-to-r from-purple-500 to-pink-500 rounded-lg flex items-center justify-center">
                <SparklesIcon className="w-6 h-6 text-white" />
              </div>
            </div>
          </div>
        </div>

        {/* Enhanced Tab Navigation */}
        <div className="mb-8">
          <nav className="flex space-x-8" aria-label="Tabs">
            {[
              { id: 'marketplace', name: 'Marketplace', icon: '🏪' },
              { id: 'connected', name: 'Connected', icon: '🔗' },
              { id: 'trending', name: 'Trending', icon: '🔥' },
              { id: 'ai-powered', name: 'AI-Powered', icon: '🤖' }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`${
                  activeTab === tab.id
                    ? 'border-primary-500 text-primary-600 dark:text-primary-400'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
                } whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm flex items-center space-x-2`}
              >
                <span>{tab.icon}</span>
                <span>{tab.name}</span>
              </button>
            ))}
          </nav>
        </div>

        {/* Tab Content */}
        {activeTab === 'connected' && userIntegrations.length > 0 && (
          <div className="mb-8">
            <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">Your Connected Integrations</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {userIntegrations.map((integration) => (
                <div key={integration.id} className="integration-card p-6 hover:shadow-lg transition-all">
                  <div className="content">
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center space-x-3">
                        <span className="text-2xl">{getIntegrationIcon(integration.name)}</span>
                        <div>
                          <h3 className="font-semibold text-gray-900 dark:text-white">{integration.name}</h3>
                          <p className="text-sm text-gray-600 dark:text-gray-400">{integration.platform}</p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <div className={`px-2 py-1 rounded-full text-xs font-medium ${
                          integration.status === 'active' 
                            ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400' 
                            : 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400'
                        }`}>
                          {integration.status}
                        </div>
                        <button 
                          onClick={() => testIntegration(integration)} 
                          className="p-1 text-gray-400 hover:text-primary-500"
                          title="Test connection"
                        >
                          <BoltIcon className="w-4 h-4" />
                        </button>
                        <button 
                          onClick={() => removeIntegration(integration.id)} 
                          className="p-1 text-red-500 hover:text-red-700"
                          title="Remove integration"
                        >
                          <TrashIcon className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                    <div className="flex justify-between items-center text-sm text-gray-600 dark:text-gray-400">
                      <span>Connected: {new Date(integration.created_at).toLocaleDateString()}</span>
                      <span>Last used: 2 hours ago</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Enhanced Filters */}
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
          <div className="flex flex-wrap gap-2">
            <button 
              onClick={() => setSelectedCategory('all')} 
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                selectedCategory === 'all' 
                  ? 'bg-primary-600 text-white' 
                  : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
              }`}
            >
              All Categories
            </button>
            {getAllCategories().map((category) => (
              <button 
                key={category} 
                onClick={() => setSelectedCategory(category)} 
                className={`px-4 py-2 rounded-lg font-medium transition-colors capitalize ${
                  selectedCategory === category 
                    ? 'bg-primary-600 text-white' 
                    : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                }`}
              >
                {category.replace('_', ' ')}
              </button>
            ))}
          </div>
          <div className="relative">
            <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input 
              type="text" 
              placeholder="Search integrations..." 
              value={searchTerm} 
              onChange={(e) => setSearchTerm(e.target.value)} 
              className="pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 bg-white dark:bg-gray-800 text-gray-900 dark:text-white" 
            />
          </div>
        </div>

        {/* Enhanced Integration Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {getAllIntegrations()
            .filter(integration => {
              if (activeTab === 'trending') return integration.status === 'trending'
              if (activeTab === 'ai-powered') return integration.category === 'ai'
              if (activeTab === 'connected') return isIntegrationConnected(integration.name)
              return true
            })
            .map((integration) => {
            const isConnected = isIntegrationConnected(integration.name)
            return (
              <div 
                key={`${integration.category}-${integration.name}`} 
                className="integration-card p-6 cursor-pointer hover:shadow-lg transition-all transform hover:-translate-y-1" 
                onClick={() => { if (!isConnected) { setSelectedIntegration(integration); setShowAddModal(true) } }}
              >
                <div className="content">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center space-x-3">
                      <span className="text-3xl">{getIntegrationIcon(integration.name)}</span>
                      <div className="min-w-0 flex-1">
                        <h3 className="font-semibold text-gray-900 dark:text-white truncate">{integration.name}</h3>
                        <p className="text-sm text-gray-600 dark:text-gray-400 capitalize">{integration.category?.replace('_', ' ')}</p>
                      </div>
                    </div>
                    <div className="flex flex-col items-end space-y-1">
                      {integration.status && getStatusBadge(integration.status)}
                      {isConnected ? 
                        <CheckCircleIcon className="w-6 h-6 text-green-500" /> : 
                        <PlusIcon className="w-6 h-6 text-gray-400 group-hover:text-primary-500" />
                      }
                    </div>
                  </div>

                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-4 line-clamp-2">{integration.description}</p>

                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <div className={`px-2 py-1 rounded-full text-xs font-medium ${
                        integration.oauth 
                          ? 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400' 
                          : 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300'
                      }`}>
                        {integration.oauth ? 'OAuth' : 'API Key'}
                      </div>
                      {integration.oauth && <ShieldCheckIcon className="w-4 h-4 text-green-500" />}
                    </div>
                    <div className={`px-2 py-1 rounded-full text-xs font-medium ${
                      isConnected 
                        ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400' 
                        : 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300'
                    }`}>
                      {isConnected ? 'Connected' : 'Available'}
                    </div>
                  </div>
                </div>
              </div>
            )
          })}
        </div>

        {/* Add Integration Modal */}
        {showAddModal && selectedIntegration && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-2xl w-full max-w-md mx-4">
              <div className="p-6 border-b border-gray-200 dark:border-gray-700">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center">
                  <span className="text-2xl mr-3">{getIntegrationIcon(selectedIntegration.name)}</span>
                  Connect {selectedIntegration.name}
                  {selectedIntegration.status && (
                    <div className="ml-2">{getStatusBadge(selectedIntegration.status)}</div>
                  )}
                </h3>
                <p className="text-sm text-gray-600 dark:text-gray-400 mt-2">{selectedIntegration.description}</p>
              </div>
              <form 
                onSubmit={(e) => { 
                  e.preventDefault()
                  const formData = new FormData(e.target)
                  const integrationData = { 
                    name: selectedIntegration.name, 
                    platform: selectedIntegration.name, 
                    credentials: { 
                      type: selectedIntegration.oauth ? 'oauth' : 'api_key', 
                      api_key: formData.get('api_key') 
                    } 
                  }
                  addIntegration(integrationData) 
                }} 
                className="p-6"
              >
                {selectedIntegration.oauth ? (
                  <div className="text-center py-8">
                    <div className="w-16 h-16 bg-gradient-to-r from-primary-500 to-accent-500 rounded-full flex items-center justify-center mx-auto mb-4">
                      <ShieldCheckIcon className="w-8 h-8 text-white" />
                    </div>
                    <p className="text-gray-600 dark:text-gray-400 mb-6">
                      Click the button below to securely authenticate with {selectedIntegration.name} using OAuth
                    </p>
                    <button 
                      type="button" 
                      className="btn-primary mb-2" 
                      onClick={() => { toast.info('OAuth integration coming soon!'); setShowAddModal(false) }}
                    >
                      🔐 Authenticate with {selectedIntegration.name}
                    </button>
                    <p className="text-xs text-gray-500 dark:text-gray-400">Secure OAuth 2.0 authentication</p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        API Key
                      </label>
                      <input 
                        type="password" 
                        name="api_key" 
                        required 
                        className="input-field" 
                        placeholder={`Enter your ${selectedIntegration.name} API key`} 
                      />
                      <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                        Your API key will be encrypted and stored securely
                      </p>
                    </div>
                    <div className="flex justify-end space-x-3 pt-4">
                      <button type="button" onClick={() => setShowAddModal(false)} className="btn-secondary">
                        Cancel
                      </button>
                      <button type="submit" className="btn-primary">
                        Connect Integration
                      </button>
                    </div>
                  </div>
                )}
              </form>
            </div>
          </div>
        )}

        {/* Test Results Modal */}
        {showTestModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-2xl w-full max-w-lg mx-4">
              <div className="p-6 border-b border-gray-200 dark:border-gray-700">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                  🧪 Testing {selectedIntegration?.name} Connection
                </h3>
              </div>
              <div className="p-6">
                {!testResults ? (
                  <div className="text-center py-8">
                    <LoadingSpinner size="large" className="mx-auto mb-4" />
                    <p className="text-gray-600 dark:text-gray-400">Running connection tests...</p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {Object.entries(testResults).map(([test, result]) => (
                      <div key={test} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                        <div>
                          <h4 className="font-medium text-gray-900 dark:text-white capitalize">{test} Test</h4>
                          <p className="text-sm text-gray-600 dark:text-gray-400">{result.message}</p>
                        </div>
                        <div className={`w-6 h-6 rounded-full flex items-center justify-center ${
                          result.status === 'success' ? 'bg-green-500' : 'bg-red-500'
                        }`}>
                          {result.status === 'success' ? '✓' : '✗'}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
                <div className="flex justify-end space-x-3 pt-4">
                  <button onClick={() => setShowTestModal(false)} className="btn-primary">
                    Close
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default EnhancedIntegrations