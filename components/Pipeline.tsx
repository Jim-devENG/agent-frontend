'use client'

import { useEffect, useState } from 'react'
import { CheckCircle2, Circle, Lock, Loader2, Search, Users, Scissors, Shield, Eye, FileText, Send, RefreshCw } from 'lucide-react'
import { 
  pipelineDiscover, 
  pipelineApprove, 
  pipelineScrape, 
  pipelineVerify, 
  pipelineReview, 
  pipelineDraft, 
  pipelineSend, 
  pipelineStatus,
  listProspects,
  type Prospect,
  type PipelineStatus as PipelineStatusType
} from '@/lib/api'

interface Step {
  id: number
  name: string
  description: string
  icon: any
  status: 'pending' | 'active' | 'completed' | 'locked'
  count?: number
}

export default function Pipeline() {
  const [steps, setSteps] = useState<Step[]>([])
  const [status, setStatus] = useState<PipelineStatusType | null>(null)
  const [loading, setLoading] = useState(true)
  const [activeStep, setActiveStep] = useState<number>(1)
  const [prospects, setProspects] = useState<Prospect[]>([])

  const loadStatus = async () => {
    try {
      const statusData = await pipelineStatus()
      setStatus(statusData)
      
      // Update steps based on status
      const newSteps: Step[] = [
        {
          id: 1,
          name: 'Website Discovery',
          description: 'Find websites using DataForSEO',
          icon: Search,
          status: statusData.discovered > 0 ? 'completed' : 'active',
          count: statusData.discovered
        },
        {
          id: 2,
          name: 'Human Selection',
          description: 'Review and approve websites',
          icon: Users,
          status: statusData.discovered === 0 ? 'locked' : 
                 statusData.approved > 0 ? 'completed' : 'active',
          count: statusData.approved
        },
        {
          id: 3,
          name: 'Scraping',
          description: 'Extract emails from websites',
          icon: Scissors,
          status: statusData.approved === 0 ? 'locked' :
                 statusData.scraped > 0 ? 'completed' : 'active',
          count: statusData.scraped
        },
        {
          id: 4,
          name: 'Verification',
          description: 'Verify emails with Snov.io',
          icon: Shield,
          status: statusData.scraped === 0 ? 'locked' :
                 statusData.verified > 0 ? 'completed' : 'active',
          count: statusData.verified
        },
        {
          id: 5,
          name: 'Email Review',
          description: 'Manually review verified emails',
          icon: Eye,
          status: statusData.verified === 0 ? 'locked' :
                 statusData.reviewed > 0 ? 'completed' : 'active',
          count: statusData.reviewed
        },
        {
          id: 6,
          name: 'Drafting',
          description: 'Generate outreach emails with Gemini',
          icon: FileText,
          status: statusData.reviewed === 0 ? 'locked' :
                 statusData.drafted > 0 ? 'completed' : 'active',
          count: statusData.drafted
        },
        {
          id: 7,
          name: 'Sending',
          description: 'Send emails via Gmail API',
          icon: Send,
          status: statusData.drafted === 0 ? 'locked' :
                 statusData.sent > 0 ? 'completed' : 'active',
          count: statusData.sent
        }
      ]
      
      setSteps(newSteps)
      
      // Determine active step
      if (statusData.sent > 0) setActiveStep(7)
      else if (statusData.drafted > 0) setActiveStep(6)
      else if (statusData.reviewed > 0) setActiveStep(5)
      else if (statusData.verified > 0) setActiveStep(4)
      else if (statusData.scraped > 0) setActiveStep(3)
      else if (statusData.approved > 0) setActiveStep(2)
      else if (statusData.discovered > 0) setActiveStep(1)
      else setActiveStep(1)
      
    } catch (error) {
      console.error('Failed to load pipeline status:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadStatus()
    const interval = setInterval(loadStatus, 10000) // Refresh every 10 seconds
    return () => clearInterval(interval)
  }, [])

  const loadProspects = async (step: number) => {
    try {
      let query: any = {}
      
      if (step === 1) {
        // Discovered prospects
        query = { discovery_status: 'DISCOVERED' }
      } else if (step === 2) {
        // Discovered but not yet approved/rejected
        const all = await listProspects(0, 1000)
        const discovered = all.data.filter((p: Prospect) => 
          p.discovery_status === 'DISCOVERED' && 
          (!p.approval_status || p.approval_status === 'pending')
        )
        setProspects(discovered)
        return
      } else if (step === 3) {
        // Approved prospects ready for scraping
        const all = await listProspects(0, 1000)
        const approved = all.data.filter((p: Prospect) => 
          p.approval_status === 'approved' && 
          (!p.scrape_status || p.scrape_status === 'pending')
        )
        setProspects(approved)
        return
      } else if (step === 4) {
        // Scraped prospects ready for verification
        const all = await listProspects(0, 1000)
        const scraped = all.data.filter((p: Prospect) => 
          p.scrape_status === 'SCRAPED' && 
          (!p.verification_status || p.verification_status === 'pending')
        )
        setProspects(scraped)
        return
      } else if (step === 5) {
        // Verified prospects for review
        const review = await pipelineReview()
        setProspects(review.data as any)
        return
      } else if (step === 6) {
        // Verified prospects ready for drafting
        const all = await listProspects(0, 1000)
        const verified = all.data.filter((p: Prospect) => 
          p.verification_status && 
          ['verified', 'unverified'].includes(p.verification_status) &&
          p.contact_email &&
          (!p.draft_status || p.draft_status === 'pending')
        )
        setProspects(verified)
        return
      } else if (step === 7) {
        // Drafted prospects ready for sending
        const all = await listProspects(0, 1000)
        const drafted = all.data.filter((p: Prospect) => 
          p.draft_status === 'drafted' &&
          (!p.send_status || p.send_status === 'pending')
        )
        setProspects(drafted)
        return
      }
      
      const response = await listProspects(0, 1000)
      setProspects(response.data)
    } catch (error) {
      console.error('Failed to load prospects:', error)
      setProspects([])
    }
  }

  useEffect(() => {
    if (activeStep) {
      loadProspects(activeStep)
    }
  }, [activeStep])

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

  return (
    <div className="space-y-6">
      {/* Pipeline Steps Tracker */}
      <div className="bg-white/90 backdrop-blur-sm rounded-2xl shadow-lg border-2 border-gray-200/60 p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-gray-900">Lead Acquisition Pipeline</h2>
          <button
            onClick={loadStatus}
            className="flex items-center space-x-2 px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-md"
          >
            <RefreshCw className="w-4 h-4" />
            <span>Refresh</span>
          </button>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-7 gap-4">
          {steps.map((step, index) => {
            const Icon = step.icon
            const isActive = step.id === activeStep
            const isCompleted = step.status === 'completed'
            const isLocked = step.status === 'locked'
            
            return (
              <button
                key={step.id}
                onClick={() => !isLocked && setActiveStep(step.id)}
                disabled={isLocked}
                className={`relative p-4 rounded-lg border-2 transition-all ${
                  isActive
                    ? 'border-olive-600 bg-olive-50 shadow-md'
                    : isCompleted
                    ? 'border-green-500 bg-green-50'
                    : isLocked
                    ? 'border-gray-300 bg-gray-100 opacity-50 cursor-not-allowed'
                    : 'border-gray-200 bg-white hover:border-gray-300'
                }`}
              >
                <div className="flex flex-col items-center space-y-2">
                  <div className={`p-3 rounded-full ${
                    isActive
                      ? 'bg-olive-600 text-white'
                      : isCompleted
                      ? 'bg-green-500 text-white'
                      : isLocked
                      ? 'bg-gray-300 text-gray-500'
                      : 'bg-gray-200 text-gray-600'
                  }`}>
                    {isLocked ? (
                      <Lock className="w-5 h-5" />
                    ) : isCompleted ? (
                      <CheckCircle2 className="w-5 h-5" />
                    ) : (
                      <Icon className="w-5 h-5" />
                    )}
                  </div>
                  <div className="text-center">
                    <p className={`text-sm font-semibold ${
                      isActive ? 'text-olive-700' : 
                      isCompleted ? 'text-green-700' : 
                      isLocked ? 'text-gray-500' : 'text-gray-700'
                    }`}>
                      {step.name}
                    </p>
                    {step.count !== undefined && step.count > 0 && (
                      <p className="text-xs text-gray-500 mt-1">
                        {step.count} {step.count === 1 ? 'item' : 'items'}
                      </p>
                    )}
                  </div>
                </div>
                {index < steps.length - 1 && (
                  <div className={`absolute top-1/2 -right-2 w-4 h-0.5 ${
                    isCompleted ? 'bg-green-500' : 'bg-gray-300'
                  }`} />
                )}
              </button>
            )
          })}
        </div>
      </div>

      {/* Active Step Content */}
      <div className="bg-white/90 backdrop-blur-sm rounded-2xl shadow-lg border-2 border-gray-200/60 p-6">
        {activeStep === 1 && <Step1Discovery onComplete={loadStatus} />}
        {activeStep === 2 && <Step2Selection prospects={prospects} onComplete={loadStatus} />}
        {activeStep === 3 && <Step3Scraping prospects={prospects} onComplete={loadStatus} />}
        {activeStep === 4 && <Step4Verification prospects={prospects} onComplete={loadStatus} />}
        {activeStep === 5 && <Step5Review prospects={prospects} onComplete={loadStatus} />}
        {activeStep === 6 && <Step6Drafting prospects={prospects} onComplete={loadStatus} />}
        {activeStep === 7 && <Step7Sending prospects={prospects} onComplete={loadStatus} />}
      </div>
    </div>
  )
}

// Step Components
function Step1Discovery({ onComplete }: { onComplete: () => void }) {
  const [categories, setCategories] = useState<string[]>([])
  const [locations, setLocations] = useState<string[]>([])
  const [keywords, setKeywords] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState(false)

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

  return (
    <div>
      <h3 className="text-xl font-bold text-gray-900 mb-4">Step 1: Website Discovery</h3>
      <p className="text-gray-600 mb-6">Find websites using DataForSEO. Select categories and locations to search.</p>
      
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
            ✅ Discovery job started! Check Step 2 to review discovered websites.
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

function Step2Selection({ prospects, onComplete }: { prospects: Prospect[], onComplete: () => void }) {
  const [selected, setSelected] = useState<Set<string>>(new Set())
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)

  const handleApprove = async () => {
    if (selected.size === 0) {
      setError('Please select at least one website to approve')
      return
    }

    setLoading(true)
    setError(null)
    setSuccess(null)

    try {
      const result = await pipelineApprove({
        prospect_ids: Array.from(selected),
        action: 'approve'
      })
      setSuccess(`Successfully approved ${result.approved_count} website(s)`)
      setSelected(new Set())
      setTimeout(() => {
        onComplete()
        setSuccess(null)
      }, 2000)
    } catch (err: any) {
      setError(err.message || 'Failed to approve websites')
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this website?')) return

    setLoading(true)
    try {
      await pipelineApprove({
        prospect_ids: [id],
        action: 'delete'
      })
      onComplete()
    } catch (err: any) {
      setError(err.message || 'Failed to delete website')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <h3 className="text-xl font-bold text-gray-900 mb-4">Step 2: Human Selection</h3>
      <p className="text-gray-600 mb-6">Review discovered websites. Select and approve the ones you want to proceed with.</p>
      
      {prospects.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          No discovered websites found. Complete Step 1 first.
        </div>
      ) : (
        <>
          <div className="mb-4 flex items-center justify-between">
            <p className="text-sm text-gray-600">
              {prospects.length} website(s) found • {selected.size} selected
            </p>
            <button
              onClick={handleApprove}
              disabled={loading || selected.size === 0}
              className="px-4 py-2 bg-olive-600 text-white rounded-md hover:bg-olive-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Approving...</span>
                </>
              ) : (
                <>
                  <CheckCircle2 className="w-4 h-4" />
                  <span>Approve Selected ({selected.size})</span>
                </>
              )}
            </button>
          </div>

          <div className="space-y-2 max-h-96 overflow-y-auto">
            {prospects.map(prospect => (
              <div
                key={prospect.id}
                className={`p-4 border rounded-lg flex items-center justify-between ${
                  selected.has(prospect.id) ? 'bg-olive-50 border-olive-300' : 'bg-white border-gray-200'
                }`}
              >
                <div className="flex items-center space-x-4 flex-1">
                  <input
                    type="checkbox"
                    checked={selected.has(prospect.id)}
                    onChange={(e) => {
                      const newSelected = new Set(selected)
                      if (e.target.checked) {
                        newSelected.add(prospect.id)
                      } else {
                        newSelected.delete(prospect.id)
                      }
                      setSelected(newSelected)
                    }}
                    className="w-4 h-4 text-olive-600"
                  />
                  <div className="flex-1">
                    <p className="font-medium text-gray-900">{prospect.domain}</p>
                    <p className="text-sm text-gray-600">{prospect.page_title || 'No title'}</p>
                  </div>
                </div>
                <button
                  onClick={() => handleDelete(prospect.id)}
                  className="px-3 py-1 text-sm text-red-600 hover:bg-red-50 rounded"
                >
                  Delete
                </button>
              </div>
            ))}
          </div>

          {error && (
            <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded text-red-700 text-sm">
              {error}
            </div>
          )}

          {success && (
            <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded text-green-700 text-sm">
              {success}
            </div>
          )}
        </>
      )}
    </div>
  )
}

function Step3Scraping({ prospects, onComplete }: { prospects: Prospect[], onComplete: () => void }) {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)

  const handleScrape = async () => {
    setLoading(true)
    setError(null)
    setSuccess(null)

    try {
      const result = await pipelineScrape()
      setSuccess(`Scraping job started for ${result.prospects_count} website(s)`)
      setTimeout(() => {
        onComplete()
        setSuccess(null)
      }, 2000)
    } catch (err: any) {
      setError(err.message || 'Failed to start scraping')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <h3 className="text-xl font-bold text-gray-900 mb-4">Step 3: Scraping</h3>
      <p className="text-gray-600 mb-6">Scrape approved websites to extract visible emails from homepage and contact pages.</p>
      
      {prospects.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          No approved websites found. Complete Step 2 first.
        </div>
      ) : (
        <>
          <div className="mb-4">
            <p className="text-sm text-gray-600 mb-4">
              {prospects.length} approved website(s) ready for scraping
            </p>
            <button
              onClick={handleScrape}
              disabled={loading}
              className="w-full px-6 py-3 bg-olive-600 text-white rounded-md hover:bg-olive-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
            >
              {loading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  <span>Starting Scraping...</span>
                </>
              ) : (
                <>
                  <Scissors className="w-5 h-5" />
                  <span>Scrape Selected Websites</span>
                </>
              )}
            </button>
          </div>

          {error && (
            <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded text-red-700 text-sm">
              {error}
            </div>
          )}

          {success && (
            <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded text-green-700 text-sm">
              {success}
            </div>
          )}
        </>
      )}
    </div>
  )
}

