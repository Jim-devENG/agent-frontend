'use client'

import { useState } from 'react'
import { Search, Loader2 } from 'lucide-react'
import { discoverSocialProfiles } from '@/lib/api'

export default function SocialDiscovery() {
  const [platform, setPlatform] = useState<'linkedin' | 'instagram' | 'tiktok'>('linkedin')
  const [keywords, setKeywords] = useState('')
  const [location, setLocation] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)

  const handleDiscover = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setSuccess(null)
    setLoading(true)

    try {
      const result = await discoverSocialProfiles({
        platform,
        filters: {
          keywords: keywords.split(',').map(k => k.trim()).filter(k => k),
          location: location || undefined,
        },
        max_results: 100,
      })
      setSuccess(`Discovery job started! Job ID: ${result.job_id}`)
      setKeywords('')
      setLocation('')
    } catch (err: any) {
      setError(err.message || 'Failed to start discovery')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="bg-white rounded-lg shadow p-4">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">Discover Social Profiles</h2>
      
      <form onSubmit={handleDiscover} className="space-y-4">
        {/* Platform Selection */}
        <div>
          <label className="block text-xs font-medium text-gray-700 mb-1">Platform</label>
          <select
            value={platform}
            onChange={(e) => setPlatform(e.target.value as any)}
            className="w-full px-3 py-2 text-xs border border-gray-300 rounded-lg focus:ring-olive-500 focus:border-olive-500"
          >
            <option value="linkedin">LinkedIn</option>
            <option value="instagram">Instagram</option>
            <option value="tiktok">TikTok</option>
          </select>
        </div>

        {/* Keywords */}
        <div>
          <label className="block text-xs font-medium text-gray-700 mb-1">Keywords (comma-separated)</label>
          <input
            type="text"
            value={keywords}
            onChange={(e) => setKeywords(e.target.value)}
            placeholder="art gallery, museum, artist"
            className="w-full px-3 py-2 text-xs border border-gray-300 rounded-lg focus:ring-olive-500 focus:border-olive-500"
          />
        </div>

        {/* Location */}
        <div>
          <label className="block text-xs font-medium text-gray-700 mb-1">Location (optional)</label>
          <input
            type="text"
            value={location}
            onChange={(e) => setLocation(e.target.value)}
            placeholder="New York, NY"
            className="w-full px-3 py-2 text-xs border border-gray-300 rounded-lg focus:ring-olive-500 focus:border-olive-500"
          />
        </div>

        {/* Submit */}
        <button
          type="submit"
          disabled={loading || !keywords.trim()}
          className="w-full px-4 py-2 bg-olive-600 text-white text-xs font-medium rounded-lg hover:bg-olive-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
        >
          {loading ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              Starting Discovery...
            </>
          ) : (
            <>
              <Search className="w-4 h-4" />
              Start Discovery
            </>
          )}
        </button>
      </form>

      {/* Messages */}
      {error && (
        <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg text-xs text-red-700">
          {error}
        </div>
      )}
      {success && (
        <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-lg text-xs text-green-700">
          {success}
        </div>
      )}
    </div>
  )
}

