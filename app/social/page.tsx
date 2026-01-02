'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import SocialProfilesTable from '@/components/SocialProfilesTable'
import SocialDiscovery from '@/components/SocialDiscovery'
import { MessageSquare, Search, Send, RefreshCw } from 'lucide-react'

export default function SocialPage() {
  const router = useRouter()
  const [activeView, setActiveView] = useState<'discover' | 'profiles' | 'drafts' | 'sent'>('discover')

  useEffect(() => {
    const token = typeof window !== 'undefined' ? localStorage.getItem('auth_token') : null
    if (!token) {
      router.push('/login')
      return
    }
  }, [router])

  return (
    <div className="min-h-screen bg-gradient-to-br from-olive-50 to-white">
      <div className="container mx-auto px-4 py-6">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Social Media Outreach</h1>
          <p className="text-sm text-gray-600">Discover and engage with social media profiles</p>
        </div>

        {/* Navigation Tabs */}
        <div className="flex space-x-2 mb-6 border-b border-gray-200">
          <button
            onClick={() => setActiveView('discover')}
            className={`px-4 py-2 text-xs font-medium border-b-2 transition-colors ${
              activeView === 'discover'
                ? 'border-olive-600 text-olive-600'
                : 'border-transparent text-gray-600 hover:text-gray-900'
            }`}
          >
            <Search className="w-4 h-4 inline mr-1" />
            Discover
          </button>
          <button
            onClick={() => setActiveView('profiles')}
            className={`px-4 py-2 text-xs font-medium border-b-2 transition-colors ${
              activeView === 'profiles'
                ? 'border-olive-600 text-olive-600'
                : 'border-transparent text-gray-600 hover:text-gray-900'
            }`}
          >
            <MessageSquare className="w-4 h-4 inline mr-1" />
            Profiles
          </button>
          <button
            onClick={() => setActiveView('drafts')}
            className={`px-4 py-2 text-xs font-medium border-b-2 transition-colors ${
              activeView === 'drafts'
                ? 'border-olive-600 text-olive-600'
                : 'border-transparent text-gray-600 hover:text-gray-900'
            }`}
          >
            <RefreshCw className="w-4 h-4 inline mr-1" />
            Drafts
          </button>
          <button
            onClick={() => setActiveView('sent')}
            className={`px-4 py-2 text-xs font-medium border-b-2 transition-colors ${
              activeView === 'sent'
                ? 'border-olive-600 text-olive-600'
                : 'border-transparent text-gray-600 hover:text-gray-900'
            }`}
          >
            <Send className="w-4 h-4 inline mr-1" />
            Sent
          </button>
        </div>

        {/* Content */}
        <div>
          {activeView === 'discover' && <SocialDiscovery />}
          {activeView === 'profiles' && <SocialProfilesTable />}
          {activeView === 'drafts' && (
            <div className="bg-white rounded-lg shadow p-6">
              <p className="text-sm text-gray-600">Drafts view coming soon</p>
            </div>
          )}
          {activeView === 'sent' && (
            <div className="bg-white rounded-lg shadow p-6">
              <p className="text-sm text-gray-600">Sent messages view coming soon</p>
            </div>
          )}
        </div>
        
        {/* Debug Info - Remove in production */}
        {process.env.NODE_ENV === 'development' && (
          <div className="mt-4 p-3 bg-gray-50 rounded-lg text-xs text-gray-600">
            <p>Active View: {activeView}</p>
            <p>Component: {activeView === 'discover' ? 'SocialDiscovery' : activeView === 'profiles' ? 'SocialProfilesTable' : 'Placeholder'}</p>
          </div>
        )}
      </div>
    </div>
  )
}

