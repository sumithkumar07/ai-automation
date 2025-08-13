import React, { Suspense, lazy } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import { AuthProvider, useAuth } from './contexts/AuthContext'
import { DarkModeProvider } from './components/DarkModeProvider'
import KeyboardShortcuts from './components/KeyboardShortcuts'
import MobileResponsiveWrapper from './components/MobileResponsiveWrapper'
import { AccessibilityProvider, SkipToContent } from './components/AccessibilityProvider'
import { initWebVitalsTracking, logBundleSize, useResourceMonitor } from './components/PerformanceMonitor'
import LoadingSpinner from './components/LoadingSpinner'

// Lazy load components for better performance
const Homepage = lazy(() => import('./pages/Homepage'))
const AuthPage = lazy(() => import('./pages/AuthPage'))
const EnhancedDashboard = lazy(() => import('./components/EnhancedDashboard'))
const EnhancedWorkflowEditor = lazy(() => import('./components/EnhancedWorkflowEditor'))
const EnhancedIntegrations = lazy(() => import('./pages/EnhancedIntegrations'))
const Learning = lazy(() => import('./pages/Learning'))
const AccountSettings = lazy(() => import('./pages/AccountSettings'))

// Initialize performance monitoring
if (typeof window !== 'undefined') {
  initWebVitalsTracking()
  logBundleSize()
}

// Enhanced loading component with better UX
const PageLoader = ({ children }) => (
  <Suspense fallback={
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="text-center">
        <div className="w-16 h-16 bg-gradient-to-r from-primary-500 to-accent-500 rounded-lg flex items-center justify-center mx-auto mb-4 animate-pulse">
          <span className="text-white font-bold text-2xl">A</span>
        </div>
        <LoadingSpinner size="large" />
        <p className="text-gray-600 mt-4">Loading page...</p>
      </div>
    </div>
  }>
    {children}
  </Suspense>
)

// Protected Route component with enhanced loading and error states
const ProtectedRoute = ({ children }) => {
  const { user, loading } = useAuth()
  
  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 bg-gradient-to-r from-primary-500 to-accent-500 rounded-lg flex items-center justify-center mx-auto mb-4 animate-pulse">
            <span className="text-white font-bold text-2xl">A</span>
          </div>
          <LoadingSpinner size="large" />
          <p className="text-gray-600 mt-4">Authenticating...</p>
        </div>
      </div>
    )
  }
  
  if (!user) {
    return <Navigate to="/auth" replace />
  }
  
  return <PageLoader>{children}</PageLoader>
}

// Public Route component (redirect if logged in)
const PublicRoute = ({ children }) => {
  const { user, loading } = useAuth()
  
  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <LoadingSpinner size="large" />
      </div>
    )
  }
  
  if (user) {
    return <Navigate to="/dashboard" replace />
  }
  
  return <PageLoader>{children}</PageLoader>
}

// Error Boundary for better error handling
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props)
    this.state = { hasError: false, error: null }
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error }
  }

  componentDidCatch(error, errorInfo) {
    console.error('Application error:', error, errorInfo)
    
    // In production, you might want to send this to an error reporting service
    if (process.env.NODE_ENV === 'production') {
      // Log to error reporting service
    }
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-gray-50 flex items-center justify-center">
          <div className="text-center max-w-md mx-auto p-6">
            <div className="w-16 h-16 bg-red-100 rounded-lg flex items-center justify-center mx-auto mb-4">
              <span className="text-red-600 font-bold text-2xl">!</span>
            </div>
            <h1 className="text-2xl font-bold text-gray-900 mb-2">Something went wrong</h1>
            <p className="text-gray-600 mb-6">
              We're sorry, but something unexpected happened. Please try refreshing the page.
            </p>
            <button
              onClick={() => window.location.reload()}
              className="btn-primary"
            >
              Refresh Page
            </button>
            {process.env.NODE_ENV === 'development' && (
              <details className="mt-4 text-left">
                <summary className="text-sm text-gray-500 cursor-pointer">Error Details</summary>
                <pre className="mt-2 text-xs text-gray-700 bg-gray-100 p-2 rounded overflow-auto">
                  {this.state.error?.toString()}
                </pre>
              </details>
            )}
          </div>
        </div>
      )
    }

    return this.props.children
  }
}

