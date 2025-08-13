import React, { useState } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { useAccessibility } from '../components/AccessibilityProvider'
import EnhancedNavbar from '../components/EnhancedNavbar'
import { 
  UserIcon,
  KeyIcon,
  BellIcon,
  EyeIcon,
  ShieldCheckIcon,
  CogIcon,
  CheckCircleIcon
} from '@heroicons/react/24/outline'
import toast from 'react-hot-toast'

const AccountSettings = () => {
  const { user, updateProfile } = useAuth()
  const { preferences, updatePreference } = useAccessibility()
  const [activeTab, setActiveTab] = useState('profile')
  const [loading, setLoading] = useState(false)
  const [profileData, setProfileData] = useState({
    name: user?.name || '',
    email: user?.email || '',
    company: user?.company || '',
    role: user?.role || ''
  })

  const tabs = [
    { id: 'profile', name: 'Profile', icon: UserIcon },
    { id: 'security', name: 'Security', icon: ShieldCheckIcon },
    { id: 'notifications', name: 'Notifications', icon: BellIcon },
    { id: 'accessibility', name: 'Accessibility', icon: EyeIcon },
    { id: 'preferences', name: 'Preferences', icon: CogIcon }
  ]

  const handleProfileUpdate = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      await updateProfile(profileData)
      toast.success('Profile updated successfully!')
    } catch (error) {
      toast.error('Failed to update profile')
    } finally {
      setLoading(false)
    }
  }

  const renderTabContent = () => {
    switch (activeTab) {
      case 'profile':
        return (
          <form onSubmit={handleProfileUpdate} className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="form-label">Full Name</label>
                <input
                  type="text"
                  value={profileData.name}
                  onChange={(e) => setProfileData(prev => ({ ...prev, name: e.target.value }))}
                  className="input-field"
                  required
                />
              </div>
              <div>
                <label className="form-label">Email</label>
                <input
                  type="email"
                  value={profileData.email}
                  onChange={(e) => setProfileData(prev => ({ ...prev, email: e.target.value }))}
                  className="input-field"
                  required
                />
              </div>
              <div>
                <label className="form-label">Company</label>
                <input
                  type="text"
                  value={profileData.company}
                  onChange={(e) => setProfileData(prev => ({ ...prev, company: e.target.value }))}
                  className="input-field"
                />
              </div>
              <div>
                <label className="form-label">Role</label>
                <input
                  type="text"
                  value={profileData.role}
                  onChange={(e) => setProfileData(prev => ({ ...prev, role: e.target.value }))}
                  className="input-field"
                />
              </div>
            </div>
            <div className="flex justify-end">
              <button
                type="submit"
                disabled={loading}
                className="btn-primary disabled:opacity-50"
              >
                {loading ? 'Updating...' : 'Update Profile'}
              </button>
            </div>
          </form>
        )

      case 'security':
        return (
          <div className="space-y-6">
            <div className="card p-6">
              <h3 className="font-semibold text-gray-900 mb-4 flex items-center">
                <KeyIcon className="w-5 h-5 mr-2" />
                Change Password
              </h3>
              <div className="space-y-4">
                <div>
                  <label className="form-label">Current Password</label>
                  <input type="password" className="input-field" />
                </div>
                <div>
                  <label className="form-label">New Password</label>
                  <input type="password" className="input-field" />
                </div>
                <div>
                  <label className="form-label">Confirm New Password</label>
                  <input type="password" className="input-field" />
                </div>
                <button className="btn-primary">Update Password</button>
              </div>
            </div>
            
            <div className="card p-6">
              <h3 className="font-semibold text-gray-900 mb-4">Two-Factor Authentication</h3>
              <p className="text-gray-600 mb-4">Add an extra layer of security to your account.</p>
              <button className="btn-secondary">Enable 2FA</button>
            </div>
          </div>
        )

      case 'notifications':
        return (
          <div className="space-y-6">
            <div className="card p-6">
              <h3 className="font-semibold text-gray-900 mb-4">Email Notifications</h3>
              <div className="space-y-4">
                <label className="flex items-center">
                  <input type="checkbox" className="mr-3" defaultChecked />
                  <span>Workflow execution updates</span>
                </label>
                <label className="flex items-center">
                  <input type="checkbox" className="mr-3" defaultChecked />
                  <span>Integration status changes</span>
                </label>
                <label className="flex items-center">
                  <input type="checkbox" className="mr-3" />
                  <span>Weekly usage reports</span>
                </label>
                <label className="flex items-center">
                  <input type="checkbox" className="mr-3" />
                  <span>Product updates and features</span>
                </label>
              </div>
            </div>
          </div>
        )

      case 'accessibility':
        return (
          <div className="space-y-6">
            <div className="card p-6">
              <h3 className="font-semibold text-gray-900 mb-4">Display Settings</h3>
              <div className="space-y-4">
                <div>
                  <label className="form-label">Font Size</label>
                  <select
                    value={preferences.fontSize}
                    onChange={(e) => updatePreference('fontSize', e.target.value)}
                    className="input-field"
                  >
                    <option value="small">Small</option>
                    <option value="normal">Normal</option>
                    <option value="large">Large</option>
                    <option value="extra-large">Extra Large</option>
                  </select>
                </div>
                
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={preferences.highContrast}
                    onChange={(e) => updatePreference('highContrast', e.target.checked)}
                    className="mr-3"
                  />
                  <span>High contrast mode</span>
                </label>
                
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={preferences.reducedMotion}
                    onChange={(e) => updatePreference('reducedMotion', e.target.checked)}
                    className="mr-3"
                  />
                  <span>Reduce motion and animations</span>
                </label>
              </div>
            </div>
          </div>
        )

      case 'preferences':
        return (
          <div className="space-y-6">
            <div className="card p-6">
              <h3 className="font-semibold text-gray-900 mb-4">Workflow Preferences</h3>
              <div className="space-y-4">
                <label className="flex items-center">
                  <input type="checkbox" className="mr-3" defaultChecked />
                  <span>Auto-save workflows</span>
                </label>
                <label className="flex items-center">
                  <input type="checkbox" className="mr-3" defaultChecked />
                  <span>Show node tooltips</span>
                </label>
                <label className="flex items-center">
                  <input type="checkbox" className="mr-3" />
                  <span>Confirm before deleting nodes</span>
                </label>
              </div>
            </div>
            
            <div className="card p-6">
              <h3 className="font-semibold text-gray-900 mb-4">AI Assistant</h3>
              <div className="space-y-4">
                <label className="flex items-center">
                  <input type="checkbox" className="mr-3" defaultChecked />
                  <span>Enable AI suggestions</span>
                </label>
                <label className="flex items-center">
                  <input type="checkbox" className="mr-3" defaultChecked />
                  <span>Auto-optimize workflows</span>
                </label>
              </div>
            </div>
          </div>
        )

      default:
        return null
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <EnhancedNavbar />
      
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Account Settings</h1>
          <p className="text-gray-600">Manage your account preferences and security settings.</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Sidebar */}
          <div className="lg:col-span-1">
            <nav className="space-y-1">
              {tabs.map((tab) => {
                const Icon = tab.icon
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`w-full flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-colors ${
                      activeTab === tab.id
                        ? 'bg-primary-100 text-primary-700'
                        : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                    }`}
                  >
                    <Icon className="w-5 h-5 mr-3" />
                    {tab.name}
                  </button>
                )
              })}
            </nav>
          </div>

          {/* Content */}
          <div className="lg:col-span-3">
            <div className="card p-6">
              {renderTabContent()}
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}

export default AccountSettings