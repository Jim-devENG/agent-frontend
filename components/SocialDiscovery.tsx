'use client'

import { useState } from 'react'
import { Search, Loader2 } from 'lucide-react'
import { discoverSocialProfilesPipeline } from '@/lib/api'

export default function SocialDiscovery() {
  const [platform, setPlatform] = useState<'linkedin' | 'instagram' | 'tiktok' | 'facebook'>('linkedin')
  const [categories, setCategories] = useState<string[]>([])
  const [locations, setLocations] = useState<string[]>([])
  const [keywords, setKeywords] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)

  const availableCategories = [
    'Art Gallery', 'Museums', 'Art Studio', 'Art School', 'Art Fair', 
    'Art Dealer', 'Art Consultant', 'Art Publisher', 'Art Magazine'
  ]

  const availableLocations = [
    'United States', 'United Kingdom', 'Canada', 'Australia', 'Germany',
    'Spain', 'Netherlands', 'Belgium', 'France', 'Italy'
  ]

  const handleCategoryToggle = (category: string) => {
    if (categories.includes(category)) {
      setCategories(categories.filter(c => c !== category))
    } else {
      setCategories([...categories, category])
    }
  }

  const handleLocationToggle = (location: string) => {
    if (locations.includes(location)) {
      setLocations(locations.filter(l => l !== location))
    } else {
      setLocations([...locations, location])
    }
  }

  const handleDiscover = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (categories.length === 0) {
      setError('Please select at least one category')
      return
    }
    if (locations.length === 0) {
      setError('Please select at least one location')
      return
    }

    setError(null)
    setSuccess(null)
    setLoading(true)

    try {
      const result = await discoverSocialProfilesPipeline({
        platform,
        categories,
        locations,
        keywords: keywords.split(',').map(k => k.trim()).filter(k => k),
        max_results: 100,
      })
      setSuccess(`Discovery job started! Job ID: ${result.job_id}`)
      setKeywords('')
      setCategories([])
      setLocations([])
      
      // Refresh pipeline status
      if (typeof window !== 'undefined') {
        window.dispatchEvent(new CustomEvent('refreshSocialPipelineStatus'))
      }
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
          <label className="block text-xs font-medium text-gray-700 mb-1">Platform *</label>
          <select
            value={platform}
            onChange={(e) => setPlatform(e.target.value as any)}
            className="w-full px-3 py-2 text-xs border border-gray-300 rounded-lg focus:ring-olive-500 focus:border-olive-500"
          >
            <option value="linkedin">LinkedIn</option>
            <option value="instagram">Instagram</option>
            <option value="tiktok">TikTok</option>
            <option value="facebook">Facebook</option>
          </select>
        </div>

        {/* Categories */}
        <div>
          <label className="block text-xs font-medium text-gray-700 mb-1">Categories *</label>
          <div className="flex flex-wrap gap-2">
            {availableCategories.map((cat) => (
              <button
                key={cat}
                type="button"
                onClick={() => handleCategoryToggle(cat)}
                className={`px-3 py-1 text-xs rounded-lg border transition-colors ${
                  categories.includes(cat)
                    ? 'bg-olive-600 text-white border-olive-600'
                    : 'bg-white text-gray-700 border-gray-300 hover:border-olive-500'
                }`}
              >
                {cat}
              </button>
            ))}
          </div>
          {categories.length === 0 && (
            <p className="text-xs text-gray-500 mt-1">Select at least one category</p>
          )}
        </div>

        {/* Locations */}
        <div>
          <label className="block text-xs font-medium text-gray-700 mb-1">Locations *</label>
          <div className="flex flex-wrap gap-2">
            {availableLocations.map((loc) => (
              <button
                key={loc}
                type="button"
                onClick={() => handleLocationToggle(loc)}
                className={`px-3 py-1 text-xs rounded-lg border transition-colors ${
                  locations.includes(loc)
                    ? 'bg-olive-600 text-white border-olive-600'
                    : 'bg-white text-gray-700 border-gray-300 hover:border-olive-500'
                }`}
              >
                {loc}
              </button>
            ))}
          </div>
          {locations.length === 0 && (
            <p className="text-xs text-gray-500 mt-1">Select at least one location</p>
          )}
        </div>

        {/* Keywords */}
        <div>
          <label className="block text-xs font-medium text-gray-700 mb-1">Keywords (optional, comma-separated)</label>
          <input
            type="text"
            value={keywords}
            onChange={(e) => setKeywords(e.target.value)}
            placeholder="art gallery, museum, artist"
            className="w-full px-3 py-2 text-xs border border-gray-300 rounded-lg focus:ring-olive-500 focus:border-olive-500"
          />
        </div>

        {/* Submit */}
        <button
          type="submit"
          disabled={loading || categories.length === 0 || locations.length === 0}
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

