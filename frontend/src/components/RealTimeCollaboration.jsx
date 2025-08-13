import React, { useState, useEffect, useCallback, useRef } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { 
  UserIcon,
  EyeIcon,
  PencilIcon,
  ChatBubbleLeftIcon,
  BellIcon,
  ClockIcon
} from '@heroicons/react/24/outline'
import toast from 'react-hot-toast'

// Real-time collaboration hook
export const useRealTimeCollaboration = (workflowId) => {
  const { user } = useAuth()
  const [collaborators, setCollaborators] = useState([])
  const [isConnected, setIsConnected] = useState(false)
  const [activityFeed, setActivityFeed] = useState([])
  const wsRef = useRef(null)

  // Mock WebSocket connection for demo
  const connectToWorkflow = useCallback(() => {
    if (!workflowId || !user) return

    // Simulate WebSocket connection
    setIsConnected(true)
    
    // Mock initial collaborators
    const mockCollaborators = [
      {
        id: user.id,
        name: user.name,
        email: user.email,
        role: 'owner',
        status: 'active',
        cursor: null,
        lastSeen: new Date()
      }
    ]
    
    setCollaborators(mockCollaborators)

    // Mock activity feed
    const mockActivities = [
      {
        id: 1,
        type: 'join',
        user: user.name,
        message: 'joined the workflow',
        timestamp: new Date()
      }
    ]
    
    setActivityFeed(mockActivities)

    return () => {
      setIsConnected(false)
      setCollaborators([])
    }
  }, [workflowId, user])

  useEffect(() => {
    const cleanup = connectToWorkflow()
    return cleanup
  }, [connectToWorkflow])

  const sendCursorPosition = useCallback((x, y) => {
    if (!isConnected) return
    
    // Mock cursor position broadcast
    setCollaborators(prev => 
      prev.map(collaborator => 
        collaborator.id === user.id 
          ? { ...collaborator, cursor: { x, y } }
          : collaborator
      )
    )
  }, [isConnected, user])

  const sendNodeUpdate = useCallback((nodeId, changes) => {
    if (!isConnected) return

    // Mock node update broadcast
    const activity = {
      id: Date.now(),
      type: 'node_update',
      user: user.name,
      message: `updated node ${nodeId}`,
      timestamp: new Date(),
      details: changes
    }

    setActivityFeed(prev => [activity, ...prev.slice(0, 49)]) // Keep last 50 activities
    toast.success('Changes synced with collaborators')
  }, [isConnected, user])

  const addComment = useCallback((nodeId, comment) => {
    if (!isConnected) return

    const activity = {
      id: Date.now(),
      type: 'comment',
      user: user.name,
      message: `commented on node ${nodeId}`,
      timestamp: new Date(),
      details: { comment }
    }

    setActivityFeed(prev => [activity, ...prev.slice(0, 49)])
    toast.success('Comment added')
  }, [isConnected, user])

  return {
    collaborators,
    isConnected,
    activityFeed,
    sendCursorPosition,
    sendNodeUpdate,
    addComment
  }
}

// Collaborator avatars component
export const CollaboratorAvatars = ({ collaborators, maxVisible = 3 }) => {
  const visibleCollaborators = collaborators.slice(0, maxVisible)
  const hiddenCount = Math.max(0, collaborators.length - maxVisible)

  return (
    <div className="flex items-center space-x-2">
      <div className="flex -space-x-2">
        {visibleCollaborators.map((collaborator) => (
          <div
            key={collaborator.id}
            className={`
              relative w-8 h-8 rounded-full border-2 border-white dark:border-gray-800 flex items-center justify-center text-xs font-medium
              ${collaborator.status === 'active' 
                ? 'bg-gradient-to-r from-green-400 to-blue-500' 
                : 'bg-gray-400'
              }
            `}
            title={`${collaborator.name} (${collaborator.role})`}
          >
            <span className="text-white">
              {collaborator.name.charAt(0).toUpperCase()}
            </span>
            {collaborator.status === 'active' && (
              <div className="absolute -bottom-1 -right-1 w-3 h-3 bg-green-500 rounded-full border-2 border-white dark:border-gray-800"></div>
            )}
          </div>
        ))}
        
        {hiddenCount > 0 && (
          <div className="w-8 h-8 bg-gray-100 dark:bg-gray-700 rounded-full border-2 border-white dark:border-gray-800 flex items-center justify-center">
            <span className="text-xs font-medium text-gray-600 dark:text-gray-300">
              +{hiddenCount}
            </span>
          </div>
        )}
      </div>
      
      <div className="text-sm text-gray-500 dark:text-gray-400">
        {collaborators.length === 1 ? 'Just you' : `${collaborators.length} collaborators`}
      </div>
    </div>
  )
}

