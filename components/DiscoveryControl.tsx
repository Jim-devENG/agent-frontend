'use client'

import { useState, useEffect } from 'react'
import { Search, Loader2, CheckCircle2, AlertCircle, BarChart3 } from 'lucide-react'

interface DiscoveryStatus {
  status: string
  last_run?: string
  result?: {
    discovered?: number
    new_websites?: number
    skipped?: number
    failed?: number
  }
  error?: string
  started_at?: string
  completed_at?: string
}

interface AutomationStatus {
  automation_enabled: boolean
  email_trigger_mode: string
  search_interval_seconds: number
}

interface Location {
  value: string
  label: string
}

interface Category {
  value: string
  label: string
}

export default function DiscoveryControl() {
  const [status, setStatus] = useState<DiscoveryStatus | null>(null)
  const [automationStatus, setAutomationStatus] = useState<AutomationStatus | null>(null)
  const [loading, setLoading] = useState(true)
  const [searching, setSearching] = useState(false)
  const [showStats, setShowStats] = useState(false)
  const [locations, setLocations] = useState<Location[]>([])
  const [categories, setCategories] = useState<Category[]>([])
  const [selectedLocation, setSelectedLocation] = useState<string>('')
  const [selectedCategories, setSelectedCategories] = useState<string[]>([])

  useEffect(() => {
    loadStatus()
    loadAutomationStatus()
    loadLocations()
    loadCategories()
    // Refresh every 10 seconds
    const interval = setInterval(() => {
      loadStatus()
      loadAutomationStatus()
    }, 10000)
    return () => clearInterval(interval)
  }, [])

  const loadLocations = async () => {
    try {
      const token = typeof window !== 'undefined' ? localStorage.getItem('auth_token') : null
      if (!token) return
      
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1'}/discovery/locations`,
        {
          headers: { 'Authorization': `Bearer ${token}` }
        }
      )
      if (response.ok) {
        const data = await response.json()
        setLocations(data.locations || [])
      }
    } catch (error) {
      console.error('Error loading locations:', error)
    }
  }

  const loadCategories = async () => {
    try {
      const token = typeof window !== 'undefined' ? localStorage.getItem('auth_token') : null
      if (!token) return
      
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1'}/discovery/categories`,
        {
          headers: { 'Authorization': `Bearer ${token}` }
        }
      )
      if (response.ok) {
        const data = await response.json()
        setCategories(data.categories || [])
      }
    } catch (error) {
      console.error('Error loading categories:', error)
    }
  }

  const loadStatus = async () => {
    try {
      const token = typeof window !== 'undefined' ? localStorage.getItem('auth_token') : null
      if (!token) return
      
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1'}/discovery/status`,
        {
          headers: { 'Authorization': `Bearer ${token}` }
        }
      )
      if (response.ok) {
        const data = await response.json()
        setStatus(data)
      }
    } catch (error) {
      console.error('Error loading discovery status:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadAutomationStatus = async () => {
    try {
      const token = typeof window !== 'undefined' ? localStorage.getItem('auth_token') : null
      if (!token) return
      
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1'}/automation/status`,
        {
          headers: { 'Authorization': `Bearer ${token}` }
        }
      )
      if (response.ok) {
        const data = await response.json()
        setAutomationStatus(data)
      }
    } catch (error) {
      console.error('Error loading automation status:', error)
    }
  }

  const triggerSearch = async () => {
    // Check if automation is enabled
    if (!isAutomationOn) {
      alert('Please enable automation (Master Switch) before running searches')
      return
    }
    
    setSearching(true)
    try {
      const token = typeof window !== 'undefined' ? localStorage.getItem('auth_token') : null
      if (!token) return
      
      // Build query params
      const params = new URLSearchParams()
      if (selectedLocation) {
        params.append('location', selectedLocation)
      }
      if (selectedCategories.length > 0) {
        params.append('categories', selectedCategories.join(','))
      }
      
      const url = `${process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1'}/discovery/search-now${params.toString() ? '?' + params.toString() : ''}`
      
      const response = await fetch(
        url,
        {
          method: 'POST',
          headers: { 'Authorization': `Bearer ${token}` }
        }
      )
      if (response.ok) {
        // Wait a moment then refresh status
        setTimeout(() => {
          loadStatus()
        }, 2000)
      } else {
        alert('Failed to start search')
      }
    } catch (error: any) {
      alert(`Error: ${error.message}`)
    } finally {
      setSearching(false)
    }
  }

  const stopSearch = async () => {
    try {
      const token = typeof window !== 'undefined' ? localStorage.getItem('auth_token') : null
      if (!token) return
      
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1'}/discovery/stop`,
        {
          method: 'POST',
          headers: { 'Authorization': `Bearer ${token}` }
        }
      )
      if (response.ok) {
        setTimeout(() => {
          loadStatus()
        }, 1000)
      } else {
        alert('Failed to stop search')
      }
    } catch (error: any) {
      alert(`Error: ${error.message}`)
    }
  }

  const formatTime = (timeString?: string) => {
    if (!timeString) return 'Never'
    const date = new Date(timeString)
    // Show actual time instead of "ago" format
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    })
  }

  // Only show "Search Now" button if automation is in manual mode
  const isManualMode = automationStatus?.email_trigger_mode === 'manual'
  const isAutomationOn = automationStatus?.automation_enabled

  return (
    <div className="bg-white/80 backdrop-blur-sm rounded-lg shadow-md border border-gray-200/50 p-3">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center space-x-1.5">
          <div className="p-1.5 bg-olive-600 rounded-md">
            <Search className="w-3.5 h-3.5 text-white" />
          </div>
          <h2 className="text-sm font-bold text-gray-900">Website Discovery</h2>
        </div>
        <button
          onClick={() => setShowStats(!showStats)}
          className="p-1.5 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md transition-colors"
          title="Show discovery statistics"
        >
          <BarChart3 className="w-3.5 h-3.5" />
        </button>
      </div>

      {/* Status Display */}
      {loading ? (
        <div className="flex items-center space-x-1.5 text-gray-600">
          <Loader2 className="w-3 h-3 animate-spin" />
          <span className="text-xs">Loading status...</span>
        </div>
      ) : (
        <div className="space-y-2">
          {/* Current Status */}
          <div className="flex items-center space-x-2">
            {status?.status === 'running' ? (
              <>
                <Loader2 className="w-3.5 h-3.5 text-olive-600 animate-spin" />
                <div>
                  <p className="text-xs font-medium text-gray-900">Searching Internet...</p>
                  <p className="text-xs text-gray-600">
                    {status.started_at ? `Started: ${formatTime(status.started_at)}` : 'In progress'}
                  </p>
                </div>
              </>
            ) : status?.status === 'completed' ? (
              <>
                <CheckCircle2 className="w-3.5 h-3.5 text-green-500" />
                <div>
                  <p className="text-xs font-medium text-gray-900">Last Search Completed</p>
                  <p className="text-xs text-gray-600">
                    {status.completed_at ? formatTime(status.completed_at) : 'Unknown'}
                  </p>
                </div>
              </>
            ) : status?.status === 'failed' ? (
              <>
                <AlertCircle className="w-3.5 h-3.5 text-red-500" />
                <div>
                  <p className="text-xs font-medium text-gray-900">Last Search Failed</p>
                  <p className="text-xs text-red-600">{status.error || 'Unknown error'}</p>
                </div>
              </>
            ) : (
              <>
                <AlertCircle className="w-3.5 h-3.5 text-gray-400" />
                <div>
                  <p className="text-xs font-medium text-gray-900">Never Run</p>
                  <p className="text-xs text-gray-600">No searches have been performed yet</p>
                </div>
              </>
            )}
            </div>
            {status?.status === 'running' && (
              <button
                onClick={stopSearch}
                className="px-2 py-1 bg-red-600 hover:bg-red-700 text-white rounded-md transition-colors text-xs flex items-center space-x-1"
                title="Stop current search"
              >
                <Square className="w-3 h-3" />
                <span>Stop</span>
              </button>
            )}
          </div>

          {/* Statistics Panel (Toggle) */}
          {showStats && status?.result && (
            <div className="bg-gray-50 rounded-md p-2 border border-gray-200">
              <h3 className="text-xs font-semibold text-gray-700 mb-2">Last Search Results</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                <div>
                  <p className="text-xs text-gray-600">Discovered</p>
                  <p className="text-sm font-bold text-gray-900">
                    {status.result.discovered || 0}
                  </p>
                </div>
                <div>
                  <p className="text-xs text-gray-600">New Websites</p>
                  <p className="text-sm font-bold text-green-600">
                    {status.result.new_websites || 0}
                  </p>
                </div>
                <div>
                  <p className="text-xs text-gray-600">Skipped</p>
                  <p className="text-sm font-bold text-yellow-600">
                    {status.result.skipped || 0}
                  </p>
                </div>
                <div>
                  <p className="text-xs text-gray-600">Failed</p>
                  <p className="text-sm font-bold text-red-600">
                    {status.result.failed || 0}
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Location and Category Selection */}
          <div className="space-y-2 border-t pt-2 mt-2">
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">
                Search Location
              </label>
              <select
                value={selectedLocation}
                onChange={(e) => setSelectedLocation(e.target.value)}
                className="w-full px-2 py-1.5 border border-gray-300 rounded-md text-xs focus:ring-2 focus:ring-olive-500 focus:border-transparent"
              >
                <option value="">All Locations</option>
                {locations.map((loc) => (
                  <option key={loc.value} value={loc.value}>
                    {loc.label}
                  </option>
                ))}
              </select>
            </div>
            
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">
                Categories (Optional - leave empty for all)
              </label>
              <div className="space-y-1 max-h-32 overflow-y-auto border border-gray-200 rounded-md p-1.5">
                {categories.map((cat) => (
                  <label key={cat.value} className="flex items-center space-x-1.5 text-xs">
                    <input
                      type="checkbox"
                      checked={selectedCategories.includes(cat.value)}
                      onChange={(e) => {
                        if (e.target.checked) {
                          setSelectedCategories([...selectedCategories, cat.value])
                        } else {
                          setSelectedCategories(selectedCategories.filter(c => c !== cat.value))
                        }
                      }}
                      className="rounded border-gray-300 text-olive-600 focus:ring-olive-500"
                    />
                    <span>{cat.label}</span>
                  </label>
                ))}
              </div>
            </div>
          </div>

          {/* Automation Info */}
          {isAutomationOn && (
            <div className="bg-olive-50 border border-olive-200 rounded-md p-2 mt-2">
              <p className="text-xs text-olive-800">
                <strong>Automatic Mode:</strong> Searching every {automationStatus?.search_interval_seconds ? Math.floor(automationStatus.search_interval_seconds / 60) : '15'} minutes
              </p>
              <p className="text-xs text-olive-600 mt-0.5">
                The system will automatically discover and scrape websites every 15 minutes.
                You can also trigger manual searches anytime using the button above.
              </p>
            </div>
          )}

          {/* Manual Search Button - Only when automation is ON */}
          {isAutomationOn && (
            <div className="border-t pt-2 mt-2">
              <button
                onClick={triggerSearch}
                disabled={searching || status?.status === 'running'}
                className="w-full px-3 py-2 bg-olive-600 text-white rounded-md font-medium hover:bg-olive-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-sm hover:shadow-md flex items-center justify-center space-x-1.5 text-sm"
              >
                {searching || status?.status === 'running' ? (
                  <>
                    <Loader2 className="w-3.5 h-3.5 animate-spin" />
                    <span>Searching...</span>
                  </>
                ) : (
                  <>
                    <Search className="w-3.5 h-3.5" />
                    <span>Search Now (Manual)</span>
                  </>
                )}
              </button>
              <p className="text-xs text-gray-500 mt-1.5 text-center">
                Manual search works independently of automatic schedule. Next automatic search in ~15 minutes.
              </p>
            </div>
          )}
          {!isAutomationOn && (
            <div className="border-t pt-2 mt-2 p-2 bg-yellow-50 border-yellow-200 rounded-md">
              <p className="text-xs text-yellow-800 text-center">
                Enable automation (Master Switch) to use manual search
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
