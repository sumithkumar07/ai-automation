import React, { createContext, useContext, useState, useEffect } from 'react'
import api from '../utils/api'

const AuthContext = createContext()

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Check for existing token on mount
    const token = localStorage.getItem('token')
    const userData = localStorage.getItem('user')
    if (token && userData) {
      try {
        const parsedUser = JSON.parse(userData)
        setUser(parsedUser)
      } catch (error) {
        console.error('Error parsing user data:', error)
        localStorage.removeItem('token')
        localStorage.removeItem('user')
      }
    }
    setLoading(false)
  }, [])

  const login = async (email, password) => {
    try {
      const response = await api.post('/api/auth/login', {
        email,
        password
      })
      
      const { access_token, user: userData } = response.data
      
      localStorage.setItem('token', access_token)
      localStorage.setItem('user', JSON.stringify(userData))
      setUser(userData)
      
      return { success: true }
    } catch (error) {
      return { success: false, error: error.response?.data?.detail || 'Login failed' }
    }
  }

  const signup = async (name, email, password) => {
    try {
      // Split name into first_name and last_name for backend compatibility
      const nameParts = name.trim().split(' ')
      const first_name = nameParts[0] || ''
      const last_name = nameParts.slice(1).join(' ') || ''
      
      const response = await api.post('/api/auth/signup', {
        first_name,
        last_name,
        email,
        password
      })
      
      const { access_token, user: userData } = response.data
      
      localStorage.setItem('token', access_token)
      localStorage.setItem('user', JSON.stringify(userData))
      setUser(userData)
      
      return { success: true }
    } catch (error) {
      return { success: false, error: error.response?.data?.detail || 'Signup failed' }
    }
  }

  const logout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    setUser(null)
  }

  const value = {
    user,
    login,
    signup,
    logout,
    loading
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}