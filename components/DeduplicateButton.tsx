'use client'

import { useState } from 'react'
import { Trash2, Loader2, CheckCircle, XCircle } from 'lucide-react'
import { deduplicateProspects } from '@/lib/api'

export default function DeduplicateButton() {
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<{ success: boolean; message: string } | null>(null)

  const handleDeduplicate = async () => {
    if (!confirm('This will remove duplicate websites, keeping only the best version of each domain. Continue?')) {
      return
    }

    setLoading(true)
    setResult(null)

    try {
      const response = await deduplicateProspects()
      setResult({
        success: response.success,
        message: response.message || `Removed ${response.deleted} duplicate(s), kept ${response.kept} unique domain(s)`
      })
      
      // Auto-refresh after 2 seconds
      setTimeout(() => {
        window.location.reload()
      }, 2000)
    } catch (error: any) {
      setResult({
        success: false,
        message: error.message || 'Failed to remove duplicates'
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="bg-white/90 backdrop-blur-sm rounded-2xl shadow-lg border-2 border-gray-200/60 p-4">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900">Remove Duplicates</h3>
          <p className="text-xs text-gray-500 mt-1">Clean up duplicate websites</p>
        </div>
        <button
          onClick={handleDeduplicate}
          disabled={loading}
          className={`flex items-center space-x-2 px-4 py-2 rounded-lg font-medium transition-all ${
            !loading
              ? 'bg-red-600 text-white hover:bg-red-700 shadow-md hover:shadow-lg'
              : 'bg-gray-300 text-gray-500 cursor-not-allowed'
          }`}
        >
          {loading ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              <span>Cleaning...</span>
            </>
          ) : (
            <>
              <Trash2 className="w-4 h-4" />
              <span>Remove Duplicates</span>
            </>
          )}
        </button>
      </div>
      {result && (
        <div className={`mt-3 p-2 rounded-lg flex items-center space-x-2 ${
          result.success ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'
        }`}>
          {result.success ? (
            <CheckCircle className="w-4 h-4 text-green-600" />
          ) : (
            <XCircle className="w-4 h-4 text-red-600" />
          )}
          <p className={`text-xs ${result.success ? 'text-green-800' : 'text-red-800'}`}>
            {result.message}
          </p>
        </div>
      )}
    </div>
  )
}

