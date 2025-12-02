'use client'

import { useState, useEffect } from 'react'
import { Power, Zap, MapPin, Tag, Clock, AlertCircle, CheckCircle, Loader2 } from 'lucide-react'
import {
  getScraperStatus,
  setMasterSwitch,
  setAutoSwitch,
  setScraperConfig,
  type ScraperStatus,
} from '@/lib/api'

const LOCATION_OPTIONS = [
  { value: 'usa', label: 'USA' },
  { value: 'canada', label: 'Canada' },
  { value: 'uk_london', label: 'UK / London' },
  { value: 'germany', label: 'Germany' },
  { value: 'france', label: 'France' },
  { value: 'europe', label: 'Europe' },
]

const CATEGORY_OPTIONS = [
  { value: 'home_decor', label: 'Home decor' },
  { value: 'holiday', label: 'Holiday' },
  { value: 'parenting', label: 'Parenting' },
  { value: 'audio_visuals', label: 'Audio visuals' },
  { value: 'gift_guides', label: 'Gift guides' },
  { value: 'tech_innovation', label: 'Tech innovation' },
]

const INTERVAL_OPTIONS = [
  { value: '1h', label: 'Every 1 hour' },
  { value: '2h', label: 'Every 2 hours' },
  { value: '3h', label: 'Every 3 hours' },
  { value: '4h', label: 'Every 4 hours' },
  { value: '5h', label: 'Every 5 hours' },
  { value: 'daily', label: 'Daily' },
  { value: 'weekly', label: 'Weekly' },
]

