import React, { useState, useRef, useEffect } from 'react'
import { apiMethods } from '../utils/api'
import { 
  SparklesIcon,
  ChatBubbleLeftIcon,
  XMarkIcon,
  PaperAirplaneIcon,
  LightBulbIcon,
  CommandLineIcon,
  CogIcon,
  DocumentTextIcon
} from '@heroicons/react/24/outline'
import LoadingSpinner from './LoadingSpinner'
import toast from 'react-hot-toast'

const EnhancedAIAssistant = ({ isOpen, onClose, onWorkflowGenerated, sessionId }) => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'assistant',
      content: "👋 Hi! I'm your AI assistant. I can help you:",
      suggestions: [
        "Create workflows from descriptions",
        "Suggest optimizations for existing workflows", 
        "Explain automation concepts",
        "Help with integration setup"
      ]
    }
  ])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [mode, setMode] = useState('chat') // 'chat' or 'workflow-gen'
  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus()
    }
  }, [isOpen])

  const handleSend = async () => {
    if (!input.trim() || isLoading) return

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: input.trim()
    }

    setMessages(prev => [...prev, userMessage])
    setInput('')
    setIsLoading(true)

    try {
      if (mode === 'workflow-gen') {
        // Workflow generation mode
        const response = await apiMethods.generateWorkflow(userMessage.content, true, sessionId)
        
        if (response.type === 'workflow' && response.data) {
          const assistantMessage = {
            id: Date.now() + 1,
            type: 'assistant',
            content: `✨ I've generated a workflow for you! It includes ${response.data.nodes?.length || 0} nodes and covers: ${response.data.description}`,
            workflow: response.data
          }
          setMessages(prev => [...prev, assistantMessage])
          
          if (onWorkflowGenerated) {
            onWorkflowGenerated(response.data)
          }
          toast.success('Workflow generated successfully!')
        } else {
          const assistantMessage = {
            id: Date.now() + 1,
            type: 'assistant',
            content: response.data?.suggestion || "I couldn't generate a structured workflow, but here are some suggestions for your automation."
          }
          setMessages(prev => [...prev, assistantMessage])
        }
      } else {
        // Chat mode
        const response = await apiMethods.chatWithAI(userMessage.content, sessionId)
        const assistantMessage = {
          id: Date.now() + 1,
          type: 'assistant',
          content: response.response
        }
        setMessages(prev => [...prev, assistantMessage])
      }
    } catch (error) {
      console.error('AI request failed:', error)
      const errorMessage = {
        id: Date.now() + 1,
        type: 'assistant',
        content: "I'm sorry, I'm having trouble processing your request right now. Please try again later."
      }
      setMessages(prev => [...prev, errorMessage])
      toast.error('AI request failed')
    } finally {
      setIsLoading(false)
    }
  }

  const handleSuggestionClick = (suggestion) => {
    setInput(suggestion)
    inputRef.current?.focus()
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-2xl mx-4 h-[600px] flex flex-col">
        {/* Header */}
        <div className="p-4 border-b border-gray-200 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-gradient-to-r from-purple-500 to-pink-500 rounded-lg flex items-center justify-center">
              <SparklesIcon className="w-5 h-5 text-white" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900">AI Assistant</h3>
              <p className="text-sm text-gray-600">Powered by advanced AI</p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <div className="flex bg-gray-100 rounded-lg p-1">
              <button
                onClick={() => setMode('chat')}
                className={`px-3 py-1 rounded-md text-sm font-medium transition-colors ${
                  mode === 'chat' 
                    ? 'bg-white text-primary-600 shadow-sm' 
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                <ChatBubbleLeftIcon className="w-4 h-4 inline mr-1" />
                Chat
              </button>
              <button
                onClick={() => setMode('workflow-gen')}
                className={`px-3 py-1 rounded-md text-sm font-medium transition-colors ${
                  mode === 'workflow-gen' 
                    ? 'bg-white text-primary-600 shadow-sm' 
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                <CogIcon className="w-4 h-4 inline mr-1" />
                Generate
              </button>
            </div>
            <button
              onClick={onClose}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <XMarkIcon className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[80%] rounded-lg p-3 ${
                  message.type === 'user'
                    ? 'bg-primary-600 text-white'
                    : 'bg-gray-100 text-gray-900'
                }`}
              >
                <p className="whitespace-pre-wrap">{message.content}</p>
                
                {/* Suggestions */}
                {message.suggestions && (
                  <div className="mt-3 space-y-2">
                    {message.suggestions.map((suggestion, index) => (
                      <button
                        key={index}
                        onClick={() => handleSuggestionClick(suggestion)}
                        className="block w-full text-left text-sm bg-white bg-opacity-20 hover:bg-opacity-30 rounded-md p-2 transition-colors"
                      >
                        <LightBulbIcon className="w-4 h-4 inline mr-2" />
                        {suggestion}
                      </button>
                    ))}
                  </div>
                )}

                {/* Workflow preview */}
                {message.workflow && (
                  <div className="mt-3 p-3 bg-white bg-opacity-10 rounded-md">
                    <div className="flex items-center mb-2">
                      <DocumentTextIcon className="w-4 h-4 mr-2" />
                      <span className="font-medium">Generated Workflow</span>
                    </div>
                    <p className="text-sm opacity-90">
                      Name: {message.workflow.name}
                    </p>
                    <p className="text-sm opacity-90">
                      Nodes: {message.workflow.nodes?.length || 0}
                    </p>
                    <p className="text-sm opacity-90">
                      Connections: {message.workflow.connections?.length || 0}
                    </p>
                  </div>
                )}
              </div>
            </div>
          ))}
          
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-gray-100 rounded-lg p-3">
                <LoadingSpinner size="small" />
                <span className="ml-2 text-gray-600">AI is thinking...</span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="p-4 border-t border-gray-200">
          <div className="flex space-x-2">
            <div className="flex-1 relative">
              <textarea
                ref={inputRef}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyPress}
                placeholder={
                  mode === 'chat' 
                    ? "Ask me anything about automation..." 
                    : "Describe the workflow you want to create..."
                }
                className="w-full px-4 py-3 border border-gray-300 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                rows="2"
                disabled={isLoading}
              />
              <div className="absolute right-2 bottom-2">
                <button
                  onClick={handleSend}
                  disabled={!input.trim() || isLoading}
                  className="p-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  <PaperAirplaneIcon className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
          <p className="text-xs text-gray-500 mt-2">
            {mode === 'chat' ? 'Chat mode - Ask questions and get help' : 'Generation mode - Create workflows from descriptions'}
          </p>
        </div>
      </div>
    </div>
  )
}

export default EnhancedAIAssistant