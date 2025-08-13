import React, { createContext, useContext, useState, useEffect } from 'react'

const AccessibilityContext = createContext()

export const useAccessibility = () => {
  const context = useContext(AccessibilityContext)
  if (!context) {
    throw new Error('useAccessibility must be used within AccessibilityProvider')
  }
  return context
}

export const AccessibilityProvider = ({ children }) => {
  const [preferences, setPreferences] = useState({
    reducedMotion: false,
    highContrast: false,
    fontSize: 'normal', // 'small', 'normal', 'large', 'extra-large'
    keyboardNavigation: false,
    screenReader: false
  })

  // Detect system preferences
  useEffect(() => {
    // Check for reduced motion preference
    const mediaQueryReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)')
    setPreferences(prev => ({ ...prev, reducedMotion: mediaQueryReducedMotion.matches }))

    // Check for high contrast preference
    const mediaQueryHighContrast = window.matchMedia('(prefers-contrast: high)')
    setPreferences(prev => ({ ...prev, highContrast: mediaQueryHighContrast.matches }))

    // Detect keyboard navigation
    const handleKeyDown = (e) => {
      if (e.key === 'Tab') {
        setPreferences(prev => ({ ...prev, keyboardNavigation: true }))
      }
    }

    // Detect screen reader (basic detection)
    const screenReaderDetected = navigator.userAgent.includes('JAWS') || 
                                 navigator.userAgent.includes('NVDA') || 
                                 window.speechSynthesis

    if (screenReaderDetected) {
      setPreferences(prev => ({ ...prev, screenReader: true }))
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [])

  // Apply accessibility preferences to document
  useEffect(() => {
    const root = document.documentElement

    // Apply font size
    root.style.setProperty('--accessibility-font-scale', 
      preferences.fontSize === 'small' ? '0.875' :
      preferences.fontSize === 'large' ? '1.125' :
      preferences.fontSize === 'extra-large' ? '1.25' : '1'
    )

    // Apply high contrast
    if (preferences.highContrast) {
      root.classList.add('high-contrast')
    } else {
      root.classList.remove('high-contrast')
    }

    // Apply reduced motion
    if (preferences.reducedMotion) {
      root.classList.add('reduced-motion')
    } else {
      root.classList.remove('reduced-motion')
    }

    // Keyboard navigation focus styles
    if (preferences.keyboardNavigation) {
      root.classList.add('keyboard-navigation')
    }
  }, [preferences])

  const updatePreference = (key, value) => {
    setPreferences(prev => ({ ...prev, [key]: value }))
    
    // Store in localStorage
    const stored = JSON.parse(localStorage.getItem('accessibility-preferences') || '{}')
    stored[key] = value
    localStorage.setItem('accessibility-preferences', JSON.stringify(stored))
  }

  // Load stored preferences
  useEffect(() => {
    const stored = JSON.parse(localStorage.getItem('accessibility-preferences') || '{}')
    setPreferences(prev => ({ ...prev, ...stored }))
  }, [])

  const value = {
    preferences,
    updatePreference,
    announceToScreenReader: (message) => {
      if (preferences.screenReader) {
        const announcement = document.createElement('div')
        announcement.setAttribute('aria-live', 'polite')
        announcement.setAttribute('aria-atomic', 'true')
        announcement.className = 'sr-only'
        announcement.textContent = message
        document.body.appendChild(announcement)
        setTimeout(() => document.body.removeChild(announcement), 1000)
      }
    }
  }

  return (
    <AccessibilityContext.Provider value={value}>
      {children}
    </AccessibilityContext.Provider>
  )
}

// Screen reader only utility component
export const ScreenReaderOnly = ({ children }) => (
  <span className="sr-only">{children}</span>
)

// Skip to content link
export const SkipToContent = () => (
  <a
    href="#main-content"
    className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 bg-primary-600 text-white px-4 py-2 rounded-lg z-50"
  >
    Skip to main content
  </a>
)