import React, { useState, useEffect } from 'react'
import { apiMethods } from '../utils/api'
import { 
  CogIcon, 
  SparklesIcon,
  UsersIcon,
  ChartBarIcon,
  BeakerIcon,
  ToggleIcon,
  InformationCircleIcon
} from '@heroicons/react/24/outline'
import toast from 'react-hot-toast'
import LoadingSpinner from './LoadingSpinner'

const EnhancementSettings = ({ isOpen, onClose }) => {
  const [features, setFeatures] = useState({})
  const [loading, setLoading] = useState(true)
  const [updating, setUpdating] = useState(null)

  useEffect(() => {
    if (isOpen) {
      loadAvailableFeatures()
    }
  }, [isOpen])

  const loadAvailableFeatures = async () => {
    try {
      setLoading(true)
      const response = await apiMethods.getEnhancementFeatures()
      if (response.success) {
        setFeatures(response.data.features || {})
      }
    } catch (error) {
      console.error('Error loading enhancement features:', error)
      toast.error('Failed to load enhancement features')
    } finally {
      setLoading(false)
    }
  }

  const toggleFeature = async (featureKey, enabled) => {
    try {
      setUpdating(featureKey)
      
      const response = await apiMethods.updateEnhancementPreference({
        feature: featureKey,
        enabled: enabled
      })
      
      if (response.success) {
        // Update local state
        setFeatures(prev => ({
          ...prev,
          [getPhaseKey(featureKey)]: {
            ...prev[getPhaseKey(featureKey)],
            features: {
              ...prev[getPhaseKey(featureKey)]?.features,
              [featureKey]: {
                ...prev[getPhaseKey(featureKey)]?.features[featureKey],
                enabled: enabled
              }
            }
          }
        }))
        
        toast.success(
          enabled 
            ? `${getFeatureName(featureKey)} enabled successfully!` 
            : `${getFeatureName(featureKey)} disabled`
        )
      } else {
        throw new Error(response.error || 'Failed to update preference')
      }
    } catch (error) {
      console.error('Error updating feature preference:', error)
      toast.error('Failed to update feature preference')
    } finally {
      setUpdating(null)
    }
  }

  const getPhaseKey = (featureKey) => {
    // Map feature keys to their phase groups
    const phaseMapping = {
      'ai_smart_suggestions': 'phase_2_ai_intelligence',
      'ai_predictive_analytics': 'phase_2_ai_intelligence',
      'ai_voice_input': 'phase_2_ai_intelligence',
      'enterprise_workspaces': 'phase_3_collaboration',
      'realtime_collaboration': 'phase_3_collaboration',
      'advanced_permissions': 'phase_3_collaboration',
      'advanced_analytics': 'phase_4_platform',
      'business_intelligence': 'phase_4_platform',
      'smart_marketplace': 'phase_4_platform',
      'iot_integration': 'phase_5_future',
      'blockchain_verification': 'phase_5_future',
      'custom_ai_models': 'phase_5_future'
    }
    return phaseMapping[featureKey] || 'phase_2_ai_intelligence'
  }

  const getFeatureName = (featureKey) => {
    const allFeatures = Object.values(features).reduce((acc, phase) => {
      return { ...acc, ...phase.features }
    }, {})
    return allFeatures[featureKey]?.name || featureKey
  }

  const getPhaseIcon = (phaseKey) => {
    const icons = {
      'phase_2_ai_intelligence': SparklesIcon,
      'phase_3_collaboration': UsersIcon,
      'phase_4_platform': ChartBarIcon,
      'phase_5_future': BeakerIcon
    }
    return icons[phaseKey] || CogIcon
  }

  const getPhaseColor = (phaseKey) => {
    const colors = {
      'phase_2_ai_intelligence': 'from-purple-500 to-pink-500',
      'phase_3_collaboration': 'from-blue-500 to-cyan-500',
      'phase_4_platform': 'from-green-500 to-teal-500',
      'phase_5_future': 'from-orange-500 to-red-500'
    }
    return colors[phaseKey] || 'from-gray-500 to-gray-600'
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex items-center justify-center min-h-screen px-4 pt-4 pb-20 text-center sm:block sm:p-0">
        <div className="fixed inset-0 transition-opacity bg-gray-500 bg-opacity-75" onClick={onClose}></div>
        
        <div className="inline-block w-full max-w-4xl px-6 py-4 my-8 text-left align-middle transition-all transform bg-white rounded-lg shadow-xl">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-gradient-to-r from-primary-500 to-accent-500 rounded-lg">
                <CogIcon className="w-6 h-6 text-white" />
              </div>
              <div>
                <h3 className="text-xl font-bold text-gray-900">Enhancement Settings</h3>
                <p className="text-sm text-gray-600">
                  Enable optional features to unlock advanced capabilities. All features are hidden by default.
                </p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg"
            >
              <span className="sr-only">Close</span>
              <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {loading ? (
            <div className="flex items-center justify-center py-12">
              <LoadingSpinner size="large" />
              <span className="ml-3 text-gray-600">Loading enhancement features...</span>
            </div>
          ) : (
            <div className="space-y-6">
              {/* Zero UI Disruption Notice */}
              <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                <div className="flex items-start space-x-3">
                  <InformationCircleIcon className="w-5 h-5 text-blue-500 mt-0.5" />
                  <div>
                    <h4 className="font-medium text-blue-900">Zero UI Disruption Guarantee</h4>
                    <p className="text-sm text-blue-700 mt-1">
                      All enhancement features are completely optional and hidden by default. 
                      Your existing interface will remain exactly the same until you choose to enable specific features.
                    </p>
                  </div>
                </div>
              </div>

              {/* Feature Phases */}
              {Object.entries(features).map(([phaseKey, phase]) => {
                const Icon = getPhaseIcon(phaseKey)
                const colorClass = getPhaseColor(phaseKey)
                
                return (
                  <div key={phaseKey} className="border border-gray-200 rounded-lg overflow-hidden">
                    {/* Phase Header */}
                    <div className={`px-6 py-4 bg-gradient-to-r ${colorClass}`}>
                      <div className="flex items-center space-x-3">
                        <Icon className="w-6 h-6 text-white" />
                        <div>
                          <h4 className="text-lg font-semibold text-white">{phase.title}</h4>
                          <p className="text-sm text-white/90">{phase.description}</p>
                        </div>
                      </div>
                    </div>

                    {/* Phase Features */}
                    <div className="px-6 py-4 space-y-4">
                      {Object.entries(phase.features || {}).map(([featureKey, feature]) => (
                        <div key={featureKey} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                          <div className="flex-1">
                            <h5 className="font-medium text-gray-900">{feature.name}</h5>
                            <p className="text-sm text-gray-600 mt-1">{feature.description}</p>
                          </div>
                          
                          <div className="ml-4">
                            <button
                              onClick={() => toggleFeature(featureKey, !feature.enabled)}
                              disabled={updating === featureKey}
                              className={`relative inline-flex items-center h-6 rounded-full w-11 transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 ${
                                feature.enabled 
                                  ? 'bg-primary-600' 
                                  : 'bg-gray-200'
                              } ${updating === featureKey ? 'opacity-50 cursor-not-allowed' : ''}`}
                            >
                              {updating === featureKey ? (
                                <div className="w-4 h-4 mx-auto">
                                  <LoadingSpinner size="small" />
                                </div>
                              ) : (
                                <span
                                  className={`inline-block w-4 h-4 transform bg-white rounded-full transition-transform ${
                                    feature.enabled ? 'translate-x-6' : 'translate-x-1'
                                  }`}
                                />
                              )}
                            </button>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )
              })}

              {/* Summary */}
              {Object.keys(features).length > 0 && (
                <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                  <div className="text-center">
                    <p className="text-sm text-green-800">
                      <strong>All 5 Enhancement Phases Available:</strong> Advanced Intelligence, 
                      Enterprise Collaboration, Next-Gen Platform Features, and Future Technologies
                    </p>
                    <p className="text-xs text-green-600 mt-1">
                      Enable features gradually to discover new capabilities while maintaining your familiar interface.
                    </p>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Footer */}
          <div className="flex items-center justify-between mt-8 pt-6 border-t border-gray-200">
            <div className="text-sm text-gray-500">
              Enhancement System v2.0.0 • Zero UI Disruption Mode
            </div>
            <div className="flex space-x-3">
              <button
                onClick={onClose}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default EnhancementSettings