// Performance monitoring hook
const PerformanceWrapper = ({ children }) => {
  useResourceMonitor()
  return children
}

function App() {
  return (
    <ErrorBoundary>
      <DarkModeProvider>
        <AccessibilityProvider>
          <AuthProvider>
            <MobileResponsiveWrapper>
              <PerformanceWrapper>
                <Router future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
                  <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
                    <SkipToContent />
                    <KeyboardShortcuts />
                    
                    <Routes>
                      {/* Public routes */}
                      <Route path="/" element={
                        <PublicRoute>
                          <Homepage />
                        </PublicRoute>  
                      } />
                      <Route path="/auth" element={
                        <PublicRoute>
                          <AuthPage />
                        </PublicRoute>
                      } />
                      
                      {/* Protected routes */}
                      <Route path="/dashboard" element={
                        <ProtectedRoute>
                          <EnhancedDashboard />
                        </ProtectedRoute>
                      } />
                      <Route path="/editor" element={
                        <ProtectedRoute>
                          <EnhancedWorkflowEditor />
                        </ProtectedRoute>
                      } />
                      <Route path="/editor/:workflowId" element={
                        <ProtectedRoute>
                          <EnhancedWorkflowEditor />
                        </ProtectedRoute>
                      } />
                      <Route path="/integrations" element={
                        <ProtectedRoute>
                          <EnhancedIntegrations />
                        </ProtectedRoute>
                      } />
                      <Route path="/docs" element={
                        <ProtectedRoute>
                          <Learning />
                        </ProtectedRoute>
                      } />
                      <Route path="/help" element={
                        <ProtectedRoute>
                          <Learning />
                        </ProtectedRoute>
                      } />
                      <Route path="/academy" element={
                        <ProtectedRoute>
                          <Learning />
                        </ProtectedRoute>
                      } />
                      <Route path="/account" element={
                        <ProtectedRoute>
                          <AccountSettings />
                        </ProtectedRoute>
                      } />
                      <Route path="/settings" element={
                        <ProtectedRoute>
                          <AccountSettings />
                        </ProtectedRoute>
                      } />
                      
                      {/* Fallback route */}
                      <Route path="*" element={<Navigate to="/" replace />} />
                    </Routes>
                    
                    {/* Enhanced toast notifications with dark mode support */}
                    <Toaster
                      position="top-right"
                      reverseOrder={false}
                      gutter={8}
                      containerClassName="toast-container"
                      toastOptions={{
                        duration: 4000,
                        className: 'toast-item',
                        style: {
                          background: 'var(--toast-bg, #363636)',
                          color: 'var(--toast-color, #fff)',
                          fontSize: 'calc(var(--accessibility-font-scale, 1) * 14px)',
                          borderRadius: '8px',
                          boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)'
                        },
                        success: {
                          style: {
                            background: 'var(--toast-success, #10b981)',
                          },
                          iconTheme: {
                            primary: '#fff',
                            secondary: '#10b981'
                          }
                        },
                        error: {
                          style: {
                            background: 'var(--toast-error, #ef4444)',
                          },
                          iconTheme: {
                            primary: '#fff',
                            secondary: '#ef4444'
                          }
                        },
                        loading: {
                          style: {
                            background: 'var(--toast-loading, #6b7280)',
                          }
                        }
                      }}
                    />
                  </div>
                </Router>
              </PerformanceWrapper>
            </MobileResponsiveWrapper>
          </AuthProvider>
        </AccessibilityProvider>
      </DarkModeProvider>
    </ErrorBoundary>
  )
}

export default App