function Step4Verification({ prospects, onComplete }: { prospects: Prospect[], onComplete: () => void }) {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)

  const handleVerify = async () => {
    setLoading(true)
    setError(null)
    setSuccess(null)

    try {
      const result = await pipelineVerify()
      setSuccess(`Verification job started for ${result.prospects_count} prospect(s)`)
      setTimeout(() => {
        onComplete()
        setSuccess(null)
      }, 2000)
    } catch (err: any) {
      setError(err.message || 'Failed to start verification')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <h3 className="text-xl font-bold text-gray-900 mb-4">Step 4: Email Verification</h3>
      <p className="text-gray-600 mb-6">Verify scraped emails using Snov.io. If no emails were scraped, Snov will attempt domain search.</p>
      
      {prospects.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          No scraped websites found. Complete Step 3 first.
        </div>
      ) : (
        <>
          <div className="mb-4">
            <p className="text-sm text-gray-600 mb-4">
              {prospects.length} scraped website(s) ready for verification
            </p>
            <button
              onClick={handleVerify}
              disabled={loading}
              className="w-full px-6 py-3 bg-olive-600 text-white rounded-md hover:bg-olive-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
            >
              {loading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  <span>Starting Verification...</span>
                </>
              ) : (
                <>
                  <Shield className="w-5 h-5" />
                  <span>Verify Emails</span>
                </>
              )}
            </button>
          </div>

          {error && (
            <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded text-red-700 text-sm">
              {error}
            </div>
          )}

          {success && (
            <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded text-green-700 text-sm">
              {success}
            </div>
          )}
        </>
      )}
    </div>
  )
}

