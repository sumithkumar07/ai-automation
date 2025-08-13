// Service Worker for Aether Automation PWA
const CACHE_NAME = 'aether-automation-v1.0.0'
const OFFLINE_URL = '/offline.html'

// Files to cache for offline functionality
const urlsToCache = [
  '/',
  '/static/js/bundle.js',
  '/static/css/main.css',
  '/manifest.json',
  '/offline.html',
  // Add more static assets as needed
]

// API endpoints that should be cached
const apiEndpointsToCache = [
  '/api/nodes',
  '/api/integrations',
  '/api/v2/nodes/categories',
  '/api/v2/templates/popular'
]

// Install event - cache core files
self.addEventListener('install', (event) => {
  console.log('Service Worker: Installing...')
  
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('Service Worker: Caching core files')
        return cache.addAll(urlsToCache)
      })
      .then(() => {
        console.log('Service Worker: Installation complete')
        // Force the service worker to activate immediately
        return self.skipWaiting()
      })
      .catch((error) => {
        console.error('Service Worker: Installation failed', error)
      })
  )
})

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  console.log('Service Worker: Activating...')
  
  event.waitUntil(
    caches.keys()
      .then((cacheNames) => {
        return Promise.all(
          cacheNames.map((cacheName) => {
            if (cacheName !== CACHE_NAME) {
              console.log('Service Worker: Deleting old cache', cacheName)
              return caches.delete(cacheName)
            }
          })
        )
      })
      .then(() => {
        console.log('Service Worker: Activation complete')
        // Take control of all pages immediately
        return self.clients.claim()
      })
  )
})

// Fetch event - handle network requests
self.addEventListener('fetch', (event) => {
  const { request } = event
  const url = new URL(request.url)

  // Skip cross-origin requests
  if (!url.origin.includes(self.location.origin) && !url.origin.includes('localhost')) {
    return
  }

  // Handle API requests with network-first strategy
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(networkFirstStrategy(request))
    return
  }

  // Handle navigation requests
  if (request.mode === 'navigate') {
    event.respondWith(
      fetch(request)
        .catch(() => {
          // If navigation fails, serve offline page
          return caches.match(OFFLINE_URL)
        })
    )
    return
  }

  // Handle other requests with cache-first strategy
  event.respondWith(cacheFirstStrategy(request))
})

// Network-first strategy for API requests
async function networkFirstStrategy(request) {
  try {
    // Try network first
    const networkResponse = await fetch(request)
    
    // If successful, update cache
    if (networkResponse.ok) {
      const cache = await caches.open(CACHE_NAME)
      cache.put(request, networkResponse.clone())
    }
    
    return networkResponse
  } catch (error) {
    console.log('Network request failed, trying cache:', request.url)
    
    // If network fails, try cache
    const cachedResponse = await caches.match(request)
    
    if (cachedResponse) {
      return cachedResponse
    }
    
    // If no cache, return offline response for API requests
    return new Response(
      JSON.stringify({
        error: 'Network unavailable',
        message: 'This feature requires an internet connection',
        offline: true
      }),
      {
        status: 503,
        headers: { 'Content-Type': 'application/json' }
      }
    )
  }
}

// Cache-first strategy for static assets
async function cacheFirstStrategy(request) {
  try {
    // Try cache first
    const cachedResponse = await caches.match(request)
    
    if (cachedResponse) {
      return cachedResponse
    }
    
    // If not in cache, fetch from network
    const networkResponse = await fetch(request)
    
    // Cache the response if successful
    if (networkResponse.ok) {
      const cache = await caches.open(CACHE_NAME)
      cache.put(request, networkResponse.clone())
    }
    
    return networkResponse
  } catch (error) {
    console.error('Cache-first strategy failed:', error)
    
    // Return a fallback response
    return new Response('Resource unavailable offline', {
      status: 503,
      headers: { 'Content-Type': 'text/plain' }
    })
  }
}

