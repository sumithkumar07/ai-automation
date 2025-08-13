import React, { useState, useEffect } from 'react'
import { 
  Bars3Icon, 
  XMarkIcon, 
  ChevronDownIcon,
  DevicePhoneMobileIcon,
  ComputerDesktopIcon,
  DeviceTabletIcon
} from '@heroicons/react/24/outline'

// Hook to detect device type and screen size
export const useResponsive = () => {
  const [screenSize, setScreenSize] = useState({
    width: typeof window !== 'undefined' ? window.innerWidth : 1200,
    height: typeof window !== 'undefined' ? window.innerHeight : 800
  })
  
  const [deviceType, setDeviceType] = useState('desktop')

  useEffect(() => {
    const updateScreenSize = () => {
      const width = window.innerWidth
      const height = window.innerHeight
      
      setScreenSize({ width, height })
      
      // Determine device type
      if (width < 768) {
        setDeviceType('mobile')
      } else if (width < 1024) {
        setDeviceType('tablet')
      } else {
        setDeviceType('desktop')
      }
    }

    updateScreenSize()
    window.addEventListener('resize', updateScreenSize)
    return () => window.removeEventListener('resize', updateScreenSize)
  }, [])

  return {
    screenSize,
    deviceType,
    isMobile: deviceType === 'mobile',
    isTablet: deviceType === 'tablet',
    isDesktop: deviceType === 'desktop',
    isMobileOrTablet: deviceType === 'mobile' || deviceType === 'tablet'
  }
}

// Mobile-first navigation component
export const MobileNavigation = ({ isOpen, onClose, navigationItems, currentPath }) => {
  const { isMobile } = useResponsive()

  if (!isMobile) return null

  return (
    <>
      {/* Overlay */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
          onClick={onClose}
        />
      )}
      
      {/* Mobile menu */}
      <div className={`
        fixed top-0 left-0 h-full w-80 bg-white dark:bg-gray-800 shadow-xl z-50 transform transition-transform duration-300 ease-in-out lg:hidden
        ${isOpen ? 'translate-x-0' : '-translate-x-full'}
      `}>
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-gradient-to-r from-primary-500 to-accent-500 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-lg">A</span>
            </div>
            <span className="text-xl font-bold text-gray-900 dark:text-white">Aether</span>
          </div>
          <button
            onClick={onClose}
            className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
          >
            <XMarkIcon className="w-6 h-6" />
          </button>
        </div>

        {/* Navigation Items */}
        <nav className="p-4">
          <div className="space-y-2">
            {navigationItems.map((item) => {
              const Icon = item.icon
              const isActive = currentPath === item.path
              
              return (
                <a
                  key={item.path}
                  href={item.path}
                  onClick={onClose}
                  className={`
                    flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors
                    ${isActive 
                      ? 'bg-primary-50 dark:bg-primary-900/20 text-primary-600 dark:text-primary-400' 
                      : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                    }
                  `}
                >
                  <Icon className="w-6 h-6" />
                  <span className="font-medium">{item.name}</span>
                </a>
              )
            })}
          </div>
        </nav>
      </div>
    </>
  )
}

// Responsive grid component
export const ResponsiveGrid = ({ children, className = '', cols = { mobile: 1, tablet: 2, desktop: 3 } }) => {
  return (
    <div className={`
      grid gap-4 sm:gap-6
      grid-cols-${cols.mobile}
      md:grid-cols-${cols.tablet}
      lg:grid-cols-${cols.desktop}
      ${className}
    `}>
      {children}
    </div>
  )
}

// Responsive container
export const ResponsiveContainer = ({ children, className = '', size = 'default' }) => {
  const sizeClasses = {
    small: 'max-w-4xl',
    default: 'max-w-7xl',
    large: 'max-w-8xl',
    full: 'max-w-full'
  }

  return (
    <div className={`
      ${sizeClasses[size]} mx-auto px-4 sm:px-6 lg:px-8
      ${className}
    `}>
      {children}
    </div>
  )
}

// Mobile-optimized workflow editor toolbar
export const MobileWorkflowToolbar = ({ onAddNode, onZoomIn, onZoomOut, onFitView, isCollapsed, onToggleCollapse }) => {
  const { isMobile } = useResponsive()

  if (!isMobile) return null

  return (
    <div className="fixed bottom-4 left-4 right-4 z-40 lg:hidden">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 p-4">
        {/* Collapsed view */}
        {isCollapsed ? (
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-gray-900 dark:text-white">Workflow Tools</span>
            <button
              onClick={onToggleCollapse}
              className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
            >
              <ChevronDownIcon className="w-5 h-5 transform rotate-180" />
            </button>
          </div>
        ) : (
          <>
            {/* Expanded view */}
            <div className="flex items-center justify-between mb-4">
              <span className="text-sm font-medium text-gray-900 dark:text-white">Workflow Tools</span>
              <button
                onClick={onToggleCollapse}
                className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
              >
                <ChevronDownIcon className="w-5 h-5" />
              </button>
            </div>
            
            <div className="grid grid-cols-2 gap-3">
              <button
                onClick={onAddNode}
                className="flex items-center justify-center px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors"
              >
                <span className="text-sm font-medium">Add Node</span>
              </button>
              
              <button
                onClick={onFitView}
                className="flex items-center justify-center px-4 py-2 bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
              >
                <span className="text-sm font-medium">Fit View</span>
              </button>
              
              <button
                onClick={onZoomIn}
                className="flex items-center justify-center px-4 py-2 bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
              >
                <span className="text-sm font-medium">Zoom In</span>
              </button>
              
              <button
                onClick={onZoomOut}
                className="flex items-center justify-center px-4 py-2 bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
              >
                <span className="text-sm font-medium">Zoom Out</span>
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  )
}

// Responsive card component
export const ResponsiveCard = ({ children, className = '', padding = 'default' }) => {
  const paddingClasses = {
    none: '',
    small: 'p-3 sm:p-4',
    default: 'p-4 sm:p-6',
    large: 'p-6 sm:p-8'
  }

  return (
    <div className={`
      bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 shadow-sm
      ${paddingClasses[padding]}
      ${className}
    `}>
      {children}
    </div>
  )
}

// Device indicator (for development/testing)
export const DeviceIndicator = () => {
  const { deviceType, screenSize } = useResponsive()
  
  if (import.meta.env.MODE !== 'development') return null

  const getDeviceIcon = () => {
    switch (deviceType) {
      case 'mobile':
        return <DevicePhoneMobileIcon className="w-4 h-4" />
      case 'tablet':
        return <DeviceTabletIcon className="w-4 h-4" />
      default:
        return <ComputerDesktopIcon className="w-4 h-4" />
    }
  }

  return (
    <div className="fixed top-4 left-4 z-50 bg-black bg-opacity-75 text-white px-3 py-2 rounded-lg text-xs font-mono">
      <div className="flex items-center space-x-2">
        {getDeviceIcon()}
        <span>{deviceType}</span>
        <span>{screenSize.width}×{screenSize.height}</span>
      </div>
    </div>
  )
}

// Main responsive wrapper component
const MobileResponsiveWrapper = ({ children }) => {
  const { isMobile, isTablet, deviceType } = useResponsive()

  return (
    <div className={`
      responsive-wrapper
      ${deviceType === 'mobile' ? 'mobile-layout' : ''}
      ${deviceType === 'tablet' ? 'tablet-layout' : ''}
      ${deviceType === 'desktop' ? 'desktop-layout' : ''}
    `}>
      {children}
      <DeviceIndicator />
    </div>
  )
}

export default MobileResponsiveWrapper