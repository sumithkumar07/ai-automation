// Enhanced Navbar with Global Search and Performance Indicators
import React, { useState, useRef, useEffect } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import {
  MagnifyingGlassIcon,
  BellIcon,
  UserCircleIcon,
  CogIcon,
  ChartBarIcon,
  DocumentDuplicateIcon,
  QuestionMarkCircleIcon,
  ArrowRightOnRectangleIcon,
  Bars3Icon,
  XMarkIcon,
  SparklesIcon,
  CommandLineIcon,
  GlobeAltIcon,
  CloudIcon
} from '@heroicons/react/24/outline'
import { Transition } from '@headlessui/react'
import GlobalSearch from './GlobalSearch'
import TemplatesGallery from './TemplatesGallery'
import PerformanceMonitor from './PerformanceMonitor'
import { enhancedApiMethods } from '../utils/enhancedApi'
import toast from 'react-hot-toast'

const EnhancedNavbar = () => {
  const { user, logout } = useAuth()
  const location = useLocation()
  const navigate = useNavigate()
  
  const [showUserMenu, setShowUserMenu] = useState(false)
  const [showMobileMenu, setShowMobileMenu] = useState(false)
  const [showGlobalSearch, setShowGlobalSearch] = useState(false)
  const [showTemplatesGallery, setShowTemplatesGallery] = useState(false)
  const [showPerformanceMonitor, setShowPerformanceMonitor] = useState(false)
  const [systemStatus, setSystemStatus] = useState('healthy')
  const [notifications, setNotifications] = useState([])
  const [quickActions, setQuickActions] = useState(false)
  
  const userMenuRef = useRef()
  const mobileMenuRef = useRef()

  // Navigation items with enhanced structure
  const navigation = [
    { name: 'Dashboard', href: '/dashboard', icon: ChartBarIcon, current: location.pathname === '/dashboard' },
    { name: 'Editor', href: '/editor', icon: CogIcon, current: location.pathname.startsWith('/editor') },
    { name: 'Integrations', href: '/integrations', icon: GlobeAltIcon, current: location.pathname === '/integrations' },
    { name: 'Docs', href: '/docs', icon: QuestionMarkCircleIcon, current: location.pathname.startsWith('/docs') || location.pathname.startsWith('/help') || location.pathname.startsWith('/academy') },
  ]

  const quickActionItems = [
    {
      name: 'New Workflow',
      action: () => navigate('/editor'),
      icon: CogIcon,
      shortcut: 'Ctrl+N'
    },
    {
      name: 'Search Everything',
      action: () => setShowGlobalSearch(true),
      icon: MagnifyingGlassIcon,
      shortcut: 'Ctrl+K'
    },
    {
      name: 'Templates Gallery',
      action: () => setShowTemplatesGallery(true),
      icon: DocumentDuplicateIcon,
      shortcut: 'Ctrl+T'
    },
    {
      name: 'AI Assistant',
      action: () => {/* AI Assistant logic */},
      icon: SparklesIcon,
      shortcut: 'Ctrl+A'
    },
    {
      name: 'Performance Monitor',
      action: () => setShowPerformanceMonitor(true),
      icon: ChartBarIcon,
      shortcut: 'Ctrl+P'
    }
  ]

  // Load system status and notifications
  useEffect(() => {
    loadSystemStatus()
    loadNotifications()
    
    // Set up periodic status checks
    const interval = setInterval(loadSystemStatus, 30000)
    return () => clearInterval(interval)
  }, [])

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.ctrlKey || e.metaKey) {
        switch (e.key.toLowerCase()) {
          case 'k':
            e.preventDefault()
            setShowGlobalSearch(true)
            break
          case 'n':
            e.preventDefault()
            navigate('/editor')
            break
          case 't':
            e.preventDefault()
            setShowTemplatesGallery(true)
            break
          case 'p':
            e.preventDefault()
            setShowPerformanceMonitor(true)
            break
          case '/':
            e.preventDefault()
            setQuickActions(true)
            break
        }
      }
      
      // Escape key handling
      if (e.key === 'Escape') {
        setShowGlobalSearch(false)
        setShowTemplatesGallery(false)
        setShowPerformanceMonitor(false)
        setQuickActions(false)
        setShowUserMenu(false)
        setShowMobileMenu(false)
      }
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [navigate])

  // Click outside handlers
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (userMenuRef.current && !userMenuRef.current.contains(event.target)) {
        setShowUserMenu(false)
      }
      if (mobileMenuRef.current && !mobileMenuRef.current.contains(event.target)) {
        setShowMobileMenu(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const loadSystemStatus = async () => {
    try {
      const result = await enhancedApiMethods.getSystemHealth()
      setSystemStatus(result.system_health?.status || 'healthy')
    } catch (error) {
      setSystemStatus('degraded')
    }
  }

  const loadNotifications = async () => {
    // Mock notifications - in real app, this would fetch from API
    setNotifications([
      {
        id: 1,
        type: 'info',
        message: 'New template "Customer Onboarding" is available',
        time: '5 min ago',
        unread: true
      },
      {
        id: 2,
        type: 'warning',
        message: 'Integration "Slack Bot" needs attention',
        time: '1 hour ago',
        unread: true
      }
    ])
  }

  const handleTemplateSelect = async (template) => {
    try {
      const result = await enhancedApiMethods.deployEnhancedTemplate(template.id)
      toast.success(`Template "${template.name}" deployed successfully!`)
      navigate(`/editor/${result.workflow.id}`)
    } catch (error) {
      toast.error('Failed to deploy template')
    }
  }

  const handleGlobalSearchSelect = (result, type) => {
    // Handle different result types
    switch (type) {
      case 'workflows':
        navigate(`/editor/${result.id}`)
        break
      case 'templates':
        setShowTemplatesGallery(true)
        break
      case 'integrations':
        navigate('/integrations')
        break
      default:
        toast.info(`Selected ${type}: ${result.name}`)
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'healthy':
        return 'bg-green-500'
      case 'warning':
        return 'bg-yellow-500'
      case 'critical':
        return 'bg-red-500'
      default:
        return 'bg-gray-500'
    }
  }

  const handleLogout = async () => {
    try {
      logout()
      navigate('/auth')
      toast.success('Logged out successfully')
    } catch (error) {
      toast.error('Logout failed')
    }
  }

  return (
    <>
      <nav className="bg-white dark:bg-gray-800 shadow-lg border-b border-gray-200 dark:border-gray-700 sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            {/* Logo and Navigation */}
            <div className="flex items-center">
              <Link to="/dashboard" className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-gradient-to-r from-primary-500 to-accent-500 rounded-lg flex items-center justify-center">
                  <span className="text-white font-bold text-lg">A</span>
                </div>
                <span className="text-xl font-bold text-gray-900 dark:text-white">
                  Aether Automation
                </span>
              </Link>

              {/* Desktop Navigation */}
              <div className="hidden md:ml-10 md:flex md:space-x-8">
                {navigation.map((item) => {
                  const Icon = item.icon
                  return (
                    <Link
                      key={item.name}
                      to={item.href}
                      className={`${
                        item.current
                          ? 'border-primary-500 text-primary-600 dark:text-primary-400'
                          : 'border-transparent text-gray-500 dark:text-gray-400 hover:border-gray-300 hover:text-gray-700 dark:hover:text-gray-300'
                      } inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium transition-colors`}
                    >
                      <Icon className="w-4 h-4 mr-2" />
                      {item.name}
                    </Link>
                  )
                })}
              </div>
            </div>

            {/* Right side items */}
            <div className="flex items-center space-x-4">
              {/* System Status Indicator */}
              <div className="hidden md:flex items-center space-x-2">
                <div className={`w-2 h-2 rounded-full ${getStatusColor(systemStatus)} animate-pulse`}></div>
                <span className="text-xs text-gray-500 dark:text-gray-400 capitalize">
                  {systemStatus}
                </span>
              </div>

              {/* Quick Actions Button */}
              <button
                onClick={() => setQuickActions(true)}
                className="p-2 text-gray-400 hover:text-gray-500 dark:hover:text-gray-300 relative group"
                title="Quick Actions (Ctrl+/)"
              >
                <CommandLineIcon className="w-5 h-5" />
                <span className="absolute -bottom-8 left-1/2 transform -translate-x-1/2 bg-gray-900 text-white text-xs rounded px-2 py-1 opacity-0 group-hover:opacity-100 transition-opacity">
                  Ctrl+/
                </span>
              </button>

              {/* Global Search Button */}
              <button
                onClick={() => setShowGlobalSearch(true)}
                className="p-2 text-gray-400 hover:text-gray-500 dark:hover:text-gray-300 relative group"
                title="Search (Ctrl+K)"
              >
                <MagnifyingGlassIcon className="w-5 h-5" />
                <span className="absolute -bottom-8 left-1/2 transform -translate-x-1/2 bg-gray-900 text-white text-xs rounded px-2 py-1 opacity-0 group-hover:opacity-100 transition-opacity">
                  Ctrl+K
                </span>
              </button>

              {/* Templates Button */}
              <button
                onClick={() => setShowTemplatesGallery(true)}
                className="p-2 text-gray-400 hover:text-gray-500 dark:hover:text-gray-300 relative group"
                title="Templates (Ctrl+T)"
              >
                <DocumentDuplicateIcon className="w-5 h-5" />
                <span className="absolute -bottom-8 left-1/2 transform -translate-x-1/2 bg-gray-900 text-white text-xs rounded px-2 py-1 opacity-0 group-hover:opacity-100 transition-opacity">
                  Ctrl+T
                </span>
              </button>

              {/* Performance Monitor Button */}
              <button
                onClick={() => setShowPerformanceMonitor(true)}
                className="hidden md:block p-2 text-gray-400 hover:text-gray-500 dark:hover:text-gray-300 relative group"
                title="Performance (Ctrl+P)"
              >
                <ChartBarIcon className="w-5 h-5" />
                <span className="absolute -bottom-8 left-1/2 transform -translate-x-1/2 bg-gray-900 text-white text-xs rounded px-2 py-1 opacity-0 group-hover:opacity-100 transition-opacity">
                  Ctrl+P
                </span>
              </button>

              {/* Notifications */}
              <button className="p-2 text-gray-400 hover:text-gray-500 dark:hover:text-gray-300 relative">
                <BellIcon className="w-5 h-5" />
                {notifications.filter(n => n.unread).length > 0 && (
                  <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
                    {notifications.filter(n => n.unread).length}
                  </span>
                )}
              </button>

              {/* User Menu */}
              <div className="relative" ref={userMenuRef}>
                <button
                  onClick={() => setShowUserMenu(!showUserMenu)}
                  className="flex items-center space-x-2 p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                >
                  <div className="w-8 h-8 bg-gradient-to-r from-primary-500 to-accent-500 rounded-full flex items-center justify-center">
                    <span className="text-white text-sm font-medium">
                      {user?.name?.charAt(0)?.toUpperCase() || 'U'}
                    </span>
                  </div>
                  <span className="hidden md:block text-sm font-medium text-gray-700 dark:text-gray-300">
                    {user?.name}
                  </span>
                </button>

                <Transition
                  show={showUserMenu}
                  enter="transition ease-out duration-200"
                  enterFrom="transform opacity-0 scale-95"
                  enterTo="transform opacity-100 scale-100"
                  leave="transition ease-in duration-75"
                  leaveFrom="transform opacity-100 scale-100"
                  leaveTo="transform opacity-0 scale-95"
                >
                  <div className="absolute right-0 mt-2 w-48 bg-white dark:bg-gray-700 rounded-md shadow-lg py-1 ring-1 ring-black ring-opacity-5">
                    <Link
                      to="/account"
                      className="flex items-center px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-600"
                      onClick={() => setShowUserMenu(false)}
                    >
                      <UserCircleIcon className="w-4 h-4 mr-3" />
                      Account Settings
                    </Link>
                    <Link
                      to="/settings"
                      className="flex items-center px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-600"
                      onClick={() => setShowUserMenu(false)}
                    >
                      <CogIcon className="w-4 h-4 mr-3" />
                      Preferences
                    </Link>
                    <div className="border-t border-gray-100 dark:border-gray-600 my-1"></div>
                    <button
                      onClick={() => {
                        setShowUserMenu(false)
                        handleLogout()
                      }}
                      className="flex items-center w-full px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-600"
                    >
                      <ArrowRightOnRectangleIcon className="w-4 h-4 mr-3" />
                      Sign out
                    </button>
                  </div>
                </Transition>
              </div>

              {/* Mobile menu button */}
              <button
                onClick={() => setShowMobileMenu(!showMobileMenu)}
                className="md:hidden p-2 text-gray-400 hover:text-gray-500 dark:hover:text-gray-300"
              >
                {showMobileMenu ? (
                  <XMarkIcon className="w-6 h-6" />
                ) : (
                  <Bars3Icon className="w-6 h-6" />
                )}
              </button>
            </div>
          </div>
        </div>

        {/* Mobile Navigation Menu */}
        <Transition
          show={showMobileMenu}
          enter="transition ease-out duration-200"
          enterFrom="transform opacity-0 scale-95"
          enterTo="transform opacity-100 scale-100"
          leave="transition ease-in duration-75"
          leaveFrom="transform opacity-100 scale-100"
          leaveTo="transform opacity-0 scale-95"
        >
          <div className="md:hidden" ref={mobileMenuRef}>
            <div className="px-2 pt-2 pb-3 space-y-1 bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700">
              {navigation.map((item) => {
                const Icon = item.icon
                return (
                  <Link
                    key={item.name}
                    to={item.href}
                    className={`${
                      item.current
                        ? 'bg-primary-50 dark:bg-primary-900/50 border-primary-500 text-primary-700 dark:text-primary-300'
                        : 'border-transparent text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-700 hover:border-gray-300 hover:text-gray-800 dark:hover:text-gray-200'
                    } block pl-3 pr-4 py-2 border-l-4 text-base font-medium flex items-center`}
                    onClick={() => setShowMobileMenu(false)}
                  >
                    <Icon className="w-5 h-5 mr-3" />
                    {item.name}
                  </Link>
                )
              })}
            </div>
          </div>
        </Transition>
      </nav>

      {/* Quick Actions Modal */}
      {quickActions && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-start justify-center pt-20 z-50">
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-2xl w-full max-w-lg mx-4">
            <div className="p-6">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                Quick Actions
              </h3>
              <div className="space-y-2">
                {quickActionItems.map((item) => {
                  const Icon = item.icon
                  return (
                    <button
                      key={item.name}
                      onClick={() => {
                        item.action()
                        setQuickActions(false)
                      }}
                      className="w-full flex items-center justify-between p-3 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 text-left"
                    >
                      <div className="flex items-center">
                        <Icon className="w-5 h-5 mr-3 text-gray-500" />
                        <span className="text-gray-900 dark:text-white">{item.name}</span>
                      </div>
                      <span className="text-sm text-gray-500 dark:text-gray-400">
                        {item.shortcut}
                      </span>
                    </button>
                  )
                })}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Enhanced Modals */}
      <GlobalSearch
        isOpen={showGlobalSearch}
        onClose={() => setShowGlobalSearch(false)}
        onResultSelect={handleGlobalSearchSelect}
      />

      <TemplatesGallery
        isOpen={showTemplatesGallery}
        onClose={() => setShowTemplatesGallery(false)}
        onTemplateSelect={handleTemplateSelect}
      />

      <PerformanceMonitor
        isOpen={showPerformanceMonitor}
        onClose={() => setShowPerformanceMonitor(false)}
      />
    </>
  )
}

export default EnhancedNavbar