function Step5Review({ prospects, onComplete }: { prospects: any[], onComplete: () => void }) {
  const [confirmed, setConfirmed] = useState<Set<string>>(new Set())

  return (
    <div>
      <h3 className="text-xl font-bold text-gray-900 mb-4">Step 5: Email Review</h3>
      <p className="text-gray-600 mb-6">Review verified emails. Manually confirm each email before proceeding to drafting.</p>
      
      {prospects.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          No verified emails found. Complete Step 4 first.
        </div>
      ) : (
        <div className="space-y-4">
          {prospects.map((prospect: any) => (
            <div
              key={prospect.id}
              className={`p-4 border rounded-lg ${
                confirmed.has(prospect.id) ? 'bg-green-50 border-green-300' : 'bg-white border-gray-200'
              }`}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <p className="font-medium text-gray-900">{prospect.domain || prospect.email?.split('@')[1]}</p>
                  <p className="text-sm text-gray-600 mt-1">
                    <span className="font-medium">Email:</span> {prospect.email || prospect.contact_email}
                  </p>
                  <div className="mt-2 flex flex-wrap gap-2 text-xs">
                    <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded">
                      Source: {prospect.source || 'Unknown'}
                    </span>
                    <span className="px-2 py-1 bg-purple-100 text-purple-700 rounded">
                      Type: {prospect.type || 'generic'}
                    </span>
                    {prospect.confidence && (
                      <span className="px-2 py-1 bg-green-100 text-green-700 rounded">
                        Confidence: {prospect.confidence}%
                      </span>
                    )}
                    {prospect.verification_status && (
                      <span className={`px-2 py-1 rounded ${
                        prospect.verification_status === 'verified'
                          ? 'bg-green-100 text-green-700'
                          : 'bg-yellow-100 text-yellow-700'
                      }`}>
                        Status: {prospect.verification_status}
                      </span>
                    )}
                  </div>
                </div>
                <button
                  onClick={() => {
                    const newConfirmed = new Set(confirmed)
                    if (confirmed.has(prospect.id)) {
                      newConfirmed.delete(prospect.id)
                    } else {
                      newConfirmed.add(prospect.id)
                    }
                    setConfirmed(newConfirmed)
                  }}
                  className={`px-4 py-2 rounded-md text-sm font-medium ${
                    confirmed.has(prospect.id)
                      ? 'bg-green-600 text-white'
                      : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                  }`}
                >
                  {confirmed.has(prospect.id) ? 'Confirmed' : 'Confirm'}
                </button>
              </div>
            </div>
          ))}
          
          {confirmed.size > 0 && (
            <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded">
              <p className="text-sm text-blue-700">
                ✅ {confirmed.size} email(s) confirmed. You can proceed to Step 6: Drafting.
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

function Step6Drafting({ prospects, onComplete }: { prospects: Prospect[], onComplete: () => void }) {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)

  const handleDraft = async () => {
    if (prospects.length === 0) {
      setError('No prospects available for drafting')
      return
    }

    setLoading(true)
    setError(null)
    setSuccess(null)

    try {
      const result = await pipelineDraft({
        prospect_ids: prospects.map(p => p.id)
      })
      setSuccess(`Drafting job started for ${result.prospects_count} prospect(s)`)
      setTimeout(() => {
        onComplete()
        setSuccess(null)
      }, 2000)
    } catch (err: any) {
      setError(err.message || 'Failed to start drafting')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <h3 className="text-xl font-bold text-gray-900 mb-4">Step 6: Outreach Drafting</h3>
      <p className="text-gray-600 mb-6">Generate personalized outreach emails using Gemini AI based on website info, category, location, and email type.</p>
      
      {prospects.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          No verified prospects found. Complete Step 5 first.
        </div>
      ) : (
        <>
          <div className="mb-4">
            <p className="text-sm text-gray-600 mb-4">
              {prospects.length} verified prospect(s) ready for drafting
            </p>
            <button
              onClick={handleDraft}
              disabled={loading}
              className="w-full px-6 py-3 bg-olive-600 text-white rounded-md hover:bg-olive-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
            >
              {loading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  <span>Starting Drafting...</span>
                </>
              ) : (
                <>
                  <FileText className="w-5 h-5" />
                  <span>Generate Draft</span>
                </>
              )}
            </button>
          </div>

          {error && (
            <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded text-red-700 text-sm">
              {error}
            </div>
          )}

          {success && (
            <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded text-green-700 text-sm">
              {success}
            </div>
          )}
        </>
      )}
    </div>
  )
}

function Step7Sending({ prospects, onComplete }: { prospects: Prospect[], onComplete: () => void }) {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)

  const handleSend = async () => {
    if (prospects.length === 0) {
      setError('No prospects available for sending')
      return
    }

    setLoading(true)
    setError(null)
    setSuccess(null)

    try {
      const result = await pipelineSend({
        prospect_ids: prospects.map(p => p.id)
      })
      setSuccess(`Sending job started for ${result.prospects_count} prospect(s)`)
      setTimeout(() => {
        onComplete()
        setSuccess(null)
      }, 2000)
    } catch (err: any) {
      setError(err.message || 'Failed to start sending')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <h3 className="text-xl font-bold text-gray-900 mb-4">Step 7: Sending</h3>
      <p className="text-gray-600 mb-6">Send drafted emails via Gmail API. Success and failure will be logged.</p>
      
      {prospects.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          No drafted prospects found. Complete Step 6 first.
        </div>
      ) : (
        <>
          <div className="mb-4">
            <p className="text-sm text-gray-600 mb-4">
              {prospects.length} drafted prospect(s) ready for sending
            </p>
            <button
              onClick={handleSend}
              disabled={loading}
              className="w-full px-6 py-3 bg-olive-600 text-white rounded-md hover:bg-olive-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
            >
              {loading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  <span>Sending...</span>
                </>
              ) : (
                <>
                  <Send className="w-5 h-5" />
                  <span>Send Email</span>
                </>
              )}
            </button>
          </div>

          {error && (
            <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded text-red-700 text-sm">
              {error}
            </div>
          )}

          {success && (
            <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded text-green-700 text-sm">
              {success}
            </div>
          )}
        </>
      )}
    </div>
  )
}

