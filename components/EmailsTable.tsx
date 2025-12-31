'use client'

import { useEffect, useState } from 'react'
import { Mail, CheckCircle, XCircle, Clock, RefreshCw } from 'lucide-react'
import { listProspects, type Prospect } from '@/lib/api'

export default function EmailsTable() {
  const [prospects, setProspects] = useState<Prospect[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [skip, setSkip] = useState(0)
  const [total, setTotal] = useState(0)
  const limit = 50
  const [selectedCategory, setSelectedCategory] = useState<string>('all')

  // Available categories
  const availableCategories = [
    'Art Gallery', 'Museum', 'Museums', 'Art Studio', 'Art School', 'Art Fair', 
    'Art Dealer', 'Art Consultant', 'Art Publisher', 'Art Magazine'
  ]

  const loadSentEmails = async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await listProspects(skip, limit, 'sent')
      // Ensure data is always an array
      let prospectsData = Array.isArray(response?.data) ? response.data : []
      
      // Filter by category if selected
      if (selectedCategory !== 'all') {
        prospectsData = prospectsData.filter((p: Prospect) => 
          p.discovery_category === selectedCategory || p.discovery_category?.toLowerCase() === selectedCategory.toLowerCase()
        )
      }
      
      // Sort by category in ascending order
      prospectsData.sort((a: Prospect, b: Prospect) => {
        const catA = a.discovery_category || ''
        const catB = b.discovery_category || ''
        return catA.localeCompare(catB)
      })
      
      setProspects(prospectsData)
      setTotal(selectedCategory === 'all' ? (response?.total ?? 0) : prospectsData.length)
      // Clear error if we successfully got data (even if empty)
      // Empty data is not an error, it's a valid state
    } catch (error: any) {
      console.error('Failed to load sent emails:', error)
      const errorMessage = error?.message || 'Failed to load sent emails. Check if backend is running.'
      setError(errorMessage)
      setProspects([])
      setTotal(0)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadSentEmails()
    const interval = setInterval(loadSentEmails, 15000)
    
    const handleJobCompleted = () => {
      console.log('🔄 Job completed event received, refreshing emails table...')
      loadSentEmails()
    }
    
    if (typeof window !== 'undefined') {
      window.addEventListener('jobsCompleted', handleJobCompleted)
    }
    
    return () => {
      clearInterval(interval)
      if (typeof window !== 'undefined') {
        window.removeEventListener('jobsCompleted', handleJobCompleted)
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [skip, selectedCategory])

  const formatDate = (dateString?: string) => {
    if (!dateString) return 'N/A'
    return new Date(dateString).toLocaleString()
  }

  return (
    <div className="glass rounded-xl shadow-lg border border-white/20 p-3">
      <div className="flex items-center justify-between mb-3">
        <h2 className="text-sm font-bold text-gray-900">Sent Emails</h2>
        <div className="flex items-center space-x-2">
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="px-2 py-1.5 text-xs border border-gray-300 rounded-lg focus:ring-olive-500 focus:border-olive-500 bg-white"
          >
            <option value="all">All Categories</option>
            {availableCategories.map((cat) => (
              <option key={cat} value={cat}>{cat}</option>
            ))}
          </select>
          <button
            onClick={loadSentEmails}
            className="flex items-center space-x-1 px-2 py-1.5 bg-olive-600 text-white rounded-lg hover:bg-olive-700 text-xs font-medium"
          >
            <RefreshCw className="w-3 h-3" />
            <span>{loading ? 'Refreshing...' : 'Refresh'}</span>
          </button>
        </div>
      </div>

      {loading && prospects.length === 0 ? (
        <div className="text-center py-4">
          <div className="inline-block animate-spin rounded-full h-6 w-6 border-2 border-olive-600 border-t-transparent"></div>
          <p className="text-gray-500 mt-2 text-xs">Loading sent emails...</p>
        </div>
      ) : error ? (
        <div className="text-center py-4">
          <p className="text-red-600 mb-2 font-semibold text-xs">Error loading sent emails</p>
          <p className="text-gray-600 text-xs">{error}</p>
          <button
            onClick={loadSentEmails}
            className="mt-3 px-2 py-1.5 bg-olive-600 text-white rounded-lg hover:bg-olive-700 text-xs font-medium"
          >
            Retry
          </button>
        </div>
      ) : prospects.length === 0 && !loading ? (
        <div className="text-center py-4">
          <p className="text-gray-500 mb-2 text-xs">No sent emails found</p>
          <p className="text-gray-400 text-xs">Send emails to prospects from the Leads tab to see them here.</p>
        </div>
      ) : (
        <>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-2 px-3 text-xs font-semibold text-gray-700">Category</th>
                  <th className="text-left py-2 px-3 text-xs font-semibold text-gray-700">Recipient</th>
                  <th className="text-left py-2 px-3 text-xs font-semibold text-gray-700">Subject</th>
                  <th className="text-left py-2 px-3 text-xs font-semibold text-gray-700">Status</th>
                  <th className="text-left py-2 px-3 text-xs font-semibold text-gray-700">Sent At</th>
                  <th className="text-left py-2 px-3 text-xs font-semibold text-gray-700">Follow-ups</th>
                </tr>
              </thead>
              <tbody>
                {prospects.map((prospect) => (
                  <tr key={prospect.id} className="border-b border-gray-100 hover:bg-gray-50">
                    <td className="py-2 px-3">
                      <span className="text-gray-700 text-xs font-medium">{prospect.discovery_category || 'N/A'}</span>
                    </td>
                    <td className="py-2 px-3">
                      <div className="flex items-center space-x-1">
                        <Mail className="w-3 h-3 text-gray-400" />
                        <span className="text-gray-900 text-xs">{prospect.contact_email || 'N/A'}</span>
                      </div>
                    </td>
                    <td className="py-2 px-3">
                      <span className="text-gray-900 text-xs">{prospect.draft_subject || 'No subject'}</span>
                    </td>
                    <td className="py-2 px-3">
                      <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                        prospect.outreach_status === 'replied' ? 'bg-blue-100 text-blue-800' :
                        prospect.outreach_status === 'sent' ? 'bg-green-100 text-green-800' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {prospect.outreach_status}
                      </span>
                    </td>
                    <td className="py-2 px-3 text-xs text-gray-600">
                      {formatDate(prospect.last_sent)}
                    </td>
                    <td className="py-2 px-3">
                      <span className="text-gray-900 text-xs">{prospect.followups_sent || 0}</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="flex items-center justify-between mt-3">
            <p className="text-xs text-gray-600">
              Showing {skip + 1}-{Math.min(skip + limit, total)} of {total}
            </p>
            <div className="flex space-x-2">
              <button
                onClick={() => setSkip(Math.max(0, skip - limit))}
                disabled={skip === 0}
                className="px-2 py-1.5 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 disabled:opacity-50 text-xs font-medium"
              >
                Previous
              </button>
              <button
                onClick={() => setSkip(skip + limit)}
                disabled={skip + limit >= total}
                className="px-2 py-1.5 bg-olive-600 text-white rounded-lg hover:bg-olive-700 disabled:opacity-50 text-xs font-medium"
              >
                Next
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  )
}

