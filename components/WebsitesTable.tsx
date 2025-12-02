'use client'

import { ExternalLink, RefreshCw, ChevronLeft, ChevronRight } from 'lucide-react'
import { listWebsites, type Prospect } from '@/lib/api'
import { safeToFixed } from '@/lib/safe-utils'
import { usePaginatedFetch } from '@/hooks/usePaginatedFetch'

export default function WebsitesTable() {
  const {
    page,
    data: prospects,
    totalPages,
    loading,
    refresh,
    goToNext,
    goToPrev,
    canGoNext,
    canGoPrev,
  } = usePaginatedFetch<Prospect>({
    fetchFn: listWebsites,
    initialPage: 1,
    limit: 10,
    autoLoad: true,
  })

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString()
  }

  return (
    <div className="bg-white/90 backdrop-blur-sm rounded-2xl shadow-lg border-2 border-gray-200/60 p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-bold text-gray-900">Discovered Websites</h2>
        <button
          onClick={refresh}
          className="flex items-center space-x-2 px-3 py-2 bg-olive-600 text-white rounded-md hover:bg-olive-700"
        >
          <RefreshCw className="w-4 h-4" />
          <span>{loading ? 'Refreshing...' : 'Refresh'}</span>
        </button>
      </div>

      {loading && prospects.length === 0 ? (
        <div className="text-center py-8">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-olive-600 border-t-transparent"></div>
          <p className="text-gray-500 mt-2">Loading...</p>
        </div>
      ) : prospects.length === 0 ? (
        <p className="text-gray-500 text-center py-8">No websites found</p>
      ) : (
        <>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Domain</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Page Title</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">DA Score</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Score</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Status</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Created</th>
                </tr>
              </thead>
              <tbody>
                {prospects.map((prospect) => (
                  <tr key={prospect.id} className="border-b border-gray-100 hover:bg-gray-50">
                    <td className="py-3 px-4">
                      <div className="flex items-center space-x-2">
                        <span className="font-medium text-gray-900">{prospect.domain}</span>
                        {prospect.page_url && (
                          <a
                            href={prospect.page_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-olive-600 hover:text-olive-700"
                          >
                            <ExternalLink className="w-4 h-4" />
                          </a>
                        )}
                      </div>
                    </td>
                    <td className="py-3 px-4">
                      <span className="text-gray-900">{prospect.page_title || 'N/A'}</span>
                    </td>
                    <td className="py-3 px-4">
                      <span className="text-gray-900">{safeToFixed(prospect.da_est, 1)}</span>
                    </td>
                    <td className="py-3 px-4">
                      <span className="text-gray-900">{safeToFixed(prospect.score, 2)}</span>
                    </td>
                    <td className="py-3 px-4">
                      <span className={`px-2 py-1 rounded text-xs font-medium ${
                        prospect.outreach_status === 'sent' ? 'bg-green-100 text-green-800' :
                        prospect.outreach_status === 'replied' ? 'bg-blue-100 text-blue-800' :
                        prospect.outreach_status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {prospect.outreach_status}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-sm text-gray-600">
                      {formatDate(prospect.created_at)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="flex items-center justify-between mt-4">
            <p className="text-sm text-gray-600">
              Page {page} of {totalPages || 1} ({prospects.length} items)
            </p>
            <div className="flex space-x-2">
              <button
                onClick={goToPrev}
                disabled={!canGoPrev}
                className="flex items-center space-x-1 px-3 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <ChevronLeft className="w-4 h-4" />
                <span>Previous</span>
              </button>
              <button
                onClick={goToNext}
                disabled={!canGoNext}
                className="flex items-center space-x-1 px-3 py-2 bg-olive-600 text-white rounded-md hover:bg-olive-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <span>Next</span>
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  )
}

