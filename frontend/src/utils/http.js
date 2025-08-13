import axios from 'axios'

// Build a robust base URL from env and ensure single /api prefix
const env = (typeof import !== 'undefined' && import.meta && import.meta.env) ? import.meta.env : {}
const rawBase = env.VITE_BACKEND_URL || ''
const trimmed = (rawBase || '').replace(/\/$/, '')
const baseURL = trimmed.endsWith('/api') ? trimmed : `${trimmed}/api`

const http = axios.create({ baseURL })

// Attach auth token automatically on every request
http.interceptors.request.use((config) => {
  try {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers = config.headers || {}
      config.headers.Authorization = `Bearer ${token}`
    }
  } catch (_) {}
  return config
})

export default http