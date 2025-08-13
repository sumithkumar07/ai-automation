import React, { useEffect, useCallback, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { 
  CommandLineIcon,
  XMarkIcon,
  MagnifyingGlassIcon,
  HomeIcon,
  ChartBarIcon,
  CogIcon,
  PlusIcon,
  PlayIcon
} from '@heroicons/react/24/outline'

const KeyboardShortcuts = () => {
  const [isCommandPaletteOpen, setIsCommandPaletteOpen] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const navigate = useNavigate()

  // Available commands
  const commands = [
    {
      id: 'home',
      title: 'Go to Homepage',
      shortcut: 'g h',
      icon: HomeIcon,
      action: () => navigate('/'),
      keywords: ['home', 'homepage', 'landing']
    },
    {
      id: 'dashboard',
      title: 'Go to Dashboard',
      shortcut: 'g d',
      icon: ChartBarIcon,
      action: () => navigate('/dashboard'),
      keywords: ['dashboard', 'overview', 'stats']
    },
    {
      id: 'editor',
      title: 'Create New Workflow',
      shortcut: 'c w',
      icon: PlusIcon,
      action: () => navigate('/editor'),
      keywords: ['create', 'workflow', 'editor', 'new']
    },
    {
      id: 'integrations',
      title: 'Browse Integrations',
      shortcut: 'g i',
      icon: CogIcon,
      action: () => navigate('/integrations'),
      keywords: ['integrations', 'connections', 'apps']
    },
    {
      id: 'settings',
      title: 'Account Settings',
      shortcut: 'g s',
      icon: CogIcon,
      action: () => navigate('/settings'),
      keywords: ['settings', 'account', 'profile']
    },
    {
      id: 'help',
      title: 'Open Help Documentation',
      shortcut: '?',
      icon: CommandLineIcon,
      action: () => navigate('/docs'),
      keywords: ['help', 'docs', 'documentation', 'support']
    }
  ]

  // Filter commands based on search
  const filteredCommands = commands.filter(command =>
    command.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    command.keywords.some(keyword => keyword.toLowerCase().includes(searchQuery.toLowerCase()))
  )

  // Keyboard event handler
  const handleKeyDown = useCallback((event) => {
    // Command palette toggle (Cmd/Ctrl + K)
    if ((event.metaKey || event.ctrlKey) && event.key === 'k') {
      event.preventDefault()
      setIsCommandPaletteOpen(prev => !prev)
      return
    }

    // Escape to close command palette
    if (event.key === 'Escape' && isCommandPaletteOpen) {
      setIsCommandPaletteOpen(false)
      setSearchQuery('')
      return
    }

    // Don't handle shortcuts when command palette is open or when typing in inputs
    if (isCommandPaletteOpen || 
        event.target.tagName === 'INPUT' || 
        event.target.tagName === 'TEXTAREA' ||
        event.target.contentEditable === 'true') {
      return
    }

    // Handle direct shortcuts
    const key = event.key.toLowerCase()
    
    // Help shortcut
    if (key === '?' && !event.shiftKey) {
      event.preventDefault()
      navigate('/docs')
      return
    }

    // Handle g-based navigation shortcuts
    if (key === 'g') {
      event.preventDefault()
      // Wait for next key
      const handleNextKey = (nextEvent) => {
        const nextKey = nextEvent.key.toLowerCase()
        
        switch (nextKey) {
          case 'h':
            navigate('/')
            break
          case 'd':
            navigate('/dashboard')
            break
          case 'i':
            navigate('/integrations')
            break
          case 's':
            navigate('/settings')
            break
        }
        
        document.removeEventListener('keydown', handleNextKey)
      }
      
      document.addEventListener('keydown', handleNextKey)
      
      // Remove listener after 2 seconds if no key is pressed
      setTimeout(() => {
        document.removeEventListener('keydown', handleNextKey)
      }, 2000)
      
      return
    }

    // Handle c-based creation shortcuts
    if (key === 'c') {
      event.preventDefault()
      const handleNextKey = (nextEvent) => {
        const nextKey = nextEvent.key.toLowerCase()
        
        if (nextKey === 'w') {
          navigate('/editor')
        }
        
        document.removeEventListener('keydown', handleNextKey)
      }
      
      document.addEventListener('keydown', handleNextKey)
      
      setTimeout(() => {
        document.removeEventListener('keydown', handleNextKey)
      }, 2000)
      
      return
    }

  }, [isCommandPaletteOpen, navigate])

  useEffect(() => {
    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [handleKeyDown])

  const executeCommand = (command) => {
    command.action()
    setIsCommandPaletteOpen(false)
    setSearchQuery('')
  }

  return (
    <>
      {/* Command Palette */}
      {isCommandPaletteOpen && (
        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div className="flex min-h-screen items-start justify-center px-4 pt-16">
            <div className="fixed inset-0 bg-black bg-opacity-25 transition-opacity" onClick={() => setIsCommandPaletteOpen(false)} />
            
            <div className="relative w-full max-w-lg transform rounded-xl bg-white dark:bg-gray-800 shadow-2xl transition-all">
              {/* Search Input */}
              <div className="flex items-center px-4 py-4 border-b border-gray-200 dark:border-gray-700">
                <MagnifyingGlassIcon className="w-5 h-5 text-gray-400 mr-3" />
                <input
                  type="text"
                  placeholder="Search for commands..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="flex-1 bg-transparent border-none outline-none text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400"
                  autoFocus
                />
                <button
                  onClick={() => setIsCommandPaletteOpen(false)}
                  className="ml-3 p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                >
                  <XMarkIcon className="w-5 h-5" />
                </button>
              </div>

              {/* Commands List */}
              <div className="max-h-80 overflow-y-auto">
                {filteredCommands.length === 0 ? (
                  <div className="px-4 py-8 text-center text-gray-500 dark:text-gray-400">
                    No commands found for "{searchQuery}"
                  </div>
                ) : (
                  <div className="py-2">
                    {filteredCommands.map((command, index) => {
                      const Icon = command.icon
                      return (
                        <button
                          key={command.id}
                          onClick={() => executeCommand(command)}
                          className="w-full flex items-center px-4 py-3 text-left hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors focus:bg-gray-50 dark:focus:bg-gray-700 focus:outline-none"
                        >
                          <Icon className="w-5 h-5 text-gray-400 mr-3" />
                          <div className="flex-1">
                            <div className="text-sm font-medium text-gray-900 dark:text-white">
                              {command.title}
                            </div>
                          </div>
                          <div className="text-xs text-gray-500 dark:text-gray-400 bg-gray-100 dark:bg-gray-600 px-2 py-1 rounded">
                            {command.shortcut}
                          </div>
                        </button>
                      )
                    })}
                  </div>
                )}
              </div>

              {/* Footer */}
              <div className="px-4 py-3 border-t border-gray-200 dark:border-gray-700 text-xs text-gray-500 dark:text-gray-400">
                Press <kbd className="px-2 py-1 bg-gray-100 dark:bg-gray-600 rounded">⌘K</kbd> to open,{' '}
                <kbd className="px-2 py-1 bg-gray-100 dark:bg-gray-600 rounded">↵</kbd> to select,{' '}
                <kbd className="px-2 py-1 bg-gray-100 dark:bg-gray-600 rounded">↑↓</kbd> to navigate
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Keyboard Shortcuts Help */}
      <div className="fixed bottom-4 right-4 z-40">
        <button
          onClick={() => setIsCommandPaletteOpen(true)}
          className="group bg-white dark:bg-gray-800 shadow-lg rounded-lg p-3 border border-gray-200 dark:border-gray-700 hover:shadow-xl transition-all"
          title="Open Command Palette (⌘K)"
        >
          <CommandLineIcon className="w-5 h-5 text-gray-600 dark:text-gray-400 group-hover:text-gray-900 dark:group-hover:text-white" />
        </button>
      </div>
    </>
  )
}

// Keyboard shortcuts help component
export const KeyboardShortcutsHelp = () => {
  const shortcuts = [
    { keys: ['⌘', 'K'], description: 'Open command palette' },
    { keys: ['G', 'H'], description: 'Go to homepage' },
    { keys: ['G', 'D'], description: 'Go to dashboard' },
    { keys: ['G', 'I'], description: 'Go to integrations' },
    { keys: ['C', 'W'], description: 'Create new workflow' },
    { keys: ['?'], description: 'Open help documentation' },
    { keys: ['Esc'], description: 'Close modals/panels' }
  ]

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
      <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
        <CommandLineIcon className="w-5 h-5 mr-2" />
        Keyboard Shortcuts
      </h3>
      <div className="space-y-3">
        {shortcuts.map((shortcut, index) => (
          <div key={index} className="flex items-center justify-between">
            <span className="text-sm text-gray-600 dark:text-gray-400">
              {shortcut.description}
            </span>
            <div className="flex items-center space-x-1">
              {shortcut.keys.map((key, keyIndex) => (
                <kbd
                  key={keyIndex}
                  className="px-2 py-1 text-xs font-semibold text-gray-800 dark:text-gray-200 bg-gray-100 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded"
                >
                  {key}
                </kbd>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default KeyboardShortcuts