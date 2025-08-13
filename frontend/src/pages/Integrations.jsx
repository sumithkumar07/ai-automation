import React, { useState, useEffect } from 'react'
import { apiMethods } from '../utils/api'
import { 
  PlusIcon, 
  CheckCircleIcon,
  ExclamationCircleIcon,
  TrashIcon,
  CogIcon,
  MagnifyingGlassIcon,
  FunnelIcon
} from '@heroicons/react/24/outline'
import Navbar from '../components/Navbar'
import LoadingSpinner from '../components/LoadingSpinner'
import toast from 'react-hot-toast'

const Integrations = () => {
  const [availableIntegrations, setAvailableIntegrations] = useState({})
  const [userIntegrations, setUserIntegrations] = useState([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('all')
  const [showAddModal, setShowAddModal] = useState(false)
  const [selectedIntegration, setSelectedIntegration] = useState(null)

  useEffect(() => { loadIntegrations() }, [])

  const loadIntegrations = async () => {
    try {
      const [availableRes, userRes] = await Promise.all([
        apiMethods.getAvailableIntegrations(),
        apiMethods.getIntegrations()
      ])
      setAvailableIntegrations(availableRes.categories)
      setUserIntegrations(userRes.integrations)
    } catch (error) {
      console.error('Error loading integrations:', error)
      toast.error('Failed to load integrations')
    } finally {
      setLoading(false)
    }
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
      // Communication (18)
      'Slack': '💬', 'Discord': '🎮', 'Microsoft Teams': '👥', 'Email': '📧', 
      'WhatsApp Business': '📱', 'Telegram': '✈️', 'Signal': '🔒', 'Zoom': '📹',
      'Twilio': '📞', 'SendGrid': '📨', 'Vonage': '☎️', 'RingCentral': '📳',
      'Webex': '💼', 'Mattermost': '💬', 'Rocket.Chat': '🚀', 'IRC': '💻',
      'Matrix': '🔗', 'Gitter': '🗨️',
      
      // Productivity (16) 
      'Google Workspace': '🌐', 'Microsoft 365': '📊', 'Notion': '📝', 'Airtable': '📋',
      'Asana': '📌', 'Monday.com': '📅', 'ClickUp': '✅', 'Todoist': '✔️',
      'Evernote': '📓', 'OneNote': '📔', 'Basecamp': '🏕️', 'Wrike': '📈',
      'Smartsheet': '📊', 'Coda': '📄', 'Confluence': '🌊', 'Calendly': '🗓️',
      
      // Social (12)
      'Twitter': '🐦', 'LinkedIn': '💼', 'Facebook': '👤', 'Instagram': '📸',
      'YouTube': '📺', 'TikTok': '🎵', 'Pinterest': '📌', 'Reddit': '🤖',
      'Snapchat': '👻', 'Mastodon': '🐘', 'Buffer': '📡', 'Hootsuite': '🦉',
      
      // Development (20)
      'GitHub': '⚡', 'GitLab': '🦊', 'Jira': '🎯', 'Trello': '📌',
      'Bitbucket': '🪣', 'Azure DevOps': '☁️', 'Jenkins': '🔧', 'CircleCI': '⭕',
      'Travis CI': '🟢', 'Docker Hub': '🐳', 'Kubernetes': '☸️', 'Vercel': '▲',
      'Netlify': '🌐', 'Heroku': '🟣', 'Figma': '🎨', 'Linear': '📐',
      'Sentry': '🚨', 'PagerDuty': '📟', 'New Relic': '📊', 'Datadog': '🐕',
      
      // AI (12)
      'OpenAI': '🤖', 'GROQ': '🚀', 'Anthropic': '🧠', 'Stability AI': '🎨',
      'Hugging Face': '🤗', 'Cohere': '🔗', 'Replicate': '🔄', 'Google AI': '🔍',
      'AWS Bedrock': '🏔️', 'Azure OpenAI': '💙', 'IBM Watson': '🔬', 'Midjourney': '🎭',
      
      // E-commerce (10)
      'Shopify': '🛍️', 'WooCommerce': '🛒', 'Stripe': '💳', 'PayPal': '💰',
      'Square': '⬜', 'BigCommerce': '🏪', 'Magento': '🛒', 'Amazon Seller': '📦',
      'eBay': '🔨', 'Etsy': '🎨',
      
      // CRM & Sales (10)
      'Salesforce': '☁️', 'HubSpot': '🧲', 'Pipedrive': '📊', 'Zoho CRM': '📈',
      'Close': '🎯', 'Copper': '🟤', 'Freshsales': '🌱', 'ActiveCampaign': '📧',
      'Intercom': '💬', 'Zendesk': '🎫',
      
      // Marketing (10)
      'Mailchimp': '🐵', 'ConvertKit': '📬', 'Google Ads': '🎯', 'Facebook Ads': '📢',
      'Klaviyo': '📈', 'Campaign Monitor': '📊', 'Constant Contact': '📞', 'GetResponse': '📧',
      'Drip': '💧', 'AWeber': '✉️',
      
      // Analytics (8)
      'Google Analytics': '📊', 'Mixpanel': '📈', 'Segment': '📐', 'Hotjar': '🔥',
      'Amplitude': '〰️', 'Heap': '📚', 'Kissmetrics': '💋', 'Adobe Analytics': '🎨',
      
      // Cloud Storage (8)
      'AWS S3': '☁️', 'Google Drive': '💾', 'Dropbox': '📦', 'OneDrive': '💽',
      'Box': '📦', 'iCloud': '☁️', 'pCloud': '☁️', 'Azure Blob Storage': '🟦',
      
      // DevOps (10)
      'Docker': '🐳', 'Kubernetes': '☸️', 'AWS': '☁️', 'Google Cloud': '☁️',
      'Azure': '🟦', 'Terraform': '🏗️', 'Ansible': '🔧', 'Chef': '👨‍🍳',
      'Puppet': '🎭', 'Vagrant': '📦'
    }
    return icons[name] || '🔧'
  }

  const filteredIntegrations = () => {
    let allIntegrations = []
    Object.entries(availableIntegrations).forEach(([category, integrations]) => {
      if (selectedCategory === 'all' || selectedCategory === category) {
        integrations.forEach(integration => { allIntegrations.push({ ...integration, category }) })
      }
    })
    if (searchTerm) {
      allIntegrations = allIntegrations.filter(integration => integration.name.toLowerCase().includes(searchTerm.toLowerCase()))
    }
    return allIntegrations
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
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Integration Hub</h1>
          <p className="text-gray-600">Connect your favorite tools and services to build powerful automation workflows.</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="card p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Available Integrations</p>
                <p className="text-3xl font-bold text-primary-600">{Object.values(availableIntegrations).flat().length}+</p>
                <p className="text-xs text-gray-500 mt-1">Across 11 categories</p>
              </div>
              <div className="w-12 h-12 bg-gradient-to-r from-primary-500 to-accent-500 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">120+</span>
              </div>
            </div>
          </div>

          <div className="card p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Connected</p>
                <p className="text-3xl font-bold text-green-600">{userIntegrations.length}</p>
                <p className="text-xs text-green-500 mt-1">{userIntegrations.filter(i => i.status === 'active').length} active</p>
              </div>
              <CheckCircleIcon className="w-12 h-12 text-green-500" />
            </div>
          </div>

          <div className="card p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Categories</p>
                <p className="text-3xl font-bold text-accent-600">{Object.keys(availableIntegrations).length}</p>
                <p className="text-xs text-gray-500 mt-1">Business & Tech</p>
              </div>
              <FunnelIcon className="w-12 h-12 text-accent-500" />
            </div>
          </div>

          <div className="card p-6 bg-gradient-to-r from-purple-50 to-pink-50 border-purple-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-purple-700">Enterprise Ready</p>
                <p className="text-3xl font-bold text-purple-600">27</p>
                <p className="text-xs text-purple-500 mt-1">Premium integrations</p>
              </div>
              <div className="w-12 h-12 bg-gradient-to-r from-purple-500 to-pink-500 rounded-lg flex items-center justify-center">
                <span className="text-white text-xs font-bold">Pro</span>
              </div>
            </div>
          </div>
        </div>

        {userIntegrations.length > 0 && (
          <div className="mb-8">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Your Connected Integrations</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {userIntegrations.map((integration) => (
                <div key={integration.id} className="integration-card p-6">
                  <div className="content">
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center space-x-3">
                        <span className="text-2xl">{getIntegrationIcon(integration.name)}</span>
                        <div>
                          <h3 className="font-semibold text-gray-900">{integration.name}</h3>
                          <p className="text-sm text-gray-600">{integration.platform}</p>
                        </div>
                      </div>
                      <div className={`px-2 py-1 rounded-full text-xs font-medium ${integration.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                        {integration.status}
                      </div>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Connected: {new Date(integration.created_at).toLocaleDateString()}</span>
                      <button onClick={() => removeIntegration(integration.id)} className="text-red-500 hover:text-red-700 p-1">
                        <TrashIcon className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
          <div className="flex flex-wrap gap-2">
            <button onClick={() => setSelectedCategory('all')} className={`px-4 py-2 rounded-lg font-medium transition-colors ${selectedCategory === 'all' ? 'bg-primary-600 text-white' : 'bg-white text-gray-700 hover:bg-gray-100'}`}>All Categories</button>
            {Object.keys(availableIntegrations).map((category) => (
              <button key={category} onClick={() => setSelectedCategory(category)} className={`px-4 py-2 rounded-lg font-medium transition-colors capitalize ${selectedCategory === category ? 'bg-primary-600 text-white' : 'bg-white text-gray-700 hover:bg-gray-100'}`}>
                {category.replace('_', ' ')}
              </button>
            ))}
          </div>
          <div className="relative">
            <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input type="text" placeholder="Search integrations..." value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500" />
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {filteredIntegrations().map((integration) => {
            const isConnected = isIntegrationConnected(integration.name)
            return (
              <div key={`${integration.category}-${integration.name}`} className="integration-card p-6 cursor-pointer" onClick={() => { if (!isConnected) { setSelectedIntegration(integration); setShowAddModal(true) } }}>
                <div className="content">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center space-x-3">
                      <span className="text-3xl">{getIntegrationIcon(integration.name)}</span>
                      <div>
                        <h3 className="font-semibold text-gray-900">{integration.name}</h3>
                        <p className="text-sm text-gray-600 capitalize">{integration.category.replace('_', ' ')}</p>
                      </div>
                    </div>
                    {isConnected ? (<CheckCircleIcon className="w-6 h-6 text-green-500" />) : (<PlusIcon className="w-6 h-6 text-gray-400 group-hover:text-primary-500" />)}
                  </div>
                  <div className="flex items-center justify-between">
                    <div className={`px-2 py-1 rounded-full text-xs font-medium ${integration.oauth ? 'bg-blue-100 text-blue-800' : 'bg-gray-100 text-gray-800'}`}>
                      {integration.oauth ? 'OAuth' : 'API Key'}
                    </div>
                    <div className={`px-2 py-1 rounded-full text-xs font-medium ${isConnected ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}`}>
                      {isConnected ? 'Connected' : 'Available'}
                    </div>
                  </div>
                </div>
              </div>
            )
          })}
        </div>

        {showAddModal && selectedIntegration && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-xl shadow-2xl w-full max-w-md mx-4">
              <div className="p-6 border-b border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900 flex items-center">
                  <span className="text-2xl mr-3">{getIntegrationIcon(selectedIntegration.name)}</span>
                  Connect {selectedIntegration.name}
                </h3>
              </div>
              <form onSubmit={(e) => { e.preventDefault(); const formData = new FormData(e.target); const integrationData = { name: selectedIntegration.name, platform: selectedIntegration.name, credentials: { type: selectedIntegration.oauth ? 'oauth' : 'api_key', api_key: formData.get('api_key') } }; addIntegration(integrationData) }} className="p-6">
                {selectedIntegration.oauth ? (
                  <div className="text-center py-8">
                    <p className="text-gray-600 mb-6">Click the button below to authenticate with {selectedIntegration.name}</p>
                    <button type="button" className="btn-primary" onClick={() => { toast.info('OAuth integration coming soon!'); setShowAddModal(false) }}>
                      Authenticate with {selectedIntegration.name}
                    </button>
                  </div>
                ) : (
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">API Key</label>
                      <input type="text" name="api_key" required className="input-field" placeholder="Enter your API key" />
                    </div>
                    <div className="flex justify-end space-x-3 pt-4">
                      <button type="button" onClick={() => setShowAddModal(false)} className="btn-secondary">Cancel</button>
                      <button type="submit" className="btn-primary">Connect</button>
                    </div>
                  </div>
                )}
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default Integrations