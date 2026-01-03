'use client'
// Version: 3.1 - Discovery feature removed - FORCE REDEPLOY

import { useEffect, useState, useCallback, useRef } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import StatsCards from '@/components/StatsCards'
import LeadsTable from '@/components/LeadsTable'
import EmailsTable from '@/components/EmailsTable'
import JobStatusPanel from '@/components/JobStatusPanel'
import ActivityFeed from '@/components/ActivityFeed'
import AutomationControl from '@/components/AutomationControl'
import ManualScrape from '@/components/ManualScrape'
import WebsitesTable from '@/components/WebsitesTable'
import SystemStatus from '@/components/SystemStatus'
import Sidebar from '@/components/Sidebar'
import Pipeline from '@/components/Pipeline'
import { getStats, listJobs } from '@/lib/api'
import type { Stats, Job } from '@/lib/api'
import { 
  LayoutDashboard, 
  Globe, 
  Users, 
  Mail, 
  Settings, 
  Activity,
  AtSign,
  LogOut as LogOutIcon,
  BookOpen,
  RefreshCw
} from 'lucide-react'

export default function Dashboard() {
  const router = useRouter()
  const [stats, setStats] = useState<Stats | null>(null)
  const [jobs, setJobs] = useState<Job[]>([])
  const [loading, setLoading] = useState(true)
  const [connectionError, setConnectionError] = useState(false)
  const [activeTab, setActiveTab] = useState<
    'overview' | 'pipeline' | 'leads' | 'scraped_emails' | 'emails' | 'jobs' | 'websites' | 'settings' | 'guide'
  >('pipeline')  // Pipeline-first: default to Pipeline tab

  // Track if we've already triggered refresh for completed jobs to prevent loops
  const hasTriggeredRefresh = useRef(false)

  const loadData = useCallback(async (isInitialLoad = false) => {
    try {
      const [statsData, jobsData] = await Promise.all([
        getStats().catch(err => {
          console.warn('Failed to get stats:', err.message)
          return null
        }),
        listJobs(0, 20).catch(err => {
          console.warn('Failed to get jobs:', err.message)
          return []
        }),
      ])
      
      if (statsData) setStats(statsData)
      // Ensure jobsData is always an array
      const jobsArray = Array.isArray(jobsData) ? jobsData : []
      setJobs(jobsArray)
      
      // Check for completed discovery jobs and trigger refresh (only once on initial load)
      // This prevents infinite loops from repeated refreshes
      if (isInitialLoad && !hasTriggeredRefresh.current) {
        const completedDiscoveryJobs = jobsArray.filter(
          (job: any) => job.job_type === 'discover' && job.status === 'completed'
        )
        
        if (completedDiscoveryJobs.length > 0) {
          // Get the most recent completed discovery job
          const latestJob = completedDiscoveryJobs.sort((a: any, b: any) => {
            const dateA = new Date(a.updated_at || a.created_at || 0).getTime()
            const dateB = new Date(b.updated_at || b.created_at || 0).getTime()
            return dateB - dateA
          })[0]
          
          console.log('🔄 Found completed discovery job, triggering refresh...', latestJob.id)
          hasTriggeredRefresh.current = true
          // Dispatch event to refresh all tables
          // Use setTimeout to ensure tables are mounted
          setTimeout(() => {
            if (typeof window !== 'undefined') {
              window.dispatchEvent(new CustomEvent('jobsCompleted'))
            }
          }, 500)
        }
      }
      
      const backendResponding = statsData !== null || jobsArray.length > 0
      setConnectionError(!backendResponding)
    } catch (error: any) {
      console.error('Error loading data:', error)
      const isConnectionError = 
        error.message?.includes('Failed to fetch') || 
        error.message?.includes('ERR_CONNECTION_REFUSED') ||
        error.message?.includes('NetworkError')
      
      if (isConnectionError) {
        setConnectionError(true)
      }
    } finally {
      // Always set loading to false after initial load completes
      if (isInitialLoad) {
        setLoading(false)
      }
    }
  }, [])

  useEffect(() => {
    // Check if user is authenticated
    const token = typeof window !== 'undefined' ? localStorage.getItem('auth_token') : null
    if (!token) {
      router.push('/login')
      return
    }

    // Initial load with timeout to prevent infinite loading
    const loadTimeout = setTimeout(() => {
      console.warn('⚠️ Load data timeout - setting loading to false')
      setLoading(false)
    }, 10000) // 10 second timeout

    loadData(true).finally(() => {
      clearTimeout(loadTimeout)
    })
    
    // Refresh every 30 seconds (debounced to prevent loops) - increased from 10s
    const interval = setInterval(() => {
      loadData(false) // Don't set loading state on periodic refreshes
    }, 30000)
    
    // Listen for tab change events from Pipeline component
    const handleTabChange = (e: CustomEvent) => {
      const tabId = e.detail as string
      if (tabId && ['overview', 'pipeline', 'leads', 'scraped_emails', 'emails', 'jobs', 'websites', 'settings', 'guide'].includes(tabId)) {
        setActiveTab(tabId as any)
      }
    }
    
    window.addEventListener('change-tab', handleTabChange as EventListener)
    
    return () => {
      clearInterval(interval)
      clearTimeout(loadTimeout)
      window.removeEventListener('change-tab', handleTabChange as EventListener)
    }
  }, [router, loadData])

  const refreshData = () => {
    loadData(false)
    // Also trigger the jobsCompleted event to refresh all tables
    if (typeof window !== 'undefined') {
      window.dispatchEvent(new CustomEvent('jobsCompleted'))
    }
  }

  const tabs = [
    { id: 'overview', label: 'Overview', icon: LayoutDashboard },
    { id: 'social', label: 'Social Outreach', icon: AtSign, route: '/social' },
    { id: 'pipeline', label: 'Pipeline', icon: Activity },
    { id: 'websites', label: 'Websites', icon: Globe },
    { id: 'leads', label: 'Leads', icon: Users },
    { id: 'scraped_emails', label: 'Scraped Emails', icon: AtSign },
    { id: 'emails', label: 'Outreach Emails', icon: Mail },
    { id: 'jobs', label: 'Jobs', icon: Activity },
    { id: 'settings', label: 'Settings', icon: Settings },
    { id: 'guide', label: 'Guide', icon: BookOpen },
  ]

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 via-blue-50/30 to-purple-50/20">
        <div className="text-center animate-fade-in">
          <div className="inline-block relative">
            <div className="w-16 h-16 rounded-full border-4 border-liquid-200"></div>
            <div className="absolute top-0 left-0 w-16 h-16 rounded-full border-4 border-t-liquid-500 border-r-purple-500 animate-spin"></div>
          </div>
          <div className="mt-6">
            <h2 className="text-2xl font-bold liquid-gradient-text mb-2">Liquid Canvas</h2>
            <div className="text-lg font-semibold text-gray-700">Loading your studio...</div>
            <div className="text-sm text-gray-500 mt-2">Connecting to backend</div>
          </div>
        </div>
      </div>
    )
  }

  // Wrapper function to handle type compatibility with Sidebar component
  const handleTabChange = (tab: string) => {
    setActiveTab(tab as 'overview' | 'pipeline' | 'leads' | 'scraped_emails' | 'emails' | 'jobs' | 'websites' | 'settings' | 'guide')
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-liquid-50 to-white flex">
      {/* Left Sidebar */}
      <Sidebar activeTab={activeTab} onTabChange={handleTabChange} tabs={tabs} />

      {/* Main Content Area */}
      <div className="flex-1 lg:ml-64 flex flex-col">
        {/* Top Header */}
        <header className="glass border-b border-gray-200/50 sticky top-0 z-30 shadow-sm backdrop-blur-xl">
          <div className="px-3 sm:px-4 py-2 flex items-center justify-between">
            <div>
              <h2 className="text-sm font-bold text-olive-700">
                {tabs.find(t => t.id === activeTab)?.label || 'Dashboard'}
              </h2>
              <p className="text-xs text-gray-500 mt-0.5">Liquid Canvas Outreach Studio</p>
            </div>
            <div className="flex items-center space-x-2">
              <button
                onClick={refreshData}
                className="flex items-center space-x-1 px-2 py-1 glass hover:bg-white/80 text-gray-700 rounded-lg transition-all duration-200 text-xs font-medium hover:shadow-md"
                title="Refresh all data"
              >
                <RefreshCw className="w-3 h-3" />
                <span>Refresh</span>
              </button>
              <button
                onClick={() => {
                  localStorage.removeItem('auth_token')
                  router.push('/login')
                }}
                className="flex items-center space-x-1 px-2 py-1 bg-olive-600 text-white rounded-lg transition-all duration-200 text-xs font-medium shadow-md hover:bg-olive-700"
              >
                <LogOutIcon className="w-3 h-3" />
                <span>Logout</span>
              </button>
            </div>
          </div>
        </header>

      {/* Connection Error Banner */}
      {connectionError && (
          <div className="px-3 sm:px-4 py-2">
          <div className="bg-red-50 border-l-4 border-red-500 rounded-lg p-2 shadow-sm">
            <div className="flex items-center">
              <div>
                <p className="text-xs font-medium text-red-800">
                  Backend not connected
                </p>
                <p className="text-xs text-red-600 mt-0.5">
                  Unable to connect to API server. Please ensure the backend is running.
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* System Status Bar */}
        <div className="px-3 sm:px-4 py-2">
        <SystemStatus jobs={jobs} loading={loading} />
      </div>

      {/* Main Content */}
        <main className="flex-1 px-3 sm:px-4 py-2 overflow-y-auto">
        {activeTab === 'overview' && (
          <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-12 gap-3">
            {/* Stats Cards - Full Width */}
            <div className="lg:col-span-12">
              {stats ? <StatsCards stats={stats} /> : (
                <div className="bg-white/90 backdrop-blur-sm rounded-2xl shadow-lg border-2 border-gray-200/60 p-6">
                  <p className="text-gray-500">Stats unavailable. Check backend connection.</p>
                </div>
              )}
            </div>

            {/* Left Column - Automation & Manual Scrape */}
            <div className="lg:col-span-7 space-y-3">
              <AutomationControl />
              <ManualScrape />
            </div>

            {/* Right Column - Jobs & Activity */}
            <div className="lg:col-span-5 space-y-3">
              {Array.isArray(jobs) && jobs.length > 0 ? (
                <JobStatusPanel jobs={jobs} onRefresh={refreshData} />
              ) : (
                <div className="bg-white/90 backdrop-blur-sm rounded-2xl shadow-lg border-2 border-gray-200/60 p-6">
                  <p className="text-gray-500">No jobs found.</p>
                </div>
              )}
              <ActivityFeed limit={15} autoRefresh={true} />
            </div>
          </div>
        )}

        {activeTab === 'pipeline' && (
          <div className="max-w-7xl mx-auto">
            <Pipeline />
          </div>
        )}

        {activeTab === 'websites' && (
          <div className="max-w-7xl mx-auto">
            <WebsitesTable />
          </div>
        )}

        {activeTab === 'leads' && (
          <div className="max-w-7xl mx-auto">
            <LeadsTable />
          </div>
        )}

        {activeTab === 'scraped_emails' && (
          <div className="max-w-7xl mx-auto">
            <LeadsTable emailsOnly />
          </div>
        )}

        {activeTab === 'emails' && (
          <div className="max-w-7xl mx-auto">
            <EmailsTable />
          </div>
        )}

        {activeTab === 'jobs' && Array.isArray(jobs) && jobs.length > 0 && (
          <div className="max-w-7xl mx-auto">
            <JobStatusPanel jobs={jobs} expanded onRefresh={refreshData} />
          </div>
        )}

        {activeTab === 'settings' && (
          <div className="max-w-4xl mx-auto bg-white rounded-lg shadow-sm border border-gray-200 p-3">
            <div className="text-center py-4">
              <Settings className="w-8 h-8 text-olive-600 mx-auto mb-2" />
              <h2 className="text-sm font-bold text-gray-900 mb-1">System Settings</h2>
              <p className="text-xs text-gray-600 mb-3">Configure and test all API integrations</p>
              <Link
                href="/settings"
                className="inline-flex items-center px-3 py-1.5 bg-olive-600 text-white rounded-md hover:bg-olive-700 transition-colors text-xs font-semibold"
              >
                <Settings className="w-3 h-3 mr-1" />
                Open Settings Page
              </Link>
            </div>
          </div>
        )}

        {activeTab === 'guide' && (
          <div className="max-w-4xl mx-auto bg-white rounded-lg shadow-sm border border-gray-200 p-3">
            <div className="text-center mb-3">
              <h2 className="text-sm font-bold text-gray-900 mb-1">User Guide</h2>
              <p className="text-xs text-gray-600">Complete documentation on how to use the Art Outreach Automation</p>
            </div>
            <div className="prose prose-sm max-w-none">
              <p className="text-xs text-gray-700 mb-2">
                For the complete user guide, please visit the dedicated guide page.
              </p>
              <a
                href="/guide"
                className="inline-flex items-center px-3 py-1.5 bg-olive-600 text-white rounded-md hover:bg-olive-700 transition-colors text-xs"
              >
                <BookOpen className="w-3 h-3 mr-1" />
                Open Full Guide
              </a>
            </div>
          </div>
        )}
      </main>
      </div>
    </div>
  )
}