export default function AutomationControl() {
  const [status, setStatus] = useState<ScraperStatus | null>(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)

  const loadStatus = async () => {
    try {
      setLoading(true)
      const data = await getScraperStatus()
      setStatus(data)
    } catch (err: any) {
      console.error('Error loading scraper status:', err)
      setError(err.message || 'Failed to load status')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadStatus()
    const interval = setInterval(loadStatus, 10000) // Refresh every 10s
    return () => clearInterval(interval)
  }, [])

  const toggleMasterSwitch = async (enabled: boolean) => {
    try {
      setSaving(true)
      setError(null)
      await setMasterSwitch(enabled)
      await loadStatus()
      setSuccess('Master switch updated')
      setTimeout(() => setSuccess(null), 3000)
    } catch (err: any) {
      setError(err.message || 'Failed to update master switch')
    } finally {
      setSaving(false)
    }
  }

  const toggleAutoSwitch = async (enabled: boolean) => {
    if (!status) return
    
    if (enabled && !status.can_enable_auto) {
      setError(`You must select location, category, and interval before enabling automation. Missing: ${status.missing_fields.join(', ')}`)
      return
    }

    try {
      setSaving(true)
      setError(null)
      await setAutoSwitch(enabled)
      await loadStatus()
      setSuccess('Auto scraper updated')
      setTimeout(() => setSuccess(null), 3000)
    } catch (err: any) {
      setError(err.message || 'Failed to update auto switch')
    } finally {
      setSaving(false)
    }
  }

  const saveConfig = async (locations: string[], categories: string[], interval: string) => {
    try {
      setSaving(true)
      setError(null)
      await setScraperConfig(locations, categories, interval)
      await loadStatus()
      setSuccess('Configuration saved')
      setTimeout(() => setSuccess(null), 3000)
    } catch (err: any) {
      setError(err.message || 'Failed to save configuration')
    } finally {
      setSaving(false)
    }
  }

  const formatNextRun = (nextRunAt: string | null) => {
    if (!nextRunAt) return 'Not scheduled'
    try {
      const date = new Date(nextRunAt)
      const now = new Date()
      const diffMs = date.getTime() - now.getTime()
      const diffMins = Math.floor(diffMs / 60000)
      
      if (diffMins < 0) return 'Overdue'
      if (diffMins < 60) return `In ${diffMins} minutes`
      const diffHours = Math.floor(diffMins / 60)
      if (diffHours < 24) return `In ${diffHours} hours`
      const diffDays = Math.floor(diffHours / 24)
      return `In ${diffDays} days`
    } catch {
      return 'Invalid date'
    }
  }

  if (loading && !status) {
    return (
      <div className="bg-white/90 backdrop-blur-sm rounded-2xl shadow-lg border-2 border-gray-200/60 p-6">
        <div className="flex items-center justify-center py-8">
          <Loader2 className="w-6 h-6 animate-spin text-olive-600" />
          <span className="ml-2 text-gray-600">Loading automation settings...</span>
        </div>
      </div>
    )
  }

  if (!status) {
    return (
      <div className="bg-white/90 backdrop-blur-sm rounded-2xl shadow-lg border-2 border-gray-200/60 p-6">
        <p className="text-red-600">Failed to load automation settings</p>
      </div>
    )
  }

  return (
    <div className="bg-white/90 backdrop-blur-sm rounded-2xl shadow-lg border-2 border-gray-200/60 p-6">
      <h2 className="text-lg font-bold text-gray-900 mb-4">Automation Control</h2>

      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg flex items-center">
          <AlertCircle className="w-4 h-4 text-red-600 mr-2" />
          <p className="text-sm text-red-800">{error}</p>
        </div>
      )}

      {success && (
        <div className="mb-4 p-3 bg-green-50 border border-green-200 rounded-lg flex items-center">
          <CheckCircle className="w-4 h-4 text-green-600 mr-2" />
          <p className="text-sm text-green-800">{success}</p>
        </div>
      )}

      <div className="space-y-4">
        {/* Master Switch */}
        <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
          <div className="flex items-center space-x-3">
            <Power className="w-5 h-5 text-gray-600" />
            <div>
              <p className="font-semibold text-gray-900">Master Switch</p>
              <p className="text-sm text-gray-600">Enable/disable all scraping operations</p>
            </div>
          </div>
          <label className="relative inline-flex items-center cursor-pointer">
            <input
              type="checkbox"
              checked={status.master_enabled}
              onChange={(e) => toggleMasterSwitch(e.target.checked)}
              disabled={saving}
              className="sr-only peer"
            />
            <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-olive-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-olive-600"></div>
          </label>
        </div>

        {/* Auto Switch */}
        <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
          <div className="flex items-center space-x-3">
            <Zap className="w-5 h-5 text-gray-600" />
            <div>
              <p className="font-semibold text-gray-900">Automatic Scraper</p>
              <p className="text-sm text-gray-600">
                {status.can_enable_auto
                  ? 'Run automation jobs automatically'
                  : `Missing: ${status.missing_fields.join(', ')}`}
              </p>
            </div>
          </div>
          <label className="relative inline-flex items-center cursor-pointer">
            <input
              type="checkbox"
              checked={status.auto_enabled && status.master_enabled}
              disabled={!status.master_enabled || !status.can_enable_auto || saving}
              onChange={(e) => toggleAutoSwitch(e.target.checked)}
              className="sr-only peer"
            />
            <div className={`w-11 h-6 rounded-full peer ${
              status.master_enabled && status.can_enable_auto
                ? 'bg-gray-200 peer-checked:bg-olive-600'
                : 'bg-gray-100 cursor-not-allowed'
            }`}></div>
          </label>
        </div>

        {/* Configuration */}
        {status.master_enabled && (
          <div className="space-y-4 p-4 bg-gray-50 rounded-lg">
            <h3 className="font-semibold text-gray-900">Configuration</h3>

            {/* Locations */}
            <div>
              <label className="flex items-center space-x-2 text-sm font-semibold text-gray-700 mb-2">
                <MapPin className="w-4 h-4" />
                <span>Locations (Required)</span>
              </label>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                {LOCATION_OPTIONS.map((loc) => {
                  const isSelected = status.locations.includes(loc.value)
                  return (
                    <button
                      key={loc.value}
                      type="button"
                      onClick={() => {
                        const newLocations = isSelected
                          ? status.locations.filter((l) => l !== loc.value)
                          : [...status.locations, loc.value]
                        saveConfig(newLocations, status.categories, status.interval)
                      }}
                      disabled={saving}
                      className={`px-3 py-2 rounded-lg text-sm font-medium transition-all ${
                        isSelected
                          ? 'bg-blue-600 text-white shadow-md'
                          : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                      }`}
                    >
                      {loc.label}
                    </button>
                  )
                })}
              </div>
            </div>

            {/* Categories */}
            <div>
              <label className="flex items-center space-x-2 text-sm font-semibold text-gray-700 mb-2">
                <Tag className="w-4 h-4" />
                <span>Categories (Required)</span>
              </label>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                {CATEGORY_OPTIONS.map((cat) => {
                  const isSelected = status.categories.includes(cat.value)
                  return (
                    <button
                      key={cat.value}
                      type="button"
                      onClick={() => {
                        const newCategories = isSelected
                          ? status.categories.filter((c) => c !== cat.value)
                          : [...status.categories, cat.value]
                        saveConfig(status.locations, newCategories, status.interval)
                      }}
                      disabled={saving}
                      className={`px-3 py-2 rounded-lg text-sm font-medium transition-all ${
                        isSelected
                          ? 'bg-olive-600 text-white shadow-md'
                          : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                      }`}
                    >
                      {cat.label}
                    </button>
                  )
                })}
              </div>
            </div>

            {/* Interval */}
            <div>
              <label className="flex items-center space-x-2 text-sm font-semibold text-gray-700 mb-2">
                <Clock className="w-4 h-4" />
                <span>Interval (Required)</span>
              </label>
              <select
                value={status.interval || '1h'}
                onChange={(e) => saveConfig(status.locations, status.categories, e.target.value)}
                disabled={saving}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-olive-500"
              >
                {INTERVAL_OPTIONS.map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {opt.label}
                  </option>
                ))}
              </select>
            </div>
          </div>
        )}

        {/* Status */}
        <div className="p-4 bg-gray-50 rounded-lg">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-semibold text-gray-700">Status</p>
              <p className="text-xs text-gray-600 mt-1">
                {status.status === 'running' && '🟢 Running'}
                {status.status === 'idle' && '🟡 Idle'}
                {status.status === 'disabled' && '🔴 Disabled'}
              </p>
            </div>
            <div className="text-right">
              <p className="text-sm font-semibold text-gray-700">Next Run</p>
              <p className="text-xs text-gray-600 mt-1">
                {formatNextRun(status.next_run_at)}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
