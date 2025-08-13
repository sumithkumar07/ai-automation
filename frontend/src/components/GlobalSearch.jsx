// Global Search Component with Advanced Filtering
import React, { useState, useEffect, useRef } from 'react'
import { 
  MagnifyingGlassIcon,
  FunnelIcon,
  ClockIcon,
  DocumentIcon,
  CogIcon,
  LinkIcon,
  XMarkIcon,
  SparklesIcon
} from '@heroicons/react/24/outline'
import { enhancedApiMethods, handleApiError } from '../utils/enhancedApi'
import LoadingSpinner from './LoadingSpinner'

const GlobalSearch = ({ isOpen, onClose, onResultSelect }) => {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(false)
  const [selectedTypes, setSelectedTypes] = useState(['workflows', 'templates', 'nodes', 'integrations'])
  const [recentSearches, setRecentSearches] = useState([])
  const [showFilters, setShowFilters] = useState(false)
  
  const searchInputRef = useRef(null)
  const debounceRef = useRef(null)

  const searchTypes = [
    { id: 'workflows', name: 'Workflows', icon: CogIcon, color: 'blue' },
    { id: 'templates', name: 'Templates', icon: DocumentIcon, color: 'green' },
    { id: 'nodes', name: 'Nodes', icon: SparklesIcon, color: 'purple' },
    { id: 'integrations', name: 'Integrations', icon: LinkIcon, color: 'orange' }
  ]

  useEffect(() => {
    if (isOpen && searchInputRef.current) {
      searchInputRef.current.focus()
    }
  }, [isOpen])

  useEffect(() => {
    // Load recent searches from localStorage
    const recent = JSON.parse(localStorage.getItem('recentSearches') || '[]')
    setRecentSearches(recent.slice(0, 5))
  }, [])

  useEffect(() => {
    if (query.trim()) {
      // Debounce search
      if (debounceRef.current) {
        clearTimeout(debounceRef.current)
      }
      
      debounceRef.current = setTimeout(() => {
        performSearch(query)
      }, 300)
    } else {
      setResults(null)
    }

    return () => {
      if (debounceRef.current) {
        clearTimeout(debounceRef.current)
      }
    }
  }, [query, selectedTypes])

  const performSearch = async (searchQuery) => {
    if (!searchQuery.trim()) return

    setLoading(true)
    try {
      const searchResults = await enhancedApiMethods.globalSearch(searchQuery, selectedTypes)
      setResults(searchResults)
      
      // Save to recent searches
      const newRecentSearches = [searchQuery, ...recentSearches.filter(s => s !== searchQuery)].slice(0, 5)
      setRecentSearches(newRecentSearches)
      localStorage.setItem('recentSearches', JSON.stringify(newRecentSearches))
      
    } catch (error) {
      handleApiError(error)
      setResults({ results: {}, total_results: 0 })
    } finally {
      setLoading(false)
    }
  }

  const handleTypeToggle = (typeId) => {
    setSelectedTypes(prev => 
      prev.includes(typeId) 
        ? prev.filter(t => t !== typeId)
        : [...prev, typeId]
    )
  }

  const handleResultClick = (result, type) => {
    if (onResultSelect) {
      onResultSelect(result, type)
    }
    onClose()
  }

  const handleRecentSearchClick = (recentQuery) => {
    setQuery(recentQuery)
    performSearch(recentQuery)
  }

  const clearRecentSearches = () => {
    setRecentSearches([])
    localStorage.removeItem('recentSearches')
  }

  const getResultIcon = (type) => {
    const typeConfig = searchTypes.find(t => t.id === type)
    return typeConfig ? typeConfig.icon : DocumentIcon
  }

  const getResultColor = (type) => {
    const typeConfig = searchTypes.find(t => t.id === type)
    return typeConfig ? typeConfig.color : 'gray'
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-start justify-center pt-20 z-50">
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-2xl w-full max-w-3xl mx-4 max-h-[80vh] overflow-hidden">
        {/* Search Header */}
        <div className="p-6 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center space-x-4">
            <div className="relative flex-1">
              <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                ref={searchInputRef}
                type="text"
                placeholder="Search workflows, templates, nodes, integrations..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-lg"
              />
              {loading && (
                <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
                  <LoadingSpinner size="small" />
                </div>
              )}
            </div>
            <button
              onClick={() => setShowFilters(!showFilters)}
              className={`p-3 rounded-lg border ${showFilters ? 'bg-primary-50 border-primary-200 text-primary-600' : 'border-gray-300 dark:border-gray-600 text-gray-600 dark:text-gray-400'} hover:bg-gray-50 dark:hover:bg-gray-700`}
            >
              <FunnelIcon className="w-5 h-5" />
            </button>
            <button
              onClick={onClose}
              className="p-3 rounded-lg border border-gray-300 dark:border-gray-600 text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-700"
            >
              <XMarkIcon className="w-5 h-5" />
            </button>
          </div>

          {/* Search Type Filters */}
          {showFilters && (
            <div className="mt-4 flex flex-wrap gap-2">
              {searchTypes.map((type) => {
                const Icon = type.icon
                const isSelected = selectedTypes.includes(type.id)
                return (
                  <button
                    key={type.id}
                    onClick={() => handleTypeToggle(type.id)}
                    className={`inline-flex items-center px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                      isSelected 
                        ? `bg-${type.color}-100 text-${type.color}-800 dark:bg-${type.color}-900/30 dark:text-${type.color}-400`
                        : 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                    }`}
                  >
                    <Icon className="w-4 h-4 mr-2" />
                    {type.name}
                  </button>
                )
              })}
            </div>
          )}
        </div>

        {/* Search Content */}
        <div className="max-h-96 overflow-y-auto">
          {!query && recentSearches.length > 0 && (
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm font-medium text-gray-900 dark:text-white flex items-center">
                  <ClockIcon className="w-4 h-4 mr-2" />
                  Recent Searches
                </h3>
                <button
                  onClick={clearRecentSearches}
                  className="text-xs text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
                >
                  Clear
                </button>
              </div>
              <div className="space-y-2">
                {recentSearches.map((recentQuery, index) => (
                  <button
                    key={index}
                    onClick={() => handleRecentSearchClick(recentQuery)}
                    className="block w-full text-left px-3 py-2 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300"
                  >
                    {recentQuery}
                  </button>
                ))}
              </div>
            </div>
          )}

          {results && (
            <div className="p-6">
              {results.total_results === 0 ? (
                <div className="text-center py-8">
                  <MagnifyingGlassIcon className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">No results found</h3>
                  <p className="text-gray-600 dark:text-gray-400">
                    Try adjusting your search query or filters
                  </p>
                </div>
              ) : (
                <div className="space-y-6">
                  <div className="flex items-center justify-between">
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                      Search Results ({results.total_results})
                    </h3>
                  </div>

                  {Object.entries(results.results).map(([type, typeResults]) => {
                    if (!typeResults.items || typeResults.items.length === 0) return null
                    
                    const Icon = getResultIcon(type)
                    const color = getResultColor(type)
                    
                    return (
                      <div key={type} className="space-y-3">
                        <h4 className={`text-sm font-medium text-${color}-600 dark:text-${color}-400 uppercase tracking-wide flex items-center`}>
                          <Icon className="w-4 h-4 mr-2" />
                          {type} ({typeResults.total})
                        </h4>
                        <div className="space-y-2">
                          {typeResults.items.map((item, index) => (
                            <button
                              key={index}
                              onClick={() => handleResultClick(item, type)}
                              className="block w-full text-left p-3 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 border border-gray-200 dark:border-gray-600"
                            >
                              <div className="flex items-start justify-between">
                                <div className="flex-1">
                                  <h5 className="font-medium text-gray-900 dark:text-white">
                                    {item.name || item.title}
                                  </h5>
                                  <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                                    {item.description}
                                  </p>
                                  {item.category && (
                                    <span className={`inline-block px-2 py-1 rounded-full text-xs font-medium mt-2 bg-${color}-100 text-${color}-800 dark:bg-${color}-900/30 dark:text-${color}-400`}>
                                      {item.category}
                                    </span>
                                  )}
                                </div>
                              </div>
                            </button>
                          ))}
                        </div>
                      </div>
                    )
                  })}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default GlobalSearch