// Background sync for offline actions
self.addEventListener('sync', (event) => {
  console.log('Service Worker: Background sync triggered', event.tag)
  
  switch (event.tag) {
    case 'workflow-save':
      event.waitUntil(syncWorkflowSaves())
      break
    case 'analytics-data':
      event.waitUntil(syncAnalyticsData())
      break
    default:
      console.log('Unknown sync tag:', event.tag)
  }
})

// Sync workflow saves when back online
async function syncWorkflowSaves() {
  try {
    // Get pending workflow saves from IndexedDB or localStorage
    const pendingSaves = JSON.parse(localStorage.getItem('pendingWorkflowSaves') || '[]')
    
    for (const save of pendingSaves) {
      try {
        await fetch('/api/workflows', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${save.token}`
          },
          body: JSON.stringify(save.data)
        })
        
        console.log('Synced workflow save:', save.id)
      } catch (error) {
        console.error('Failed to sync workflow save:', error)
      }
    }
    
    // Clear pending saves
    localStorage.removeItem('pendingWorkflowSaves')
    
  } catch (error) {
    console.error('Background sync failed:', error)
  }
}

// Sync analytics data
async function syncAnalyticsData() {
  try {
    const pendingAnalytics = JSON.parse(localStorage.getItem('pendingAnalytics') || '[]')
    
    if (pendingAnalytics.length > 0) {
      await fetch('/api/analytics/batch', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(pendingAnalytics)
      })
      
      localStorage.removeItem('pendingAnalytics')
      console.log('Synced analytics data')
    }
  } catch (error) {
    console.error('Analytics sync failed:', error)
  }
}

// Push notification handling
self.addEventListener('push', (event) => {
  console.log('Push notification received')
  
  const options = {
    title: 'Aether Automation',
    body: 'You have a new notification',
    icon: '/icons/icon-192x192.png',
    badge: '/icons/icon-72x72.png',
    tag: 'aether-notification',
    data: {
      url: '/'
    },
    actions: [
      {
        action: 'view',
        title: 'View',
        icon: '/icons/action-view.png'
      },
      {
        action: 'dismiss',
        title: 'Dismiss',
        icon: '/icons/action-dismiss.png'
      }
    ],
    requireInteraction: false,
    silent: false
  }

  if (event.data) {
    try {
      const payload = event.data.json()
      options.title = payload.title || options.title
      options.body = payload.body || options.body
      options.data = { ...options.data, ...payload.data }
    } catch (error) {
      console.error('Error parsing push notification data:', error)
    }
  }

  event.waitUntil(
    self.registration.showNotification(options.title, options)
  )
})

// Notification click handling
self.addEventListener('notificationclick', (event) => {
  console.log('Notification clicked:', event.notification.tag)
  
  event.notification.close()

  if (event.action === 'dismiss') {
    return
  }

  // Handle notification click
  const urlToOpen = new URL(
    event.notification.data?.url || '/',
    self.location.origin
  ).href

  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true })
      .then((clientList) => {
        // Check if app is already open
        for (const client of clientList) {
          if (client.url === urlToOpen && 'focus' in client) {
            return client.focus()
          }
        }
        
        // Open new window if not already open
        if (clients.openWindow) {
          return clients.openWindow(urlToOpen)
        }
      })
  )
})

// Message handling from main thread
self.addEventListener('message', (event) => {
  console.log('Service Worker received message:', event.data)
  
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting()
  }
  
  if (event.data && event.data.type === 'CACHE_WORKFLOW') {
    // Cache specific workflow data
    const { workflowData } = event.data
    caches.open(CACHE_NAME).then((cache) => {
      cache.put(`/workflows/${workflowData.id}`, new Response(JSON.stringify(workflowData)))
    })
  }
})

// Error handling
self.addEventListener('error', (event) => {
  console.error('Service Worker error:', event.error)
})

self.addEventListener('unhandledrejection', (event) => {
  console.error('Service Worker unhandled rejection:', event.reason)
})

console.log('Service Worker: Loaded and ready')