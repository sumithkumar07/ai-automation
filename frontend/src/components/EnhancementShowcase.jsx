import React, { useState } from 'react'

/**
 * Enhancement Showcase Component
 * Demonstrates CSS-only enhancements without changing functionality
 * This is for demonstration purposes - existing components keep working as before
 */
const EnhancementShowcase = () => {
  const [isLoading, setIsLoading] = useState(false)
  const [showNotification, setShowNotification] = useState(false)

  const handleEnhancedClick = () => {
    setIsLoading(true)
    setTimeout(() => {
      setIsLoading(false)
      setShowNotification(true)
      setTimeout(() => setShowNotification(false), 3000)
    }, 2000)
  }

  return (
    <div className="max-w-6xl mx-auto p-6 space-y-8">
      <div className="text-center mb-8">
        <h1 className="text-4xl font-bold text-gradient mb-4 bounce-in-text">
          🎨 CSS Enhancement Showcase
        </h1>
        <p className="text-gray-600 slide-up-text">
          Beautiful enhancements that preserve all existing functionality
        </p>
      </div>

      {/* Enhanced Buttons */}
      <section className="card-enhanced p-6">
        <h2 className="text-2xl font-semibold mb-4 text-gradient">Enhanced Buttons</h2>
        <div className="flex flex-wrap gap-4">
          <button className="btn-primary-enhanced" onClick={handleEnhancedClick}>
            {isLoading ? (
              <div className="flex items-center gap-2">
                <div className="loading-spinner-advanced w-4 h-4"></div>
                Processing...
              </div>
            ) : (
              'Enhanced Primary'
            )}
          </button>
          <button className="btn-secondary-enhanced">Enhanced Secondary</button>
          <button className="btn-accent-enhanced">Enhanced Accent</button>
          <button className="btn-primary hover-scale press-animation">Magnetic Button</button>
        </div>
      </section>

      {/* Enhanced Cards */}
      <section className="space-y-6">
        <h2 className="text-2xl font-semibold text-gradient">Enhanced Cards</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="card-interactive p-6">
            <div className="w-12 h-12 bg-gradient-primary rounded-lg mb-4 glow-primary"></div>
            <h3 className="font-semibold mb-2">Interactive Card</h3>
            <p className="text-gray-600 text-sm">Hover for glow effect and smooth animations</p>
          </div>
          
          <div className="card-floating p-6">
            <div className="w-12 h-12 bg-gradient-accent rounded-lg mb-4 glow-accent"></div>
            <h3 className="font-semibold mb-2">Floating Card</h3>
            <p className="text-gray-600 text-sm">Gentle floating animation</p>
          </div>
          
          <div className="dashboard-card p-6">
            <div className="metric-value">1,234</div>
            <h3 className="font-semibold">Enhanced Metric</h3>
            <p className="text-gray-600 text-sm">With gradient text and shimmer border</p>
          </div>
        </div>
      </section>

      {/* Enhanced Inputs */}
      <section className="card-enhanced p-6">
        <h2 className="text-2xl font-semibold mb-4 text-gradient">Enhanced Form Elements</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="input-floating-label">
            <input 
              type="text" 
              id="enhanced-input"
              placeholder=" "
              className="input-enhanced"
            />
            <label htmlFor="enhanced-input">Floating Label Input</label>
          </div>
          
          <div className="search-container">
            <input 
              type="text" 
              placeholder="Enhanced search..."
              className="search-input"
            />
            <div className="search-icon">🔍</div>
          </div>
        </div>
      </section>

      {/* Loading States */}
      <section className="card-enhanced p-6">
        <h2 className="text-2xl font-semibold mb-4 text-gradient">Enhanced Loading States</h2>
        <div className="flex flex-wrap items-center gap-8">
          <div className="text-center">
            <div className="loading-spinner-advanced mb-2"></div>
            <p className="text-sm text-gray-600">Advanced Spinner</p>
          </div>
          
          <div className="text-center">
            <div className="loading-pulse-wave mb-2">
              <span></span>
              <span></span>
              <span></span>
              <span></span>
            </div>
            <p className="text-sm text-gray-600">Pulse Wave</p>
          </div>
          
          <div className="text-center">
            <div className="loading-breathe mb-2"></div>
            <p className="text-sm text-gray-600">Breathing</p>
          </div>
          
          <div className="text-center">
            <div className="loading-dots mb-2">
              <span></span>
              <span></span>
              <span></span>
            </div>
            <p className="text-sm text-gray-600">Elegant Dots</p>
          </div>
        </div>
      </section>

      {/* Enhanced Badges */}
      <section className="card-enhanced p-6">
        <h2 className="text-2xl font-semibold mb-4 text-gradient">Enhanced Badges</h2>
        <div className="flex flex-wrap gap-3">
          <span className="badge-primary">Primary Badge</span>
          <span className="badge-success">Success Badge</span>
          <span className="badge-warning">Warning Badge</span>
          <span className="badge-error">Error Badge</span>
        </div>
      </section>

      {/* Progress Bar */}
      <section className="card-enhanced p-6">
        <h2 className="text-2xl font-semibold mb-4 text-gradient">Enhanced Progress</h2>
        <div className="progress-bar">
          <div className="progress-fill" style={{ width: '75%' }}></div>
        </div>
      </section>

      {/* Text Effects */}
      <section className="card-enhanced p-6">
        <h2 className="text-2xl font-semibold mb-4 text-gradient">Enhanced Text Effects</h2>
        <div className="space-y-4">
          <p className="text-shimmer text-lg font-medium">Shimmering text effect</p>
          <p className="typewriter text-lg">Typewriter effect animation</p>
          <div className="bg-gradient-animated text-white p-4 rounded-lg">
            <p className="font-medium">Animated gradient background</p>
          </div>
        </div>
      </section>

      {/* Hover Effects */}
      <section className="card-enhanced p-6">
        <h2 className="text-2xl font-semibold mb-4 text-gradient">Interactive Hover Effects</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="card-enhanced p-4 text-center magnetic-hover cursor-pointer">
            <div className="text-2xl mb-2">🎯</div>
            <p className="text-sm">Magnetic</p>
          </div>
          
          <div className="card-enhanced p-4 text-center wobble-hover cursor-pointer">
            <div className="text-2xl mb-2">🎉</div>
            <p className="text-sm">Wobble</p>
          </div>
          
          <div className="card-enhanced p-4 text-center tilt-hover cursor-pointer">
            <div className="text-2xl mb-2">📐</div>
            <p className="text-sm">Tilt</p>
          </div>
          
          <div className="card-enhanced p-4 text-center ripple-effect cursor-pointer">
            <div className="text-2xl mb-2">💧</div>
            <p className="text-sm">Ripple</p>
          </div>
        </div>
      </section>

      {/* Integration Examples */}
      <section className="space-y-6">
        <h2 className="text-2xl font-semibold text-gradient">Enhanced Integration Cards</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {['Slack', 'Gmail', 'GitHub'].map((integration, index) => (
            <div key={integration} className={`integration-card p-6 stagger-${index + 1}`}>
              <div className="integration-logo mb-4">
                <span className="text-xl">{integration === 'Slack' ? '💬' : integration === 'Gmail' ? '📧' : '🐱'}</span>
              </div>
              <h3 className="font-semibold mb-2">{integration}</h3>
              <p className="text-gray-600 text-sm mb-4">Enhanced integration card with smooth animations</p>
              <span className="integration-status connected">Connected</span>
            </div>
          ))}
        </div>
      </section>

      {/* Notification Demo */}
      {showNotification && (
        <div className="notification success">
          <div className="flex items-center gap-2">
            <span className="text-green-500">✅</span>
            <span>Enhancement applied successfully!</span>
          </div>
        </div>
      )}

      {/* Implementation Note */}
      <section className="card-enhanced p-6 bg-gradient-to-br from-blue-50 to-purple-50">
        <h2 className="text-xl font-semibold mb-3 text-gradient">🔧 Implementation Notes</h2>
        <div className="text-sm text-gray-700 space-y-2">
          <p><strong>✅ Zero Breaking Changes:</strong> All existing components continue to work exactly as before.</p>
          <p><strong>🎨 CSS-Only Enhancements:</strong> Pure CSS improvements with no JavaScript modifications.</p>
          <p><strong>📱 Fully Responsive:</strong> All enhancements adapt to mobile, tablet, and desktop.</p>
          <p><strong>♿ Accessibility Compliant:</strong> Respects reduced motion preferences and maintains focus states.</p>
          <p><strong>🚀 Performance Optimized:</strong> GPU-accelerated animations with will-change properties.</p>
        </div>
      </section>
    </div>
  )
}

export default EnhancementShowcase