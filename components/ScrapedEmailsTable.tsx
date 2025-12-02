'use client'

import { Mail, Globe, User, ShieldCheck, RefreshCw, ChevronLeft, ChevronRight } from 'lucide-react'
import type { EnrichmentResult } from '@/lib/types'
import { safeToFixed } from '@/lib/safe-utils'
import { usePaginatedFetch } from '@/hooks/usePaginatedFetch'
import { listProspects, type Prospect } from '@/lib/api'

export default function ScrapedEmailsTable() {
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
    fetchFn: async (page, limit) => {
      return listProspects(page, limit, undefined, undefined, true)
    },
    initialPage: 1,
    limit: 10,
    autoLoad: true,
  })

  // Convert prospects to EnrichmentResult format
  const rows: EnrichmentResult[] = prospects.map((p) => ({
    email: p.contact_email || null,
    name: null, // Prospects don't have name field
    company: null,
    confidence: p.hunter_payload ? (typeof p.hunter_payload === 'object' && 'confidence' in p.hunter_payload ? Number(p.hunter_payload.confidence) : null) : null,
    domain: p.domain,
    success: !!p.contact_email,
    source: p.hunter_payload ? (typeof p.hunter_payload === 'object' && 'source' in p.hunter_payload ? String(p.hunter_payload.source) : 'hunter_io') : null,
    error: null,
  }))

  return (
    <div className="bg-white/90 backdrop-blur-sm rounded-2xl shadow-lg border-2 border-gray-200/60 p-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <ShieldCheck className="w-5 h-5 text-olive-600" />
          <div>
            <h2 className="text-lg font-bold text-gray-900">Scraped Emails</h2>
            <p className="text-xs text-gray-500">
              Live stream of enriched emails discovered by the pipeline
            </p>
          </div>
        </div>
        <button
          onClick={refresh}
          className="flex items-center space-x-2 px-3 py-2 bg-olive-600 text-white rounded-md hover:bg-olive-700 text-sm"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          <span>{loading ? 'Refreshing...' : 'Refresh'}</span>
        </button>
      </div>

      {loading && rows.length === 0 ? (
        <div className="text-center py-8">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-olive-600 border-t-transparent" />
          <p className="text-gray-500 mt-2 text-sm">Loading scraped emails...</p>
        </div>
      ) : rows.length === 0 ? (
        <p className="text-gray-500 text-center py-8 text-sm">
          No scraped emails yet. Start a discovery + enrichment job to see emails here.
        </p>
      ) : (
        <>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-3 px-4 text-xs font-semibold text-gray-700 uppercase tracking-wide">
                    Name
                  </th>
                  <th className="text-left py-3 px-4 text-xs font-semibold text-gray-700 uppercase tracking-wide">
                    Email
                  </th>
                  <th className="text-left py-3 px-4 text-xs font-semibold text-gray-700 uppercase tracking-wide">
                    Domain
                  </th>
                  <th className="text-left py-3 px-4 text-xs font-semibold text-gray-700 uppercase tracking-wide">
                    Confidence
                  </th>
                </tr>
              </thead>
              <tbody>
                {rows.map((item, idx) => (
                  <tr
                    key={`${item.domain}-${item.email || 'none'}-${idx}`}
                    className="border-b border-gray-100 hover:bg-gray-50"
                  >
                    <td className="py-3 px-4">
                      <div className="flex items-center space-x-2">
                        <User className="w-4 h-4 text-gray-400" />
                        <span className="text-gray-900 text-sm">
                          {item.name || 'Unknown'}
                        </span>
                      </div>
                    </td>
                    <td className="py-3 px-4">
                      {item.email ? (
                        <div className="flex items-center space-x-2">
                          <Mail className="w-4 h-4 text-gray-400" />
                          <span className="text-gray-900 text-sm">{item.email}</span>
                        </div>
                      ) : (
                        <span className="text-gray-400 text-sm">No email</span>
                      )}
                    </td>
                    <td className="py-3 px-4">
                      <div className="flex items-center space-x-2">
                        <Globe className="w-4 h-4 text-gray-400" />
                        <span className="text-gray-900 text-sm">{item.domain}</span>
                      </div>
                    </td>
                    <td className="py-3 px-4">
                      {item.confidence != null ? (
                        <span className="text-gray-900 text-sm">
                          {safeToFixed(item.confidence, 0)}%
                        </span>
                      ) : (
                        <span className="text-gray-400 text-sm">N/A</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="flex items-center justify-between mt-4">
            <p className="text-sm text-gray-600">
              Page {page} of {totalPages || 1} ({rows.length} items)
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


