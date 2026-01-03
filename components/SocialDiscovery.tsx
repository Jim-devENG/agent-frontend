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
    <div className="glass rounded-xl shadow-lg border border-olive-200 p-4">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-bold text-olive-700">Social Profile Discovery</h3>
      </div>
      
      <form onSubmit={handleDiscover} className="space-y-3">
        {/* Platform Selection */}
        <div>
          <label className="block text-xs font-medium text-gray-700 mb-1">Platform (Required) *</label>
          <select
            value={platform}
            onChange={(e) => setPlatform(e.target.value as any)}
            className="w-full px-2 py-1.5 text-xs border border-olive-200 rounded-lg focus:ring-olive-500 focus:border-olive-500"
          >
            <option value="linkedin">LinkedIn</option>
            <option value="instagram">Instagram</option>
            <option value="tiktok">TikTok</option>
            <option value="facebook">Facebook</option>
          </select>
        </div>

        {/* Categories */}
        <div>
          <label className="block text-xs font-medium text-gray-700 mb-1">
            Categories (Required) *
          </label>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-1.5">
            {availableCategories.map(cat => (
              <label key={cat} className="flex items-center space-x-1.5 p-1.5 border border-olive-200 rounded hover:bg-olive-50 cursor-pointer">
                <input
                  type="checkbox"
                  checked={categories.includes(cat)}
                  onChange={() => handleCategoryToggle(cat)}
                  className="accent-olive-600"
                />
                <span className="text-xs">{cat}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Locations */}
        <div>
          <label className="block text-xs font-medium text-gray-700 mb-1">
            Locations (Required) *
          </label>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-1.5">
            {availableLocations.map(loc => (
              <label key={loc} className="flex items-center space-x-1.5 p-1.5 border border-olive-200 rounded hover:bg-olive-50 cursor-pointer">
                <input
                  type="checkbox"
                  checked={locations.includes(loc)}
                  onChange={() => handleLocationToggle(loc)}
                  className="accent-olive-600"
                />
                <span className="text-xs">{loc}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Keywords */}
        <div>
          <label className="block text-xs font-medium text-gray-700 mb-1">
            Keywords (Optional)
          </label>
          <input
            type="text"
            value={keywords}
            onChange={(e) => setKeywords(e.target.value)}
            placeholder="e.g., contemporary art, abstract painting"
            className="w-full px-2 py-1.5 text-xs border border-olive-200 rounded-lg focus:ring-olive-500 focus:border-olive-500"
          />
        </div>

        {error && (
          <div className="p-2 bg-red-50 border border-red-200 rounded text-red-700 text-xs">
            {error}
          </div>
        )}

        {success && (
          <div className="p-2 bg-olive-50 border border-olive-200 rounded text-olive-700 text-xs">
            ✅ {success}
          </div>
        )}

        <button
          onClick={handleDiscover}
          disabled={loading || categories.length === 0 || locations.length === 0}
          className="w-full px-3 py-2 bg-olive-600 text-white rounded-lg hover:bg-olive-700 hover:shadow-md disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2 text-xs font-semibold"
        >
          {loading ? (
            <>
              <Loader2 className="w-3 h-3 animate-spin" />
              <span>Starting Discovery...</span>
            </>
          ) : (
            <>
              <Search className="w-3 h-3" />
              <span>Discover Profiles</span>
            </>
          )}
        </button>
      </form>
    </div>
  )
}

