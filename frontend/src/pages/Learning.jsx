import React, { useState } from 'react'
import EnhancedNavbar from '../components/EnhancedNavbar'
import { 
  BookOpenIcon,
  PlayIcon,
  CheckCircleIcon,
  ClockIcon,
  StarIcon,
  AcademicCapIcon,
  LightBulbIcon,
  RocketLaunchIcon
} from '@heroicons/react/24/outline'

const Learning = () => {
  const [selectedCategory, setSelectedCategory] = useState('all')

  const learningModules = [
    {
      id: 1,
      title: 'Getting Started with Automation',
      description: 'Learn the basics of workflow automation and how to create your first workflow.',
      category: 'basics',
      duration: '15 min',
      difficulty: 'beginner',
      completed: true,
      rating: 4.8,
      lessons: 5
    },
    {
      id: 2,
      title: 'Advanced Node Configuration',
      description: 'Master complex node configurations and conditional logic in your workflows.',
      category: 'advanced',
      duration: '30 min',
      difficulty: 'advanced',
      completed: false,
      rating: 4.9,
      lessons: 8
    },
    {
      id: 3,
      title: 'Integration Best Practices',
      description: 'Learn how to effectively connect and manage multiple service integrations.',
      category: 'integrations',
      duration: '25 min',
      difficulty: 'intermediate',
      completed: false,
      rating: 4.7,
      lessons: 7
    },
    {
      id: 4,
      title: 'AI-Powered Workflow Generation',
      description: 'Discover how to leverage AI to create and optimize your automation workflows.',
      category: 'ai',
      duration: '20 min',
      difficulty: 'intermediate',
      completed: false,
      rating: 4.9,
      lessons: 6
    }
  ]

  const categories = [
    { id: 'all', name: 'All Topics', icon: BookOpenIcon },
    { id: 'basics', name: 'Basics', icon: AcademicCapIcon },
    { id: 'advanced', name: 'Advanced', icon: RocketLaunchIcon },
    { id: 'integrations', name: 'Integrations', icon: LightBulbIcon },
    { id: 'ai', name: 'AI Features', icon: StarIcon }
  ]

  const filteredModules = selectedCategory === 'all' 
    ? learningModules 
    : learningModules.filter(module => module.category === selectedCategory)

  const getDifficultyColor = (difficulty) => {
    switch (difficulty) {
      case 'beginner':
        return 'bg-green-100 text-green-800'
      case 'intermediate':
        return 'bg-yellow-100 text-yellow-800'
      case 'advanced':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <EnhancedNavbar />
      
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Learning Center</h1>
          <p className="text-gray-600">Master automation workflows with our comprehensive learning resources.</p>
        </div>

        {/* Category Filter */}
        <div className="mb-8">
          <div className="flex flex-wrap gap-2">
            {categories.map((category) => {
              const Icon = category.icon
              return (
                <button
                  key={category.id}
                  onClick={() => setSelectedCategory(category.id)}
                  className={`flex items-center px-4 py-2 rounded-lg font-medium transition-colors ${
                    selectedCategory === category.id
                      ? 'bg-primary-600 text-white'
                      : 'bg-white text-gray-700 hover:bg-gray-100'
                  }`}
                >
                  <Icon className="w-4 h-4 mr-2" />
                  {category.name}
                </button>
              )
            })}
          </div>
        </div>

        {/* Learning Modules Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredModules.map((module) => (
            <div key={module.id} className="card p-6 hover:shadow-lg transition-shadow">
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <h3 className="font-semibold text-gray-900 mb-2">{module.title}</h3>
                  <p className="text-gray-600 text-sm line-clamp-3">{module.description}</p>
                </div>
                {module.completed && (
                  <CheckCircleIcon className="w-6 h-6 text-green-500 shrink-0 ml-2" />
                )}
              </div>

              <div className="flex items-center justify-between text-sm text-gray-600 mb-4">
                <div className="flex items-center space-x-4">
                  <span className="flex items-center">
                    <ClockIcon className="w-4 h-4 mr-1" />
                    {module.duration}
                  </span>
                  <span className="flex items-center">
                    <BookOpenIcon className="w-4 h-4 mr-1" />
                    {module.lessons} lessons
                  </span>
                </div>
                <div className="flex items-center">
                  <StarIcon className="w-4 h-4 text-yellow-400 mr-1" />
                  {module.rating}
                </div>
              </div>

              <div className="flex items-center justify-between">
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${getDifficultyColor(module.difficulty)}`}>
                  {module.difficulty}
                </span>
                <button className="btn-primary text-sm py-2 px-4 inline-flex items-center">
                  <PlayIcon className="w-4 h-4 mr-1" />
                  {module.completed ? 'Review' : 'Start'}
                </button>
              </div>
            </div>
          ))}
        </div>

        {/* Quick Tips Section */}
        <div className="mt-16">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Quick Tips</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div className="bg-gradient-to-r from-blue-50 to-blue-100 p-6 rounded-lg">
              <LightBulbIcon className="w-8 h-8 text-blue-600 mb-3" />
              <h3 className="font-semibold text-gray-900 mb-2">Start Simple</h3>
              <p className="text-gray-700 text-sm">Begin with basic workflows and gradually add complexity as you become more comfortable.</p>
            </div>
            
            <div className="bg-gradient-to-r from-green-50 to-green-100 p-6 rounded-lg">
              <CheckCircleIcon className="w-8 h-8 text-green-600 mb-3" />
              <h3 className="font-semibold text-gray-900 mb-2">Test Everything</h3>
              <p className="text-gray-700 text-sm">Always test your workflows in a safe environment before deploying them to production.</p>
            </div>
            
            <div className="bg-gradient-to-r from-purple-50 to-purple-100 p-6 rounded-lg">
              <StarIcon className="w-8 h-8 text-purple-600 mb-3" />
              <h3 className="font-semibold text-gray-900 mb-2">Use AI Assistant</h3>
              <p className="text-gray-700 text-sm">Leverage our AI assistant to generate workflows and get suggestions for optimization.</p>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}

export default Learning