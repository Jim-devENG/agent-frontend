'use client'

import { useEffect, useState } from 'react'
import { CheckCircle2, Circle, Lock, Loader2, Search, Eye, FileText, Send, RefreshCw, ArrowRight, AlertCircle, Users } from 'lucide-react'
import { 
  getSocialPipelineStatus,
  discoverSocialProfilesPipeline,
  reviewSocialProfiles,
  draftSocialProfiles,
  sendSocialProfiles,
  createSocialFollowupsPipeline,
  type SocialPipelineStatus
} from '@/lib/api'

interface StepCard {
  id: number
  name: string
  description: string
  icon: any
  status: 'pending' | 'active' | 'completed' | 'locked'
  count: number
  ctaText: string
  ctaAction: () => void
}

export default function SocialPipeline() {
  const [status, setStatus] = useState<SocialPipelineStatus | null>(null)
  const [loading, setLoading] = useState(true)
  const [discoveryLoading, setDiscoveryLoading] = useState(false)

  const loadStatus = async () => {
    try {
      const pipelineStatus = await getSocialPipelineStatus()
      setStatus(pipelineStatus)
    } catch (error) {
      console.error('Failed to load social pipeline status:', error)
      // Set default status on error
      setStatus({
        discovered: 0,
        reviewed: 0,
        qualified: 0,
        drafted: 0,
        sent: 0,
        followup_ready: 0,
        status: 'inactive'
      })
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    let abortController = new AbortController()
    let debounceTimeout: NodeJS.Timeout | null = null
    
    const loadStatusDebounced = () => {
      abortController.abort()
      abortController = new AbortController()
      
      if (debounceTimeout) {
        clearTimeout(debounceTimeout)
      }
      
      debounceTimeout = setTimeout(() => {
        loadStatus()
      }, 300)
    }
    
    // Initial load
    loadStatusDebounced()
    
    // Refresh every 10 seconds
    const interval = setInterval(() => {
      loadStatusDebounced()
    }, 10000)
    
    // Listen for manual refresh requests
    const handleRefresh = () => {
      loadStatusDebounced()
    }
    
    if (typeof window !== 'undefined') {
      window.addEventListener('refreshSocialPipelineStatus', handleRefresh)
    }
    
    return () => {
      abortController.abort()
      if (debounceTimeout) {
        clearTimeout(debounceTimeout)
      }
      clearInterval(interval)
      if (typeof window !== 'undefined') {
        window.removeEventListener('refreshSocialPipelineStatus', handleRefresh)
      }
    }
  }, [])

  const handleDiscover = async () => {
    // Discovery is handled in the discovery component
    // This is just a placeholder
  }

  const handleReview = async () => {
    // Review is handled in the profiles table
    // This is just a placeholder
  }

  const handleDraft = async () => {
    try {
      // Get qualified profiles - this would come from the profiles table
      // For now, this is a placeholder
      alert('Drafting is handled from the Profiles tab. Select qualified profiles and click "Draft".')
    } catch (err: any) {
      alert(err.message || 'Failed to create drafts')
    }
  }

  const handleSend = async () => {
    try {
      // Get drafted profiles - this would come from the profiles table
      // For now, this is a placeholder
      alert('Sending is handled from the Profiles tab. Select drafted profiles and click "Send".')
    } catch (err: any) {
      alert(err.message || 'Failed to send messages')
    }
  }

  const handleFollowup = async () => {
    try {
      // Get sent profiles - this would come from the profiles table
      // For now, this is a placeholder
      alert('Follow-ups are handled from the Profiles tab. Select sent profiles and click "Create Follow-up".')
    } catch (err: any) {
      alert(err.message || 'Failed to create follow-ups')
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <Loader2 className="w-6 h-6 animate-spin text-olive-600" />
      </div>
    )
  }

  if (!status || status.status === 'inactive') {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center space-x-2 text-amber-600 mb-2">
          <AlertCircle className="w-5 h-5" />
          <h3 className="font-semibold">Social Outreach Not Available</h3>
        </div>
        <p className="text-sm text-gray-600">
          {status?.reason || 'Social outreach feature is not initialized. Please run database migrations.'}
        </p>
      </div>
    )
  }

  const steps: StepCard[] = [
    {
      id: 1,
      name: 'Discovery',
      description: 'Discover social media profiles',
      icon: Search,
      status: 'active', // Always unlocked
      count: status.discovered,
      ctaText: 'Discover Profiles',
      ctaAction: handleDiscover
    },
    {
      id: 2,
      name: 'Profile Review',
      description: 'Review and qualify profiles',
      icon: Eye,
      status: status.discovered > 0 ? 'active' : 'locked',
      count: status.qualified,
      ctaText: 'Review Profiles',
      ctaAction: handleReview
    },
    {
      id: 3,
      name: 'Drafting',
      description: 'Create outreach messages',
      icon: FileText,
      status: status.qualified > 0 ? 'active' : 'locked',
      count: status.drafted,
      ctaText: 'Create Drafts',
      ctaAction: handleDraft
    },
    {
      id: 4,
      name: 'Sending',
      description: 'Send messages to profiles',
      icon: Send,
      status: status.drafted > 0 ? 'active' : 'locked',
      count: status.sent,
      ctaText: 'Send Messages',
      ctaAction: handleSend
    },
    {
      id: 5,
      name: 'Follow-ups',
      description: 'Create follow-up messages',
      icon: RefreshCw,
      status: status.sent > 0 ? 'active' : 'locked',
      count: status.followup_ready,
      ctaText: 'Create Follow-ups',
      ctaAction: handleFollowup
    }
  ]

  return (
    <div className="space-y-6">
      {/* Pipeline Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {steps.map((step, index) => {
          const Icon = step.icon
          const isLocked = step.status === 'locked'
          const isCompleted = step.count > 0 && step.status === 'active'
          const isActive = step.status === 'active' && !isCompleted

          return (
            <div
              key={step.id}
              className={`
                bg-white rounded-lg shadow-md p-4 border-2 transition-all duration-200
                ${isLocked ? 'border-gray-200 opacity-60' : 'border-olive-200 hover:border-olive-400 hover:shadow-lg'}
                ${isActive ? 'ring-2 ring-olive-300' : ''}
              `}
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center space-x-2">
                  {isLocked ? (
                    <Lock className="w-5 h-5 text-gray-400" />
                  ) : isCompleted ? (
                    <CheckCircle2 className="w-5 h-5 text-green-600" />
                  ) : (
                    <Icon className="w-5 h-5 text-olive-600" />
                  )}
                  <h3 className="font-semibold text-sm text-gray-900">{step.name}</h3>
                </div>
                {isLocked && (
                  <Circle className="w-4 h-4 text-gray-400" />
                )}
              </div>

              <p className="text-xs text-gray-600 mb-3">{step.description}</p>

              <div className="flex items-center justify-between mb-3">
                <span className="text-2xl font-bold text-olive-600">{step.count}</span>
                {isActive && (
                  <span className="text-xs text-olive-600 font-medium">Active</span>
                )}
              </div>

              <button
                onClick={step.ctaAction}
                disabled={isLocked}
                className={`
                  w-full py-2 px-3 rounded-lg text-xs font-medium transition-all duration-200
                  ${isLocked
                    ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                    : 'bg-olive-600 text-white hover:bg-olive-700 hover:shadow-md'
                  }
                `}
              >
                {step.ctaText}
              </button>
            </div>
          )
        })}
      </div>

      {/* Summary Stats */}
      <div className="bg-white rounded-lg shadow p-4">
        <h3 className="font-semibold text-sm text-gray-900 mb-3">Pipeline Summary</h3>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-olive-600">{status.discovered}</div>
            <div className="text-xs text-gray-600">Discovered</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-olive-600">{status.qualified}</div>
            <div className="text-xs text-gray-600">Qualified</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-olive-600">{status.drafted}</div>
            <div className="text-xs text-gray-600">Drafted</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-olive-600">{status.sent}</div>
            <div className="text-xs text-gray-600">Sent</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-olive-600">{status.followup_ready}</div>
            <div className="text-xs text-gray-600">Follow-up Ready</div>
          </div>
        </div>
      </div>
    </div>
  )
}

