import React from 'react'
import { Link } from 'react-router-dom'
import { 
  ArrowRightIcon,
  BoltIcon,
  ChartBarIcon,
  CogIcon,
  GlobeAltIcon,
  ShieldCheckIcon,
  SparklesIcon
} from '@heroicons/react/24/outline'

const Homepage = () => {
  const features = [
    {
      icon: BoltIcon,
      title: 'Lightning Fast Automation',
      description: 'Build complex workflows in minutes with our intuitive drag-and-drop editor and pre-built templates.'
    },
    {
      icon: SparklesIcon,
      title: 'AI-Powered Intelligence',
      description: 'Leverage cutting-edge AI to generate workflows, analyze data, and make intelligent decisions automatically.'
    },
    {
      icon: GlobeAltIcon,
      title: '100+ Integrations',
      description: 'Connect to all your favorite tools and services with our extensive integration marketplace.'
    },
    {
      icon: ChartBarIcon,
      title: 'Real-time Analytics',
      description: 'Monitor performance, track success rates, and optimize your workflows with detailed insights.'
    },
    {
      icon: ShieldCheckIcon,
      title: 'Enterprise Security',
      description: 'Bank-level security with encryption, compliance, and advanced access controls for your data.'
    },
    {
      icon: CogIcon,
      title: 'Advanced Workflow Engine',
      description: 'Handle complex logic, loops, conditions, and parallel processing with our robust execution engine.'
    }
  ]

  const stats = [
    { label: 'Active Users', value: '10,000+' },
    { label: 'Workflows Created', value: '50,000+' },
    { label: 'Hours Saved', value: '100,000+' },
    { label: 'Integrations', value: '100+' }
  ]

  return (
    <div className="min-h-screen bg-white">
      {/* Navigation */}
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-gradient-to-r from-primary-500 to-accent-500 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-lg">A</span>
              </div>
              <span className="text-xl font-bold text-gray-900">Aether Automation</span>
            </div>
            <div className="flex items-center space-x-4">
              <Link
                to="/auth"
                className="text-gray-600 hover:text-gray-900 font-medium"
              >
                Sign In
              </Link>
              <Link
                to="/auth"
                className="btn-primary"
              >
                Get Started Free
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="relative overflow-hidden">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-16">
          <div className="text-center">
            <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-6">
              Automate Everything
              <span className="block text-transparent bg-clip-text bg-gradient-to-r from-primary-600 to-accent-600">
                With AI Power
              </span>
            </h1>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto mb-8">
              The most advanced automation platform that combines drag-and-drop workflow building 
              with cutting-edge AI to help you automate complex business processes in minutes.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                to="/auth"
                className="btn-primary text-lg px-8 py-4 inline-flex items-center justify-center"
              >
                Start Building Free
                <ArrowRightIcon className="w-5 h-5 ml-2" />
              </Link>
              <button className="btn-secondary text-lg px-8 py-4">
                Watch Demo
              </button>
            </div>
          </div>
        </div>
        
        {/* Background decoration */}
        <div className="absolute inset-0 -z-10">
          <div className="absolute top-0 left-1/2 transform -translate-x-1/2 w-96 h-96 bg-gradient-to-r from-primary-100 to-accent-100 rounded-full blur-3xl opacity-30"></div>
          <div className="absolute bottom-0 right-1/4 w-64 h-64 bg-gradient-to-r from-accent-100 to-primary-100 rounded-full blur-2xl opacity-20"></div>
        </div>
      </div>

      {/* Stats Section */}
      <div className="bg-gray-50 py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {stats.map((stat, index) => (
              <div key={index} className="text-center">
                <div className="text-3xl md:text-4xl font-bold text-gray-900 mb-2">
                  {stat.value}
                </div>
                <div className="text-gray-600 font-medium">
                  {stat.label}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Everything You Need to Automate
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              From simple tasks to complex workflows, our platform has all the tools 
              and integrations you need to automate your business processes.
            </p>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => {
              const Icon = feature.icon
              return (
                <div key={index} className="card p-8 text-center">
                  <div className="w-12 h-12 bg-gradient-to-r from-primary-500 to-accent-500 rounded-lg flex items-center justify-center mx-auto mb-4">
                    <Icon className="w-6 h-6 text-white" />
                  </div>
                  <h3 className="text-xl font-semibold text-gray-900 mb-3">
                    {feature.title}
                  </h3>
                  <p className="text-gray-600">
                    {feature.description}
                  </p>
                </div>
              )
            })}
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="bg-gradient-to-r from-primary-600 to-accent-600 py-16">
        <div className="max-w-4xl mx-auto text-center px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
            Ready to Transform Your Business?
          </h2>
          <p className="text-xl text-primary-100 mb-8">
            Join thousands of companies already using Aether to automate their workflows 
            and boost productivity by 10x.
          </p>
          <Link
            to="/auth"
            className="bg-white text-primary-600 hover:bg-gray-100 font-bold py-4 px-8 rounded-lg inline-flex items-center transition-colors text-lg"
          >
            Get Started for Free
            <ArrowRightIcon className="w-5 h-5 ml-2" />
          </Link>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="flex items-center space-x-2 mb-4 md:mb-0">
              <div className="w-8 h-8 bg-gradient-to-r from-primary-500 to-accent-500 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-lg">A</span>
              </div>
              <span className="text-xl font-bold">Aether Automation</span>
            </div>
            <div className="flex space-x-6 text-gray-400">
              <a href="#" className="hover:text-white transition-colors">Privacy</a>
              <a href="#" className="hover:text-white transition-colors">Terms</a>
              <a href="#" className="hover:text-white transition-colors">Support</a>
              <a href="#" className="hover:text-white transition-colors">Docs</a>
            </div>
          </div>
          <div className="border-t border-gray-800 mt-8 pt-8 text-center text-gray-400">
            <p>&copy; 2024 Aether Automation. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default Homepage