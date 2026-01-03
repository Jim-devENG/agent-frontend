'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import SocialProfilesTable from '@/components/SocialProfilesTable'
import SocialDiscovery from '@/components/SocialDiscovery'
import SocialPipeline from '@/components/SocialPipeline'
import Sidebar from '@/components/Sidebar'
import { 
  LayoutDashboard, 
  Search, 
  MessageSquare, 
  RefreshCw, 
  Send,
  Users,
  FileText,
  Mail
} from 'lucide-react'

export default function SocialPage() {
  const router = useRouter()
  const [activeTab, setActiveTab] = useState<
    'pipeline' | 'discover' | 'profiles' | 'drafts' | 'sent'
  >('pipeline')

  useEffect(() => {
    const token = typeof window !== 'undefined' ? localStorage.getItem('auth_token') : null
    if (!token) {
      router.push('/login')
      return
    }
  }, [router])

  const socialTabs = [
    { id: 'pipeline', label: 'Pipeline', icon: LayoutDashboard },
    { id: 'discover', label: 'Discover', icon: Search },
    { id: 'profiles', label: 'Profiles', icon: Users },
    { id: 'drafts', label: 'Drafts', icon: FileText },
    { id: 'sent', label: 'Sent', icon: Mail },
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-olive-50 to-white">
      <Sidebar 
        activeTab={activeTab} 
        onTabChange={(tab) => setActiveTab(tab as any)}
        tabs={socialTabs}
      />
      
      <main className="lg:ml-64 p-4 lg:p-6">
        <div className="max-w-7xl mx-auto">
          {/* Content */}
          <div>
            {activeTab === 'pipeline' && <SocialPipeline />}
            {activeTab === 'discover' && <SocialDiscovery />}
            {activeTab === 'profiles' && <SocialProfilesTable />}
            {activeTab === 'drafts' && (
              <div className="glass rounded-xl shadow-lg p-6 border border-olive-200">
                <p className="text-sm text-gray-600">Drafts view coming soon</p>
              </div>
            )}
            {activeTab === 'sent' && (
              <div className="glass rounded-xl shadow-lg p-6 border border-olive-200">
                <p className="text-sm text-gray-600">Sent messages view coming soon</p>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  )
}

