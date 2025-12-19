/**
 * PIPELINE COMPONENT - BACKEND AUTHORITY DISCIPLINE
 * 
 * CRITICAL PRINCIPLE: The backend is the SINGLE SOURCE OF TRUTH for pipeline state.
 * 
 * Why pipeline status is authoritative:
 * - Backend `/api/pipeline/status` computes counts directly from database state
 * - Frontend cannot know database state without querying backend
 * - Any frontend assumption about state can be wrong (race conditions, stale data)
 * 
 * Why frontend must not guess:
 * - Backend endpoints enforce strict validation rules
 * - Calling endpoints optimistically causes 400/422 errors
 * - User experience degrades when buttons are enabled but backend rejects
 * - Frontend guessing creates inconsistencies between UI and actual state
 * 
 * Why errors were happening before:
 * - Verify button checked `leads === 0` instead of calculating verify-ready count
 * - Draft button didn't strictly check `drafting_ready_count === 0`
 * - Endpoints were called optimistically without checking backend state
 * - Generic error messages hid backend's specific validation failures
 * 
 * DISCIPLINE ENFORCED:
 * 1. All button enable/disable logic derives from `/api/pipeline/status` response
 * 2. Never call pipeline endpoints unless backend confirms readiness
 * 3. Show backend's exact error messages (not generic alerts)
 * 4. Calculate verify-ready count from backend fields (emails_found - emails_verified)
 * 5. Use backend's explicit counts (drafting_ready_count, send_ready_count) for gating
 */

'use client'

import { useEffect, useState, useRef } from 'react'
import { CheckCircle2, Circle, Lock, Loader2, Search, Scissors, Shield, Eye, FileText, Send, RefreshCw, ArrowRight } from 'lucide-react'
import { 
  pipelineDiscover, 
  pipelineApprove, 
  pipelineApproveAll,
  pipelineScrape, 
  pipelineVerify, 
  pipelineDraft, 
  pipelineSend,
  pipelineStatus,
  listJobs,
  normalizePipelineStatus,
  type Job,
  type NormalizedPipelineStatus
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
  jobStatus?: string
}