// Activity feed component
export const ActivityFeed = ({ activities, className = '' }) => {
  const getActivityIcon = (type) => {
    switch (type) {
      case 'join':
        return <UserIcon className="w-4 h-4 text-green-500" />
      case 'leave':
        return <UserIcon className="w-4 h-4 text-red-500" />
      case 'node_update':
        return <PencilIcon className="w-4 h-4 text-blue-500" />
      case 'comment':
        return <ChatBubbleLeftIcon className="w-4 h-4 text-purple-500" />
      case 'view':
        return <EyeIcon className="w-4 h-4 text-gray-500" />
      default:
        return <ClockIcon className="w-4 h-4 text-gray-400" />
    }
  }

  const formatTimeAgo = (timestamp) => {
    const now = new Date()
    const diff = now - timestamp
    const minutes = Math.floor(diff / (1000 * 60))
    const hours = Math.floor(minutes / 60)

    if (hours > 0) return `${hours}h ago`
    if (minutes > 0) return `${minutes}m ago`
    return 'Just now'
  }

  return (
    <div className={`bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 ${className}`}>
      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center">
          <ClockIcon className="w-5 h-5 mr-2" />
          Recent Activity
        </h3>
      </div>
      
      <div className="max-h-64 overflow-y-auto">
        {activities.length === 0 ? (
          <div className="p-4 text-center text-gray-500 dark:text-gray-400">
            No recent activity
          </div>
        ) : (
          <div className="divide-y divide-gray-100 dark:divide-gray-700">
            {activities.map((activity) => (
              <div key={activity.id} className="p-4 hover:bg-gray-50 dark:hover:bg-gray-700">
                <div className="flex items-start space-x-3">
                  {getActivityIcon(activity.type)}
                  <div className="flex-1 min-w-0">
                    <p className="text-sm text-gray-900 dark:text-white">
                      <span className="font-medium">{activity.user}</span> {activity.message}
                    </p>
                    {activity.details && activity.type === 'comment' && (
                      <div className="mt-1 p-2 bg-gray-50 dark:bg-gray-600 rounded text-sm text-gray-700 dark:text-gray-300">
                        "{activity.details.comment}"
                      </div>
                    )}
                    <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                      {formatTimeAgo(activity.timestamp)}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

// Collaboration toolbar component
export const CollaborationToolbar = ({ 
  workflowId, 
  collaborators, 
  activities, 
  onInviteCollaborator,
  onToggleComments,
  showComments,
  className = '' 
}) => {
  const [showInviteModal, setShowInviteModal] = useState(false)
  const [inviteEmail, setInviteEmail] = useState('')
  const [inviteRole, setInviteRole] = useState('viewer')

  const handleInvite = (e) => {
    e.preventDefault()
    if (inviteEmail.trim()) {
      onInviteCollaborator(inviteEmail, inviteRole)
      setInviteEmail('')
      setShowInviteModal(false)
      toast.success(`Invitation sent to ${inviteEmail}`)
    }
  }

  return (
    <div className={`flex items-center justify-between p-4 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 ${className}`}>
      <div className="flex items-center space-x-4">
        <CollaboratorAvatars collaborators={collaborators} />
        
        <div className="h-4 w-px bg-gray-300 dark:bg-gray-600"></div>
        
        <div className="flex items-center space-x-2">
          <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
          <span className="text-sm text-gray-600 dark:text-gray-400">Live</span>
        </div>
      </div>

      <div className="flex items-center space-x-2">
        <button
          onClick={onToggleComments}
          className={`
            flex items-center space-x-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors
            ${showComments 
              ? 'bg-purple-100 dark:bg-purple-900/20 text-purple-700 dark:text-purple-300' 
              : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700'
            }
          `}
        >
          <ChatBubbleLeftIcon className="w-4 h-4" />
          <span>Comments</span>
        </button>

        <button
          onClick={() => setShowInviteModal(true)}
          className="flex items-center space-x-2 px-3 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors text-sm font-medium"
        >
          <UserIcon className="w-4 h-4" />
          <span>Invite</span>
        </button>
      </div>

      {/* Invite Modal */}
      {showInviteModal && (
        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div className="flex min-h-screen items-center justify-center px-4">
            <div className="fixed inset-0 bg-black bg-opacity-25" onClick={() => setShowInviteModal(false)} />
            
            <div className="relative bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-md w-full p-6">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                Invite Collaborator
              </h3>
              
              <form onSubmit={handleInvite} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Email Address
                  </label>
                  <input
                    type="email"
                    value={inviteEmail}
                    onChange={(e) => setInviteEmail(e.target.value)}
                    placeholder="colleague@company.com"
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:text-white"
                    required
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Role
                  </label>
                  <select
                    value={inviteRole}
                    onChange={(e) => setInviteRole(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:text-white"
                  >
                    <option value="viewer">Viewer - Can view workflow</option>
                    <option value="editor">Editor - Can edit workflow</option>
                    <option value="admin">Admin - Full access</option>
                  </select>
                </div>
                
                <div className="flex items-center justify-end space-x-3 pt-4">
                  <button
                    type="button"
                    onClick={() => setShowInviteModal(false)}
                    className="px-4 py-2 text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors"
                  >
                    Send Invite
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

// Main collaboration provider component
const RealTimeCollaboration = ({ workflowId, children }) => {
  const collaboration = useRealTimeCollaboration(workflowId)
  const [showComments, setShowComments] = useState(false)

  const handleInviteCollaborator = async (email, role) => {
    // Mock invite functionality
    console.log(`Inviting ${email} as ${role}`)
  }

  return (
    <div className="relative">
      <CollaborationToolbar
        workflowId={workflowId}
        collaborators={collaboration.collaborators}
        activities={collaboration.activityFeed}
        onInviteCollaborator={handleInviteCollaborator}
        onToggleComments={() => setShowComments(!showComments)}
        showComments={showComments}
      />
      
      <div className="flex">
        <div className="flex-1">
          {children}
        </div>
        
        {showComments && (
          <div className="w-80 border-l border-gray-200 dark:border-gray-700">
            <ActivityFeed activities={collaboration.activityFeed} className="h-full border-none rounded-none" />
          </div>
        )}
      </div>
    </div>
  )
}

export default RealTimeCollaboration