'use client'

import { useState } from 'react'
import { Search, Loader2, CheckCircle2, AlertCircle, ExternalLink } from 'lucide-react'
import { scrapeUrl } from '@/lib/api'

interface ScrapeFormProps {
  onScrape?: () => void
}

export default function ScrapeForm({ onScrape }: ScrapeFormProps) {
  const [url, setUrl] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!url.trim()) return

    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const data = await scrapeUrl(url)
      setResult(data)
      setUrl('')
      if (onScrape) {
        onScrape()
      }
    } catch (err: any) {
      setError(err.message || 'Failed to scrape website')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="bg-white/80 backdrop-blur-sm rounded-lg shadow-md border border-gray-200/50 p-3">
      <div className="flex items-center space-x-1.5 mb-2">
        <div className="p-1.5 bg-olive-600 rounded-md">
          <Search className="w-3.5 h-3.5 text-white" />
        </div>
        <h2 className="text-sm font-bold text-gray-900">Scrape Website</h2>
      </div>

      <form onSubmit={handleSubmit} className="space-y-2">
        <div>
          <label htmlFor="url" className="block text-xs font-medium text-gray-700 mb-1">
            Website URL
          </label>
          <div className="flex space-x-1.5">
            <input
              type="url"
              id="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://example.com"
              className="flex-1 px-3 py-2 border border-gray-300 rounded-md bg-white text-gray-900 placeholder-gray-400 focus:ring-2 focus:ring-olive-500 focus:border-transparent transition-all text-sm"
              disabled={loading}
            />
            <button
              type="submit"
              disabled={loading || !url.trim()}
              className="px-3 py-2 bg-olive-600 text-white rounded-md font-medium hover:bg-olive-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-sm hover:shadow-md flex items-center space-x-1.5 text-sm"
            >
              {loading ? (
                <>
                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                  <span>Scraping...</span>
                </>
              ) : (
                <>
                  <Search className="w-3.5 h-3.5" />
                  <span>Scrape</span>
                </>
              )}
            </button>
          </div>
        </div>
      </form>

      {error && (
        <div className="mt-2 p-2 bg-red-50 border border-red-200 rounded-md flex items-start space-x-2">
          <AlertCircle className="w-3.5 h-3.5 text-red-600 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-xs font-medium text-red-800">Error</p>
            <p className="text-xs text-red-600 mt-0.5">{error}</p>
          </div>
        </div>
      )}

      {result && (
        <div className="mt-2 p-2 bg-green-50 border border-green-200 rounded-md">
          <div className="flex items-start space-x-2">
            <CheckCircle2 className="w-3.5 h-3.5 text-green-600 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <p className="text-xs font-medium text-green-800">Successfully scraped!</p>
              <div className="mt-1.5 space-y-1 text-xs text-green-700">
                <p>
                  <strong>Title:</strong> {result.title || 'N/A'}
                </p>
                {result.extraction_stats && (
                  <div className="mt-2 pt-2 border-t border-green-200">
                    <p className="font-medium mb-1">Extracted:</p>
                    <div className="grid grid-cols-3 gap-2 text-xs">
                      <div>{result.extraction_stats.emails_found || 0} emails</div>
                      <div>{result.extraction_stats.phones_found || 0} phones</div>
                      <div>{result.extraction_stats.social_links_found || 0} social</div>
                    </div>
                  </div>
                )}
                {result.url && (
                  <a
                    href={result.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center space-x-1 text-olive-600 hover:text-olive-800 mt-2"
                  >
                    <span>View website</span>
                    <ExternalLink className="w-3 h-3" />
                  </a>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