export default function Pipeline() {
  const [status, setStatus] = useState<NormalizedPipelineStatus | null>(null)
  const [loading, setLoading] = useState(true)
  const [discoveryJobs, setDiscoveryJobs] = useState<Job[]>([])
  const [verificationJobs, setVerificationJobs] = useState<Job[]>([])

  const loadStatus = async () => {
    try {
      const rawStatus = await pipelineStatus()
      const normalizedStatus = normalizePipelineStatus(rawStatus)
      setStatus(normalizedStatus)
    } catch (error) {
      console.error('Failed to load pipeline status:', error)
      // Set default normalized status on error
      setStatus(normalizePipelineStatus(null))
    } finally {
      setLoading(false)
    }
  }

  const loadDiscoveryJobs = async () => {
    try {
      const jobs = await listJobs(0, 50)
      const discoveryJobsList = jobs.filter((j: Job) => j.job_type === 'discover')
      setDiscoveryJobs(discoveryJobsList)
    } catch (err) {
      console.error('Failed to load discovery jobs:', err)
    }
  }

  // Track if we've already triggered refresh for completed verification jobs
  const hasTriggeredVerificationRefresh = useRef(false)

  const loadVerificationJobs = async () => {
    try {
      const jobs = await listJobs(0, 50)
      const verificationJobsList = jobs.filter((j: Job) => j.job_type === 'verify')
      setVerificationJobs(verificationJobsList)
      
      // Check for completed verification jobs and trigger refresh
      const completedJobs = verificationJobsList.filter((j: Job) => j.status === 'completed')
      if (completedJobs.length > 0 && !hasTriggeredVerificationRefresh.current) {
        hasTriggeredVerificationRefresh.current = true
        console.log('🔄 Found completed verification job, triggering refresh...', completedJobs[0].id)
        setTimeout(() => {
          loadStatus()
          hasTriggeredVerificationRefresh.current = false
        }, 2000)
      }
    } catch (err) {
      console.error('Failed to load verification jobs:', err)
    }
  }

  useEffect(() => {
    let abortController = new AbortController()
    let debounceTimeout: NodeJS.Timeout | null = null
    
    const loadStatusDebounced = () => {
      // Cancel previous request if still in flight
      abortController.abort()
      abortController = new AbortController()
      
      // Clear existing debounce timeout
      if (debounceTimeout) {
        clearTimeout(debounceTimeout)
      }
      
      // Debounce: wait 300ms before making request
      debounceTimeout = setTimeout(() => {
        loadStatus()
        loadDiscoveryJobs()
        loadVerificationJobs()
      }, 300)
    }
    
    // Initial load
    loadStatusDebounced()
    
    // Debounced refresh every 10 seconds
    const interval = setInterval(() => {
      loadStatusDebounced()
    }, 10000)
    
    // Listen for manual refresh requests (e.g., after composing email from Leads page)
    const handleRefreshPipelineStatus = () => {
      console.log('🔄 Pipeline status refresh requested...')
      loadStatusDebounced()
    }
    
    if (typeof window !== 'undefined') {
      window.addEventListener('refreshPipelineStatus', handleRefreshPipelineStatus)
    }
    
    return () => {
      abortController.abort()
      if (debounceTimeout) {
        clearTimeout(debounceTimeout)
      }
      clearInterval(interval)
      if (typeof window !== 'undefined') {
        window.removeEventListener('refreshPipelineStatus', handleRefreshPipelineStatus)
      }
    }
  }, [])

  const handleDiscover = async () => {
    // Discovery form is handled in Step1Discovery component
    // This is just a placeholder - actual discovery happens in the step card
  }

  const handleScrape = async () => {
    try {
      await pipelineScrape()
      await loadStatus()
    } catch (err: any) {
      alert(err.message || 'Failed to start scraping')
    }
  }

  const handleApproveAll = async () => {
    try {
      const res = await pipelineApproveAll()
      alert(res.message || `Approved ${res.approved_count} websites`)
      await loadStatus()
      // Optionally, navigate user to Websites tab to review approved websites
      const event = new CustomEvent('change-tab', { detail: 'websites' })
      window.dispatchEvent(event)
    } catch (err: any) {
      alert(err.message || 'Failed to approve all websites')
    }
  }

  /**
   * BACKEND AUTHORITY: /api/pipeline/verify
   * 
   * Backend allows verify ONLY when prospects satisfy:
   * - scrape_status IN ('SCRAPED','ENRICHED')
   * - contact_email IS NOT NULL
   * - verification_status != 'verified'
   * 
   * Frontend MUST:
   * - Calculate verify-ready count from backend status (emails_found - emails_verified)
   * - Disable button when count is 0 (backend will reject with 400)
   * - Show backend error message (not generic alert)
   * - NEVER call endpoint optimistically
   * - Show job status so user knows verification is running
   * 
   * VERIFICATION FLOW:
   * - Verifies scraped emails using Snov.io API
   * - Updates verification_status to 'verified' or 'unverified'
   * - Verified prospects become ready for drafting (drafting_ready_count increases)
   * - Note: Verification doesn't automatically promote to "leads" - that's a separate stage
   */
  const handleVerify = async () => {
    // Calculate verify-ready count from backend truth
    // Verify-ready = prospects with emails that are NOT verified
    // Must also be scraped (scraped > 0 ensures scraping has occurred)
    const verifyReadyCount = normalizedStatus.scraped > 0 
      ? Math.max(0, normalizedStatus.emails_found - normalizedStatus.emails_verified)
      : 0
    
    // CRITICAL: Never call backend if we know it will reject
    if (verifyReadyCount === 0) {
      alert('No prospects ready for verification. Ensure prospects are scraped and have emails.')
      return
    }
    
    try {
      const response = await pipelineVerify()
      // Show success message with job info
      alert(`✅ Verification job started!\n\nVerifying ${response.prospects_count} scraped emails using Snov.io.\nJob ID: ${response.job_id}\n\nWhat happens:\n• Emails are verified via Snov.io API\n• Verified emails become ready for drafting\n• Check the Jobs tab or refresh to see progress\n• Verified count will update when complete`)
      // Refresh status and jobs to show running job
      await Promise.all([loadStatus(), loadVerificationJobs()])
      // Set flag to prevent duplicate refresh
      hasTriggeredVerificationRefresh.current = false
    } catch (err: any) {
      // Backend returns 400 with specific message when no eligible prospects
      // Show backend's exact error message (not generic)
      const errorMessage = err.message || 'Failed to start verification'
      alert(errorMessage)
    }
  }

  /**
   * BACKEND AUTHORITY: /api/pipeline/draft
   * 
   * Backend allows draft ONLY when prospects satisfy:
   * - verification_status = 'verified'
   * - contact_email IS NOT NULL
   * - draft_status = 'pending' (not already drafted)
   * 
   * Frontend MUST:
   * - Use backend's drafting_ready_count (verified + email)
   * - Note: Backend also requires draft_status = 'pending', which we can't check
   * - Disable button when drafting_ready_count is 0
   * - Send valid payload matching backend schema exactly
   * - Show backend error message (not generic alert)
   */
  const handleDraft = async () => {
    // CRITICAL: Never call backend if backend says no draft-ready prospects
    // Backend will reject with 422 if requirements not met
    if (normalizedStatus.drafting_ready_count === 0) {
      alert('No prospects ready for drafting. Ensure prospects are verified and have emails.')
      return
    }
    
    try {
      // Backend schema: DraftRequest { prospect_ids?: List[UUID] }
      // Send empty object to trigger automatic selection of all draft-ready prospects
      await pipelineDraft({})
      await loadStatus()
    } catch (err: any) {
      // Backend returns 422 with specific message when requirements not met
      // Show backend's exact error message
      const errorMessage = err.message || 'Failed to start drafting'
      alert(errorMessage)
    }
  }

  /**
   * BACKEND AUTHORITY: /api/pipeline/send
   * 
   * Backend allows send ONLY when prospects satisfy:
   * - verification_status = 'verified'
   * - draft_status = 'drafted'
   * - send_status != 'sent'
   * 
   * Frontend MUST:
   * - Use backend's send_ready_count (verified + drafted + not sent)
   * - Disable button when send_ready_count is 0
   * - Show backend error message (not generic alert)
   */
  const handleSend = async () => {
    // CRITICAL: Never call backend if backend says no send-ready prospects
    if (normalizedStatus.send_ready_count === 0) {
      alert('No emails ready for sending. Ensure prospects have verified email, draft subject, and draft body.')
      return
    }
    
    try {
      // Backend schema: SendRequest { prospect_ids?: List[UUID] }
      // Send empty object to trigger automatic selection of all send-ready prospects
      await pipelineSend({})
      await loadStatus()
    } catch (err: any) {
      // Backend returns 422 with specific message when requirements not met
      // Show backend's exact error message
      const errorMessage = err.message || 'Failed to start sending'
      alert(errorMessage)
    }
  }

  if (loading) {
    return (
      <div className="bg-white/90 backdrop-blur-sm rounded-2xl shadow-lg border-2 border-gray-200/60 p-6">
        <div className="text-center py-8">
          <Loader2 className="w-8 h-8 animate-spin mx-auto text-olive-600" />
          <p className="text-gray-500 mt-2">Loading pipeline status...</p>
        </div>
      </div>
    )
  }

  // Normalized status is guaranteed to have all fields as numbers
  // If status is null, use normalized empty status
  const normalizedStatus: NormalizedPipelineStatus = status || normalizePipelineStatus(null)

  const latestDiscoveryJob = discoveryJobs.length > 0
    ? discoveryJobs.sort((a: Job, b: Job) => {
        const dateA = new Date(a.created_at || 0).getTime()
        const dateB = new Date(b.created_at || 0).getTime()
        return dateB - dateA
      })[0]
    : null

  const latestVerificationJob = verificationJobs.length > 0
    ? verificationJobs.sort((a: Job, b: Job) => {
        const dateA = new Date(a.created_at || 0).getTime()
        const dateB = new Date(b.created_at || 0).getTime()
        return dateB - dateA
      })[0]
    : null

  const steps: StepCard[] = [
    {
      id: 1,
      name: 'Website Discovery',
      description: 'Find websites using DataForSEO',
      icon: Search,
      status: normalizedStatus.discovered > 0 ? 'completed' : 'active',
      count: normalizedStatus.discovered,
      ctaText: normalizedStatus.discovered > 0 ? 'View Websites' : 'Start Discovery',
      ctaAction: () => {
        // Navigate to Websites tab or show discovery form
        if (normalizedStatus.discovered > 0) {
          // Trigger tab change via custom event
          const event = new CustomEvent('change-tab', { detail: 'websites' })
          window.dispatchEvent(event)
        } else {
          // Show discovery form modal
          const event = new CustomEvent('show-discovery-form')
          window.dispatchEvent(event)
        }
      },
      jobStatus: latestDiscoveryJob?.status
    },
    {
      id: 2,
      name: 'Scraping',
      description: 'Extract emails from approved websites',
      icon: Scissors,
      // UNLOCK as soon as we have at least one scrape-ready website from the backend
      status: normalizedStatus.scrape_ready_count === 0 ? 'locked' :
              normalizedStatus.scraped > 0 ? 'completed' : 'active',
      count: normalizedStatus.scraped,
      ctaText: normalizedStatus.scrape_ready_count === 0
        ? 'Discover Websites First'
        : normalizedStatus.scraped > 0
        ? 'View Prospects'
        : 'Start Scraping',
      ctaAction: () => {
        // If nothing is scrape-ready yet, guide user back to discovery
        if (normalizedStatus.scrape_ready_count === 0) {
          const event = new CustomEvent('show-discovery-form')
          window.dispatchEvent(event)
          return
        }

        // If scraping already ran, take user to leads
        if (normalizedStatus.scraped > 0) {
          const event = new CustomEvent('change-tab', { detail: 'leads' })
          window.dispatchEvent(event)
          return
        }

        // Otherwise start scraping approved websites
        handleScrape()
      }
    },
    {
      id: 3,
      name: 'Verification',
      description: 'Verify scraped emails with Snov.io API',
      icon: Shield,
      // BACKEND AUTHORITY: Verify-ready = scraped + email + not verified
      // Calculate from backend status: emails_found - emails_verified (only if scraped > 0)
      // Lock if no verify-ready prospects exist (backend will reject with 400)
      status: (() => {
        // Calculate verify-ready count from backend truth
        const verifyReady = normalizedStatus.scraped > 0 
          ? Math.max(0, normalizedStatus.emails_found - normalizedStatus.emails_verified)
          : 0
        // Show 'active' if job is running
        if (latestVerificationJob?.status === 'running' || latestVerificationJob?.status === 'pending') {
          return 'active'
        }
        if (verifyReady === 0) return 'locked'
        if (normalizedStatus.emails_verified > 0) return 'completed'
        return 'active'
      })(),
      count: normalizedStatus.emails_verified,
      ctaText: (() => {
        // Calculate verify-ready count from backend truth
        const verifyReady = normalizedStatus.scraped > 0 
          ? Math.max(0, normalizedStatus.emails_found - normalizedStatus.emails_verified)
          : 0
        // Show job status if verification is running
        if (latestVerificationJob?.status === 'running') return 'Verifying...'
        if (latestVerificationJob?.status === 'pending') return 'Starting...'
        if (verifyReady === 0 && normalizedStatus.scraped === 0) return 'Scrape Websites First'
        if (verifyReady === 0) return 'No Prospects Ready'
        if (normalizedStatus.emails_verified > 0) return 'View Verified'
        return 'Start Verification'
      })(),
      ctaAction: () => {
        // CRITICAL: Check verify-ready count before calling backend
        // Backend will reject with 400 if no eligible prospects
        // Calculate from backend status (emails_found - emails_verified)
        const verifyReady = normalizedStatus.scraped > 0 
          ? Math.max(0, normalizedStatus.emails_found - normalizedStatus.emails_verified)
          : 0
        if (verifyReady === 0) {
          if (normalizedStatus.scraped === 0) {
            alert('Please scrape websites first to extract emails')
          } else {
            alert('No prospects ready for verification. All scraped prospects with emails are already verified.')
          }
          return
        }
        // If verification is already running, show message
        if (latestVerificationJob?.status === 'running' || latestVerificationJob?.status === 'pending') {
          alert(`Verification is already running (Job ID: ${latestVerificationJob.id}). Check the Jobs tab for progress.`)
          return
        }
        handleVerify()
      },
      jobStatus: latestVerificationJob?.status
    },
    {
      id: 4,
      name: 'Drafting',
      description: 'Generate outreach emails with Gemini',
      icon: FileText,
      // BACKEND AUTHORITY: Draft-ready = verified + email + draft_status = 'pending'
      // Backend returns drafting_ready_count (verified + email)
      // Note: Backend also requires draft_status = 'pending', which we can't check from status
      // Lock if backend says no draft-ready prospects (backend will reject with 422)
      status: normalizedStatus.drafting_ready_count === 0 
        ? 'locked'
        : (normalizedStatus.drafted > 0 ? 'completed' : 'active'),
      count: normalizedStatus.drafted,
      ctaText: normalizedStatus.drafted > 0 ? 'View Drafts' :
               normalizedStatus.drafting_ready_count === 0 ? 'Verify Leads First' :
               'Start Drafting',
      ctaAction: () => {
        // CRITICAL: Check backend's draft-ready count before calling
        // Backend will reject with 422 if no eligible prospects
        if (normalizedStatus.drafting_ready_count === 0) {
          alert('No prospects ready for drafting. Ensure prospects are verified and have emails.')
          return
        }
        handleDraft()
      }
    },
    {
      id: 5,
      name: 'Sending',
      description: 'Send emails via Gmail API',
      icon: Send,
      // UNLOCK when drafts exist (drafted > 0) OR when send-ready exists (send_ready_count > 0)
      // Backend will filter to only send verified + drafted + not sent prospects
      status: (normalizedStatus.drafted > 0 || normalizedStatus.send_ready_count > 0)
        ? (normalizedStatus.sent > 0 ? 'completed' : 'active')
        : 'locked',
      count: normalizedStatus.sent,
      ctaText: normalizedStatus.sent > 0 ? 'View Sent' :
               normalizedStatus.drafted > 0 || normalizedStatus.send_ready_count > 0 ? 'Start Sending' :
               'No Emails Ready',
      ctaAction: () => {
        if (normalizedStatus.send_ready_count === 0 && normalizedStatus.drafted === 0) {
          alert('No emails ready for sending. Ensure prospects have verified email, draft subject, and draft body.')
          return
        }
        handleSend()
      }
    }
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white/90 backdrop-blur-sm rounded-2xl shadow-lg border-2 border-gray-200/60 p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-2xl font-bold text-gray-900">Lead Acquisition Pipeline</h2>
          <button
            onClick={loadStatus}
            className="flex items-center space-x-2 px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-md"
          >
            <RefreshCw className="w-4 h-4" />
            <span>Refresh</span>
          </button>
        </div>
        <p className="text-gray-600 text-sm">
          Orchestrate your lead acquisition process step by step. Each stage must be completed before the next can begin.
        </p>
      </div>

      {/* Step Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {steps.map((step, index) => {
          const Icon = step.icon
          const isCompleted = step.status === 'completed'
          const isLocked = step.status === 'locked'
          const isActive = step.status === 'active'
          
          return (
            <div
              key={step.id}
              className={`bg-white/90 backdrop-blur-sm rounded-2xl shadow-lg border-2 p-6 ${
                isCompleted
                  ? 'border-green-500'
                  : isLocked
                  ? 'border-gray-300 opacity-60'
                  : 'border-olive-600'
              }`}
            >
              <div className="flex items-start justify-between mb-4">
                <div className={`p-3 rounded-full ${
                  isCompleted
                    ? 'bg-green-500 text-white'
                    : isLocked
                    ? 'bg-gray-300 text-gray-500'
                    : 'bg-olive-600 text-white'
                }`}>
                  <Icon className="w-6 h-6" />
                </div>
                {isCompleted && (
                  <CheckCircle2 className="w-6 h-6 text-green-500" />
                )}
                {isLocked && (
                  <Lock className="w-6 h-6 text-gray-400" />
                )}
              </div>

              <h3 className="text-lg font-bold text-gray-900 mb-2">{step.name}</h3>
              <p className="text-sm text-gray-600 mb-4">{step.description}</p>

              <div className="flex items-center justify-between mb-4">
                <div>
                  <p className="text-2xl font-bold text-gray-900">{step.count}</p>
                  <p className="text-xs text-gray-500">
                    {step.id === 1 && `${normalizedStatus.discovered} discovered`}
                    {step.id === 2 && `${normalizedStatus.scraped} scraped • ${normalizedStatus.email_found || 0} with emails`}
                    {step.id === 3 && `${normalizedStatus.leads} leads • ${normalizedStatus.emails_verified} verified`}
                    {step.id === 4 && `${normalizedStatus.drafting_ready || 0} ready • ${normalizedStatus.drafted} drafted`}
                    {step.id === 5 && `${normalizedStatus.sent} sent`}
                    {!step.id && `${step.count} ${step.count === 1 ? 'item' : 'items'} ${isCompleted ? 'completed' : 'ready'}`}
                  </p>
                  {step.id === 2 && (
                    <div className="mt-1 space-y-1">
                      <p className="text-xs text-gray-500">
                        Discovered: {normalizedStatus.discovered} • Scrape-ready: {normalizedStatus.scrape_ready_count}
                      </p>
                      {normalizedStatus.scrape_ready_count === 0 && (
                        <p className="text-xs text-red-500">
                          Blocked: No discovered websites yet. Run discovery first.
                        </p>
                      )}
                    </div>
                  )}
                  {step.id === 3 && (
                    <div className="mt-1 space-y-1">
                      <p className="text-xs text-gray-500">
                        Scraped with emails: {normalizedStatus.emails_found || 0} • Verified: {normalizedStatus.emails_verified}
                      </p>
                      {latestVerificationJob && (
                        <p className={`text-xs ${
                          latestVerificationJob.status === 'running' ? 'text-yellow-600' :
                          latestVerificationJob.status === 'completed' ? 'text-green-600' :
                          latestVerificationJob.status === 'failed' ? 'text-red-600' :
                          'text-gray-500'
                        }`}>
                          {latestVerificationJob.status === 'running' && '🔄 Verification in progress...'}
                          {latestVerificationJob.status === 'pending' && '⏳ Verification starting...'}
                          {latestVerificationJob.status === 'completed' && '✅ Verification completed! Check verified count above.'}
                          {latestVerificationJob.status === 'failed' && `❌ Verification failed: ${latestVerificationJob.error_message || 'Unknown error'}`}
                        </p>
                      )}
                      {normalizedStatus.emails_verified > 0 && (
                        <p className="text-xs text-green-600">
                          ✓ {normalizedStatus.emails_verified} verified emails ready for drafting
                        </p>
                      )}
                      {(() => {
                        const verifyReady = normalizedStatus.scraped > 0 
                          ? Math.max(0, normalizedStatus.emails_found - normalizedStatus.emails_verified)
                          : 0
                        if (verifyReady > 0 && !latestVerificationJob) {
                          return (
                            <p className="text-xs text-blue-600">
                              {verifyReady} scraped emails ready to verify
                            </p>
                          )
                        }
                        return null
                      })()}
                    </div>
                  )}
                </div>
                {step.jobStatus && (
                  <span className={`px-2 py-1 rounded text-xs font-medium ${
                    step.jobStatus === 'completed' ? 'bg-green-100 text-green-800' :
                    step.jobStatus === 'running' ? 'bg-yellow-100 text-yellow-800' :
                    step.jobStatus === 'failed' ? 'bg-red-100 text-red-800' :
                    'bg-gray-100 text-gray-800'
                  }`}>
                    {step.jobStatus}
                  </span>
                )}
              </div>

              <button
                onClick={step.ctaAction}
                disabled={isLocked}
                className={`w-full px-4 py-2 rounded-md font-medium flex items-center justify-center space-x-2 ${
                  isLocked
                    ? 'bg-gray-200 text-gray-500 cursor-not-allowed'
                    : isCompleted
                    ? 'bg-green-100 text-green-700 hover:bg-green-200'
                    : 'bg-olive-600 text-white hover:bg-olive-700'
                }`}
              >
                <span>{step.ctaText}</span>
                {!isLocked && <ArrowRight className="w-4 h-4" />}
              </button>
            </div>
          )
        })}
      </div>

      {/* Discovery Form (shown when triggered) */}
      <Step1Discovery onComplete={loadStatus} />
    </div>
  )
}

