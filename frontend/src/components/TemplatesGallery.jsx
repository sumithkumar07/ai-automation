// Enhanced Templates Gallery with Categories and Advanced Features
import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import {
  MagnifyingGlassIcon,
  FunnelIcon,
  StarIcon,
  ClockIcon,
  PlayIcon,
  EyeIcon,
  FireIcon,
  SparklesIcon,
  TagIcon,
  UsersIcon,
  ChevronDownIcon,
  ChevronUpIcon
} from '@heroicons/react/24/outline'
import { StarIcon as StarIconSolid } from '@heroicons/react/24/solid'
import { enhancedApiMethods, handleApiError } from '../utils/enhancedApi'
import LoadingSpinner from './LoadingSpinner'
import toast from 'react-hot-toast'

const TemplatesGallery = ({ isOpen, onClose, onTemplateSelect }) => {
  const [templates, setTemplates] = useState([])
  const [categories, setCategories] = useState({})
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('all')
  const [selectedDifficulty, setSelectedDifficulty] = useState('all')
  const [sortBy, setSortBy] = useState('popular')
  const [showFilters, setShowFilters] = useState(false)
  const [activeTab, setActiveTab] = useState('all')
  const [popularTemplates, setPopularTemplates] = useState([])
  const [trendingTemplates, setTrendingTemplates] = useState([])

  const difficultyLevels = [
    { id: 'beginner', name: 'Beginner', color: 'green', description: 'Simple workflows, easy to understand' },
    { id: 'intermediate', name: 'Intermediate', color: 'yellow', description: 'Moderate complexity, some experience needed' },
    { id: 'advanced', name: 'Advanced', color: 'red', description: 'Complex workflows, requires experience' }
  ]

  const sortOptions = [
    { id: 'popular', name: 'Most Popular', icon: UsersIcon },
    { id: 'rating', name: 'Highest Rated', icon: StarIcon },
    { id: 'recent', name: 'Recently Updated', icon: ClockIcon },
    { id: 'alphabetical', name: 'Alphabetical', icon: TagIcon }
  ]

  useEffect(() => {
    if (isOpen) {
      loadTemplatesData()
    }
  }, [isOpen, selectedCategory, selectedDifficulty, searchTerm, sortBy])

  useEffect(() => {
    if (activeTab === 'popular') {
      loadPopularTemplates()
    } else if (activeTab === 'trending') {
      loadTrendingTemplates()
    }
  }, [activeTab])

  const loadTemplatesData = async () => {
    setLoading(true)
    try {
      const [templatesResult] = await Promise.all([
        enhancedApiMethods.getEnhancedTemplates({
          category: selectedCategory !== 'all' ? selectedCategory : null,
          difficulty: selectedDifficulty !== 'all' ? selectedDifficulty : null,
          search: searchTerm || null,
          limit: 50
        })
      ])

      setTemplates(templatesResult.templates || [])
      setCategories(templatesResult.categories || {})
    } catch (error) {
      handleApiError(error)
      setTemplates([])
    } finally {
      setLoading(false)
    }
  }

  const loadPopularTemplates = async () => {
    try {
      const result = await enhancedApiMethods.getPopularTemplates(15)
      setPopularTemplates(result.popular_templates || [])
    } catch (error) {
      handleApiError(error)
    }
  }

  const loadTrendingTemplates = async () => {
    try {
      const result = await enhancedApiMethods.getTrendingTemplates(15)
      setTrendingTemplates(result.trending_templates || [])
    } catch (error) {  
      handleApiError(error)
    }
  }

  const handleTemplateSelect = async (template) => {
    try {
      if (onTemplateSelect) {
        await onTemplateSelect(template)
      }
      onClose()
    } catch (error) {
      handleApiError(error)
    }
  }

  const handleDeployTemplate = async (template, e) => {
    e.stopPropagation()
    
    try {
      const result = await enhancedApiMethods.deployEnhancedTemplate(template.id, {
        name: `${template.name} (${new Date().toLocaleDateString()})`
      })
      
      toast.success(`Template "${template.name}" deployed successfully!`)
      
      // Navigate to workflow editor with the new workflow
      if (result.workflow) {
        window.location.href = `/editor/${result.workflow.id}`
      }
    } catch (error) {
      handleApiError(error)
    }
  }

  const getTemplatesByActiveTab = () => {
    switch (activeTab) {
      case 'popular':
        return popularTemplates
      case 'trending':
        return trendingTemplates
      default:
        return templates
    }
  }

  const getCategoryIcon = (categoryId) => {
    const icons = {
      business_automation: '🏢',
      data_processing: '📊',
      marketing: '📈',
      customer_service: '🎧',
      finance: '💰',
      healthcare: '🏥',
      ecommerce: '🛒',
      ai_powered: '🤖'
    }
    return icons[categoryId] || '⚙️'
  }

  const getDifficultyColor = (difficulty) => {
    const colors = {
      beginner: 'green',
      intermediate: 'yellow',
      advanced: 'red'
    }
    return colors[difficulty] || 'gray'
  }

  const renderRatingStars = (rating) => {
    return (
      <div className="flex items-center space-x-1">
        {[1, 2, 3, 4, 5].map((star) => (
          <StarIconSolid
            key={star}
            className={`w-4 h-4 ${
              star <= rating ? 'text-yellow-400' : 'text-gray-300'
            }`}
          />
        ))}
        <span className="text-sm text-gray-600 dark:text-gray-400 ml-1">
          {rating.toFixed(1)}
        </span>
      </div>
    )
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-2xl w-full max-w-7xl max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="p-6 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center">
              <SparklesIcon className="w-8 h-8 mr-3 text-primary-600" />
              Templates Gallery
            </h2>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
            >
              <span className="sr-only">Close</span>
              <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* Tabs */}
          <div className="flex space-x-1 bg-gray-100 dark:bg-gray-700 p-1 rounded-lg mb-4">
            {[
              { id: 'all', name: 'All Templates', icon: '📋' },
              { id: 'popular', name: 'Popular', icon: '🔥' },
              { id: 'trending', name: 'Trending', icon: '📈' }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex-1 flex items-center justify-center px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                  activeTab === tab.id
                    ? 'bg-white dark:bg-gray-600 text-primary-600 dark:text-primary-400 shadow-sm'
                    : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
                }`}
              >
                <span className="mr-2">{tab.icon}</span>
                {tab.name}
              </button>
            ))}
          </div>

          {/* Search and Filters */}
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1 relative">
              <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search templates..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              />
            </div>
            
            <button
              onClick={() => setShowFilters(!showFilters)}
              className={`px-4 py-2 rounded-lg border flex items-center space-x-2 ${
                showFilters
                  ? 'bg-primary-50 border-primary-200 text-primary-600'
                  : 'border-gray-300 dark:border-gray-600 text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-700'
              }`}
            >
              <FunnelIcon className="w-5 h-5" />
              <span>Filters</span>
              {showFilters ? (
                <ChevronUpIcon className="w-4 h-4" />
              ) : (
                <ChevronDownIcon className="w-4 h-4" />
              )}
            </button>
          </div>

          {/* Expanded Filters */}
          {showFilters && (
            <div className="mt-4 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {/* Category Filter */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Category
                  </label>
                  <select
                    value={selectedCategory}
                    onChange={(e) => setSelectedCategory(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 bg-white dark:bg-gray-600 text-gray-900 dark:text-white"
                  >
                    <option value="all">All Categories</option>
                    {Object.entries(categories).map(([id, category]) => (
                      <option key={id} value={id}>
                        {getCategoryIcon(id)} {category.name}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Difficulty Filter */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Difficulty
                  </label>
                  <select
                    value={selectedDifficulty}
                    onChange={(e) => setSelectedDifficulty(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 bg-white dark:bg-gray-600 text-gray-900 dark:text-white"
                  >
                    <option value="all">All Levels</option>
                    {difficultyLevels.map((level) => (
                      <option key={level.id} value={level.id}>
                        {level.name}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Sort By */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Sort By
                  </label>
                  <select
                    value={sortBy}
                    onChange={(e) => setSortBy(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 bg-white dark:bg-gray-600 text-gray-900 dark:text-white"
                  >
                    {sortOptions.map((option) => (
                      <option key={option.id} value={option.id}>
                        {option.name}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Templates Grid */}
        <div className="flex-1 overflow-y-auto p-6">
          {loading ? (
            <div className="flex items-center justify-center h-64">
              <LoadingSpinner size="large" />
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {getTemplatesByActiveTab().map((template) => (
                <div
                  key={template.id}
                  className="group bg-white dark:bg-gray-700 rounded-xl shadow-sm hover:shadow-lg transition-all duration-200 border border-gray-200 dark:border-gray-600 overflow-hidden cursor-pointer"
                  onClick={() => handleTemplateSelect(template)}
                >
                  {/* Template Header */}
                  <div className="p-5">
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex-1">
                        <h3 className="font-semibold text-gray-900 dark:text-white group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors line-clamp-2">
                          {template.name}
                        </h3>
                        {activeTab === 'trending' && template.trending_score && (
                          <div className="flex items-center mt-1">
                            <FireIcon className="w-4 h-4 text-orange-500 mr-1" />
                            <span className="text-sm text-orange-600 dark:text-orange-400 font-medium">
                              Trending
                            </span>
                          </div>
                        )}
                      </div>
                      <div className="flex items-center space-x-2">
                        {template.category && (
                          <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-${categories[template.category]?.color || 'gray'}-100 text-${categories[template.category]?.color || 'gray'}-800 dark:bg-${categories[template.category]?.color || 'gray'}-900/30 dark:text-${categories[template.category]?.color || 'gray'}-400`}>
                            {getCategoryIcon(template.category)}
                            <span className="ml-1">{categories[template.category]?.name || template.category}</span>
                          </span>
                        )}
                      </div>
                    </div>

                    <p className="text-gray-600 dark:text-gray-400 text-sm mb-4 line-clamp-3">
                      {template.description}
                    </p>

                    {/* Template Stats */}
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center space-x-4 text-sm text-gray-500 dark:text-gray-400">
                        <div className="flex items-center">
                          <UsersIcon className="w-4 h-4 mr-1" />
                          {template.usage_count?.toLocaleString() || 0}
                        </div>
                        {template.estimated_time_savings && (
                          <div className="flex items-center">
                            <ClockIcon className="w-4 h-4 mr-1" />
                            {template.estimated_time_savings}
                          </div>
                        )}
                      </div>
                      {renderRatingStars(template.rating || 0)}
                    </div>

                    {/* Template Tags */}
                    {template.tags && template.tags.length > 0 && (
                      <div className="flex flex-wrap gap-1 mb-4">
                        {template.tags.slice(0, 3).map((tag, index) => (
                          <span
                            key={index}
                            className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-gray-100 dark:bg-gray-600 text-gray-700 dark:text-gray-300"
                          >
                            {tag}
                          </span>
                        ))}
                        {template.tags.length > 3 && (
                          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-gray-100 dark:bg-gray-600 text-gray-700 dark:text-gray-300">
                            +{template.tags.length - 3}
                          </span>
                        )}
                      </div>
                    )}

                    {/* Difficulty Badge */}
                    {template.difficulty && (
                      <div className="mb-4">
                        <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-${getDifficultyColor(template.difficulty)}-100 text-${getDifficultyColor(template.difficulty)}-800 dark:bg-${getDifficultyColor(template.difficulty)}-900/30 dark:text-${getDifficultyColor(template.difficulty)}-400`}>
                          {template.difficulty.charAt(0).toUpperCase() + template.difficulty.slice(1)}
                        </span>
                      </div>
                    )}
                  </div>

                  {/* Template Actions */}
                  <div className="px-5 py-3 bg-gray-50 dark:bg-gray-600 border-t border-gray-200 dark:border-gray-500">
                    <div className="flex items-center justify-between">
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          handleTemplateSelect(template)
                        }}
                        className="text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300 text-sm font-medium flex items-center"
                      >
                        <EyeIcon className="w-4 h-4 mr-1" />
                        Preview
                      </button>
                      <button
                        onClick={(e) => handleDeployTemplate(template, e)}
                        className="bg-primary-600 hover:bg-primary-700 text-white px-3 py-1 rounded-md text-sm font-medium flex items-center transition-colors"
                      >
                        <PlayIcon className="w-4 h-4 mr-1" />
                        Deploy
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {!loading && getTemplatesByActiveTab().length === 0 && (
            <div className="text-center py-12">
              <SparklesIcon className="w-16 h-16 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                No templates found
              </h3>
              <p className="text-gray-600 dark:text-gray-400">
                Try adjusting your search or filter criteria
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default TemplatesGallery