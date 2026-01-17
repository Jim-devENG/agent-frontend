'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { login } from '@/lib/api'
import { Globe, Users } from 'lucide-react'

export default function LoginPage() {
  const router = useRouter()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [outreachType, setOutreachType] = useState<'website' | 'social' | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!outreachType) {
      setError('Please select an outreach type')
      return
    }
    
    setError('')
    setLoading(true)

    try {
      const result = await login(username, password)
      localStorage.setItem('auth_token', result.access_token)
      localStorage.setItem('outreach_type', outreachType)
      
      // Navigate based on outreach type
      if (outreachType === 'social') {
        router.push('/social')
      } else {
        router.push('/')
      }
    } catch (err: any) {
      setError(err.message || 'Login failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 via-blue-50/30 to-purple-50/20 relative overflow-hidden">
      {/* Animated background elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-20 left-20 w-72 h-72 bg-liquid-400/20 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-20 right-20 w-96 h-96 bg-purple-400/20 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }}></div>
      </div>
      
      <div className="glass rounded-3xl shadow-2xl p-10 w-full max-w-2xl border border-white/20 relative z-10 animate-fade-in">
        <div className="text-center mb-8">
          <div className="w-16 h-16 liquid-gradient rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg">
            <span className="text-white text-2xl font-bold">LC</span>
          </div>
          <h1 className="text-3xl font-bold liquid-gradient-text mb-2">Liquid Canvas</h1>
          <p className="text-gray-600 text-sm">Outreach Studio</p>
        </div>

        {/* Outreach Type Selection */}
        {!outreachType && (
          <div className="mb-8">
            <h2 className="text-lg font-semibold text-gray-900 mb-4 text-center">Choose Outreach Type</h2>
            <div className="grid grid-cols-2 gap-4">
              <button
                onClick={() => setOutreachType('website')}
                className="p-6 bg-white rounded-xl border-2 border-gray-200 hover:border-olive-500 hover:shadow-lg transition-all duration-200 text-left group"
              >
                <Globe className="w-8 h-8 text-olive-600 mb-3 group-hover:scale-110 transition-transform" />
                <h3 className="font-semibold text-gray-900 mb-2">Website Outreach</h3>
                <p className="text-xs text-gray-600">Discover websites, scrape emails, and send outreach emails</p>
              </button>
              <button
                onClick={() => setOutreachType('social')}
                className="p-6 bg-white rounded-xl border-2 border-gray-200 hover:border-olive-500 hover:shadow-lg transition-all duration-200 text-left group"
              >
                <Users className="w-8 h-8 text-olive-600 mb-3 group-hover:scale-110 transition-transform" />
                <h3 className="font-semibold text-gray-900 mb-2">Social Outreach</h3>
                <p className="text-xs text-gray-600">Discover social profiles and send messages on LinkedIn, Instagram, TikTok, Facebook</p>
              </button>
            </div>
          </div>
        )}
        
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label htmlFor="username" className="block text-sm font-semibold text-gray-700 mb-2">
              Username
            </label>
            <input
              id="username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              className="w-full px-4 py-3 glass border border-gray-200/50 rounded-xl focus:outline-none focus:ring-2 focus:ring-liquid-500 focus:border-liquid-500 transition-all duration-200"
              placeholder="Enter your username"
            />
          </div>
          <div>
            <label htmlFor="password" className="block text-sm font-semibold text-gray-700 mb-2">
              Password
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="w-full px-4 py-3 glass border border-gray-200/50 rounded-xl focus:outline-none focus:ring-2 focus:ring-liquid-500 focus:border-liquid-500 transition-all duration-200"
              placeholder="Enter your password"
            />
          </div>
          {error && (
            <div className="p-3 bg-gradient-to-r from-red-50 to-pink-50 border-2 border-red-300 rounded-xl text-red-700 text-sm font-medium animate-slide-up">
              {error}
            </div>
          )}
          {outreachType && (
            <div className="p-3 bg-olive-50 rounded-lg border border-olive-200">
              <p className="text-xs text-gray-700 text-center">
                Selected: <span className="font-semibold text-olive-700">{outreachType === 'social' ? 'Social Outreach' : 'Website Outreach'}</span>
                <button
                  type="button"
                  onClick={() => setOutreachType(null)}
                  className="ml-2 text-olive-600 hover:text-olive-800 underline"
                >
                  Change
                </button>
              </p>
            </div>
          )}

          <button
            type="submit"
            disabled={loading || !outreachType}
            className="w-full liquid-gradient text-white py-3 px-4 rounded-xl hover:shadow-xl hover:scale-105 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed font-semibold shadow-lg"
          >
            {loading ? (
              <span className="flex items-center justify-center space-x-2">
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                <span>Logging in...</span>
              </span>
            ) : (
              'Sign In'
            )}
          </button>
        </form>
        
        <div className="mt-6 text-center">
          <p className="text-xs text-gray-500">
            Powered by <a href="https://liquidcanvas.art" target="_blank" rel="noopener noreferrer" className="liquid-gradient-text font-semibold hover:underline">liquidcanvas.art</a>
          </p>
        </div>
      </div>
    </div>
  )
}