// Step 1 Discovery Form Component
function Step1Discovery({ onComplete }: { onComplete: () => void }) {
  const [showForm, setShowForm] = useState(false)
  const [categories, setCategories] = useState<string[]>([])
  const [locations, setLocations] = useState<string[]>([])
  const [keywords, setKeywords] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState(false)

  useEffect(() => {
    const handleShowForm = () => setShowForm(true)
    window.addEventListener('show-discovery-form', handleShowForm)
    return () => window.removeEventListener('show-discovery-form', handleShowForm)
  }, [])

  const availableCategories = [
    'Art Gallery', 'Museum', 'Art Studio', 'Art School', 'Art Fair', 
    'Art Dealer', 'Art Consultant', 'Art Publisher', 'Art Magazine'
  ]

  const availableLocations = [
    'United States', 'United Kingdom', 'Canada', 'Australia', 'Germany',
    'France', 'Italy', 'Spain', 'Netherlands', 'Belgium'
  ]

  const handleDiscover = async () => {
    if (categories.length === 0) {
      setError('Please select at least one category')
      return
    }
    if (locations.length === 0) {
      setError('Please select at least one location')
      return
    }

    setLoading(true)
    setError(null)
    setSuccess(false)

    try {
      await pipelineDiscover({
        categories,
        locations,
        keywords: keywords.trim() || undefined,
        max_results: 100
      })
      setSuccess(true)
      setShowForm(false)
      setTimeout(() => {
        onComplete()
        setSuccess(false)
      }, 2000)
    } catch (err: any) {
      setError(err.message || 'Failed to start discovery')
    } finally {
      setLoading(false)
    }
  }

  if (!showForm) return null

  return (
    <div className="bg-white/90 backdrop-blur-sm rounded-2xl shadow-lg border-2 border-gray-200/60 p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-xl font-bold text-gray-900">Step 1: Website Discovery</h3>
        <button
          onClick={() => setShowForm(false)}
          className="text-gray-500 hover:text-gray-700"
        >
          ×
        </button>
      </div>
      
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Categories (Required) *
          </label>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
            {availableCategories.map(cat => (
              <label key={cat} className="flex items-center space-x-2 p-2 border rounded hover:bg-gray-50 cursor-pointer">
                <input
                  type="checkbox"
                  checked={categories.includes(cat)}
                  onChange={(e) => {
                    if (e.target.checked) {
                      setCategories([...categories, cat])
                    } else {
                      setCategories(categories.filter(c => c !== cat))
                    }
                  }}
                />
                <span className="text-sm">{cat}</span>
              </label>
            ))}
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Locations (Required) *
          </label>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-2">
            {availableLocations.map(loc => (
              <label key={loc} className="flex items-center space-x-2 p-2 border rounded hover:bg-gray-50 cursor-pointer">
                <input
                  type="checkbox"
                  checked={locations.includes(loc)}
                  onChange={(e) => {
                    if (e.target.checked) {
                      setLocations([...locations, loc])
                    } else {
                      setLocations(locations.filter(l => l !== loc))
                    }
                  }}
                />
                <span className="text-sm">{loc}</span>
              </label>
            ))}
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Keywords (Optional)
          </label>
          <input
            type="text"
            value={keywords}
            onChange={(e) => setKeywords(e.target.value)}
            placeholder="e.g., contemporary art, abstract painting"
            className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-olive-500 focus:border-olive-500"
          />
        </div>

        {error && (
          <div className="p-3 bg-red-50 border border-red-200 rounded text-red-700 text-sm">
            {error}
          </div>
        )}

        {success && (
          <div className="p-3 bg-green-50 border border-green-200 rounded text-green-700 text-sm">
            ✅ Discovery job started! Check the Websites tab to see results.
          </div>
        )}

        <button
          onClick={handleDiscover}
          disabled={loading || categories.length === 0 || locations.length === 0}
          className="w-full px-6 py-3 bg-olive-600 text-white rounded-md hover:bg-olive-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
        >
          {loading ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              <span>Starting Discovery...</span>
            </>
          ) : (
            <>
              <Search className="w-5 h-5" />
              <span>Find Websites</span>
            </>
          )}
        </button>
      </div>
    </div>
  )
}
