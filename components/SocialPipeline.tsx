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
      <div className="glass rounded-xl shadow-lg p-6 border border-olive-200">
        <div className="flex items-center space-x-2 text-amber-600 mb-2">
          <AlertCircle className="w-5 h-5" />
          <h3 className="font-semibold text-sm">Social Outreach Not Available</h3>
        </div>
        <p className="text-xs text-gray-600">
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
    <div className="space-y-4 animate-fade-in">
      {/* Header */}
      <div className="glass rounded-xl shadow-lg p-3 border border-olive-200">
        <div className="flex items-center justify-between mb-2">
          <div>
            <h2 className="text-sm font-bold text-olive-700 mb-1">Social Outreach Pipeline</h2>
            <p className="text-gray-600 text-xs">
              Connect with social media profiles through creative outreach
            </p>
          </div>
          <button
            onClick={loadStatus}
            className="flex items-center space-x-1 px-2 py-1 bg-olive-600 text-white rounded-lg transition-all duration-200 text-xs font-medium hover:bg-olive-700 hover:shadow-md"
          >
            <RefreshCw className="w-3 h-3" />
            <span>Refresh</span>
          </button>
        </div>
        <div className="mt-2 p-2 bg-gradient-to-r from-olive-50 to-olive-50 rounded-lg border border-olive-200">
          <p className="text-xs text-gray-700">
            <span className="font-semibold">Orchestrate your social outreach</span> — Each stage builds on the previous, creating meaningful connections through art and creativity.
          </p>
        </div>
      </div>

      {/* Step Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {steps.map((step, index) => {
          const Icon = step.icon
          const isCompleted = step.status === 'completed' || (step.count > 0 && step.status === 'active')
          const isLocked = step.status === 'locked'
          const isActive = step.status === 'active' && !isLocked
          
          return (
            <div
              key={step.id}
              className={`glass rounded-xl shadow-lg p-3 border transition-all duration-300 hover:shadow-xl hover:scale-102 animate-slide-up ${
                isCompleted
                  ? 'border-olive-300 bg-gradient-to-br from-olive-50/80 to-olive-50/50'
                  : isLocked
                  ? 'border-gray-200 opacity-60'
                  : 'border-olive-300 bg-gradient-to-br from-olive-50/80 to-olive-50/50'
              }`}
              style={{ animationDelay: `${index * 100}ms` }}
            >
              <div className="flex items-start justify-between mb-2">
                <div className={`p-2 rounded-lg shadow-md transition-all duration-300 ${
                  isCompleted
                    ? 'bg-olive-600 text-white'
                    : isLocked
                    ? 'bg-gray-300 text-gray-500'
                    : 'bg-olive-600 text-white hover-glow'
                }`}>
                  <Icon className="w-4 h-4" />
                </div>
                {isCompleted && (
                  <CheckCircle2 className="w-4 h-4 text-olive-600 animate-scale-in" />
                )}
                {isLocked && (
                  <Lock className="w-4 h-4 text-gray-400" />
                )}
              </div>

              <h3 className="text-sm font-bold text-gray-900 mb-1">{step.name}</h3>
              <p className="text-xs text-gray-600 mb-2">{step.description}</p>

              <div className="flex items-center justify-between mb-2">
                <div>
                  <p className="text-lg font-bold text-olive-700">{step.count}</p>
                  <p className="text-xs text-gray-500">
                    {step.id === 1 && `${status.discovered} discovered`}
                    {step.id === 2 && `${status.qualified} qualified`}
                    {step.id === 3 && `${status.drafted} drafted`}
                    {step.id === 4 && `${status.sent} sent`}
                    {step.id === 5 && `${status.followup_ready} ready for follow-up`}
                  </p>
                </div>
              </div>

              <button
                onClick={step.ctaAction}
                disabled={isLocked}
                className={`w-full px-2 py-1.5 rounded-lg text-xs font-semibold flex items-center justify-center space-x-1 transition-all duration-200 ${
                  isLocked
                    ? 'bg-gray-200 text-gray-500 cursor-not-allowed'
                    : isCompleted
                    ? 'bg-olive-600 text-white hover:bg-olive-700 hover:shadow-md hover:scale-102'
                    : 'bg-olive-600 text-white hover:bg-olive-700 hover:shadow-md hover:scale-102'
                }`}
              >
                <span>{step.ctaText}</span>
                {!isLocked && <ArrowRight className="w-3 h-3" />}
              </button>
            </div>
          )
        })}
      </div>
    </div>
  )
}

