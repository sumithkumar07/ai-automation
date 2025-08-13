// 🚀 PROGRESSIVE ENHANCEMENT WRAPPER
// Zero UI disruption - Optional enhancement overlay

import React, { useState, useEffect } from 'react'
import { enhancedApiClient } from '../utils/enhancedApiClient'

const ProgressiveEnhancementIndicator = ({ children }) => {
  const [enhancementStatus, setEnhancementStatus] = useState({
    available: false,
    loading: true,
    capabilities: {}
  })
  const [showEnhancementBadge, setShowEnhancementBadge] = useState(false)

  useEffect(() => {
    checkEnhancementStatus()
  }, [])

  const checkEnhancementStatus = async () => {
    try {
      const status = await enhancedApiClient.testEnhancementsConnection()
      setEnhancementStatus({
        available: status.connected,
        loading: false,
        capabilities: enhancedApiClient.getSystemStatus().capabilities,
        systemStatus: status.status
      })
      
      // Show badge for 3 seconds when enhancements are available
      if (status.connected) {
        setShowEnhancementBadge(true)
        setTimeout(() => setShowEnhancementBadge(false), 3000)
      }
    } catch (error) {
      console.log('Enhancement status check failed:', error)
      setEnhancementStatus({
        available: false,
        loading: false,
        capabilities: {}
      })
    }
  }

  return (
    <div className="relative">
      {children}
      
      {/* Enhancement Available Badge - Very subtle, fades after 3s */}
      {showEnhancementBadge && enhancementStatus.available && (
        <div className="fixed top-20 right-4 z-50 animate-fade-in-out">
          <div className="bg-gradient-to-r from-green-500 to-blue-500 text-white px-3 py-1 rounded-full text-xs font-medium shadow-lg flex items-center space-x-2">
            <div className="w-2 h-2 bg-white rounded-full animate-pulse"></div>
            <span>Enhanced AI Active</span>
          </div>
        </div>
      )}

      {/* Enhancement Status Indicator - Hidden by default */}
      <div className="hidden" id="enhancement-status" data-available={enhancementStatus.available}>
        {JSON.stringify(enhancementStatus)}
      </div>
    </div>
  )
}

export default ProgressiveEnhancementIndicator