'use client'

import { RefreshCw, ChevronLeft, ChevronRight, CheckCircle, XCircle, Clock } from 'lucide-react'
import { getScraperHistory, type ScraperHistoryItem } from '@/lib/api'
import { usePaginatedFetch } from '@/hooks/usePaginatedFetch'

export default function ScraperHistoryTable() {
  const {
    page,
    data: historyItems,
    totalPages,
    loading,
    refresh,
    goToNext,
    goToPrev,
    canGoNext,
    canGoPrev,
  } = usePaginatedFetch<ScraperHistoryItem>({
    fetchFn: getScraperHistory,
    initialPage: 1,
    limit: 10,
    autoLoad: true,
  })

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString()
  }

  const formatDuration = (seconds: number | null) => {
    if (!seconds) return 'N/A'
    if (seconds < 60) return `${seconds.toFixed(0)}s`
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}m ${secs.toFixed(0)}s`
  }

  return (
    <div className="bg-white/90 backdrop-blur-sm rounded-2xl shadow-lg border-2 border-gray-200/60 p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-bold text-gray-900">Scraper History</h2>
        <button
          onClick={refresh}
          className="flex items-center space-x-2 px-3 py-2 bg-olive-600 text-white rounded-md hover:bg-olive-700"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          <span>{loading ? 'Refreshing...' : 'Refresh'}</span>
        </button>
      </div>

      {loading && historyItems.length === 0 ? (
        <div className="text-center py-8">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-olive-600 border-t-transparent" />
          <p className="text-gray-500 mt-2">Loading history...</p>
        </div>
      ) : historyItems.length === 0 ? (
        <p className="text-gray-500 text-center py-8">No scraper history found</p>
      ) : (
        <>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Triggered</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Completed</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Status</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Success</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Failed</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Duration</th>
                </tr>
              </thead>
              <tbody>
                {historyItems.map((item) => (
                  <tr key={item.id} className="border-b border-gray-100 hover:bg-gray-50">
                    <td className="py-3 px-4 text-sm text-gray-600">
                      {formatDate(item.triggered_at)}
                    </td>
                    <td className="py-3 px-4 text-sm text-gray-600">
                      {item.completed_at ? formatDate(item.completed_at) : 'In progress...'}
                    </td>
                    <td className="py-3 px-4">
                      <span
                        className={`px-2 py-1 rounded text-xs font-medium ${
                          item.status === 'completed'
                            ? 'bg-green-100 text-green-800'
                            : item.status === 'failed'
                            ? 'bg-red-100 text-red-800'
                            : 'bg-yellow-100 text-yellow-800'
                        }`}
                      >
                        {item.status}
                      </span>
                    </td>
                    <td className="py-3 px-4">
                      <div className="flex items-center space-x-1">
                        <CheckCircle className="w-4 h-4 text-green-600" />
                        <span className="text-gray-900">{item.success_count}</span>
                      </div>
                    </td>
                    <td className="py-3 px-4">
                      <div className="flex items-center space-x-1">
                        <XCircle className="w-4 h-4 text-red-600" />
                        <span className="text-gray-900">{item.failed_count}</span>
                      </div>
                    </td>
                    <td className="py-3 px-4 text-sm text-gray-600">
                      <div className="flex items-center space-x-1">
                        <Clock className="w-4 h-4 text-gray-400" />
                        <span>{formatDuration(item.duration_seconds)}</span>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="flex items-center justify-between mt-4">
            <p className="text-sm text-gray-600">
              Page {page} of {totalPages || 1} ({historyItems.length} items)
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




