'use client'

import { useState } from 'react'
import { 
  LayoutDashboard, 
  Globe, 
  Users, 
  Mail, 
  Settings, 
  Activity,
  AtSign,
  BookOpen,
  Menu,
  X
} from 'lucide-react'
import { LucideIcon } from 'lucide-react'

interface Tab {
  id: string
  label: string
  icon: LucideIcon
}

interface SidebarProps {
  activeTab: string
  onTabChange: (tab: 'overview' | 'leads' | 'scraped_emails' | 'emails' | 'jobs' | 'websites' | 'settings' | 'guide') => void
  tabs: Tab[]
}

export default function Sidebar({ activeTab, onTabChange, tabs }: SidebarProps) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  return (
    <>
      {/* Mobile Menu Button */}
      <button
        onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
        className="lg:hidden fixed top-4 left-4 z-50 p-2 bg-white rounded-md shadow-md border border-gray-200"
      >
        {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
      </button>

      {/* Mobile Overlay */}
      {mobileMenuOpen && (
        <div
          className="lg:hidden fixed inset-0 bg-black bg-opacity-50 z-40"
          onClick={() => setMobileMenuOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside className={`
        fixed left-0 top-0 h-full w-64 glass border-r border-gray-200/50 shadow-xl z-40 flex flex-col
        transform transition-transform duration-300 ease-in-out
        ${mobileMenuOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
      `}>
      {/* Logo/Header Section */}
      <div className="p-6 border-b border-gray-200/50 bg-gradient-to-br from-white to-gray-50">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-lg liquid-gradient flex items-center justify-center shadow-lg">
            <span className="text-white text-xl font-bold">LC</span>
          </div>
          <div>
            <h1 className="text-xl font-bold liquid-gradient-text">
              Liquid Canvas
            </h1>
            <p className="text-gray-500 text-xs mt-0.5 font-medium">
              Outreach Studio
            </p>
          </div>
        </div>
      </div>

      {/* Navigation Items */}
      <nav className="flex-1 overflow-y-auto py-4 px-3">
        <div className="space-y-1">
          {Array.isArray(tabs) && tabs.map((tab) => {
            const Icon = tab.icon
            const isActive = activeTab === tab.id
            return (
              <button
                key={tab.id}
                onClick={() => {
                  onTabChange(tab.id as 'overview' | 'leads' | 'scraped_emails' | 'emails' | 'jobs' | 'websites' | 'settings' | 'guide')
                  setMobileMenuOpen(false) // Close mobile menu when tab is selected
                }}
                className={`
                  w-full flex items-center space-x-3 px-4 py-3 rounded-xl font-medium text-sm transition-all duration-200
                  ${
                    isActive
                      ? 'liquid-gradient text-white shadow-lg hover-glow transform scale-105'
                      : 'text-gray-700 hover:bg-gradient-to-r hover:from-liquid-50 hover:to-purple-50 hover:text-liquid-600 hover:shadow-md'
                  }
                `}
              >
                <Icon className={`w-5 h-5 transition-colors ${isActive ? 'text-white' : 'text-gray-500 group-hover:text-liquid-600'}`} />
                <span>{tab.label}</span>
              </button>
            )
          })}
        </div>
      </nav>

      {/* Footer Section */}
      <div className="p-4 border-t border-gray-200/50 bg-gradient-to-t from-gray-50/50 to-transparent">
        <div className="text-xs text-center">
          <p className="text-gray-600 font-medium">Powered by</p>
          <a 
            href="https://liquidcanvas.art" 
            target="_blank" 
            rel="noopener noreferrer"
            className="liquid-gradient-text font-bold text-sm mt-1 inline-block hover:scale-105 transition-transform"
          >
            liquidcanvas.art
          </a>
        </div>
      </div>
    </aside>
    </>
  )
}

