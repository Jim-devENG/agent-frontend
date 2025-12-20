'use client'

import { Users, Mail, CheckCircle, Clock, TrendingUp, AlertCircle } from 'lucide-react'
import type { Stats } from '@/lib/api'

interface StatsCardsProps {
  stats: Stats
}

export default function StatsCards({ stats }: StatsCardsProps) {
  const cards = [
    {
      title: 'Total Prospects',
      value: stats.total_prospects,
      icon: Users,
      color: 'bg-blue-500',
      bgColor: 'bg-blue-50',
      textColor: 'text-blue-700',
    },
    {
      title: 'With Email',
      value: stats.prospects_with_email,
      icon: Mail,
      color: 'bg-green-500',
      bgColor: 'bg-green-50',
      textColor: 'text-green-700',
    },
    {
      title: 'Sent',
      value: stats.prospects_sent,
      icon: CheckCircle,
      color: 'bg-purple-500',
      bgColor: 'bg-purple-50',
      textColor: 'text-purple-700',
    },
    {
      title: 'Pending',
      value: stats.prospects_pending,
      icon: Clock,
      color: 'bg-orange-500',
      bgColor: 'bg-orange-50',
      textColor: 'text-orange-700',
    },
    {
      title: 'Replied',
      value: stats.prospects_replied,
      icon: TrendingUp,
      color: 'bg-olive-600',
      bgColor: 'bg-olive-50',
      textColor: 'text-olive-700',
    },
    {
      title: 'Jobs Running',
      value: stats.jobs_running,
      icon: AlertCircle,
      color: 'bg-yellow-500',
      bgColor: 'bg-yellow-50',
      textColor: 'text-yellow-700',
    },
  ]

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {cards.map((card, index) => {
        const Icon = card.icon
        return (
          <div
            key={card.title}
            className="glass rounded-3xl shadow-xl border border-white/20 p-6 hover:shadow-2xl hover:scale-105 transition-all duration-300 animate-slide-up"
            style={{ animationDelay: `${index * 100}ms` }}
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 mb-2">{card.title}</p>
                <p className={`text-3xl font-bold liquid-gradient-text`}>{card.value}</p>
              </div>
              <div className={`p-4 rounded-2xl shadow-lg liquid-gradient`}>
                <Icon className="w-6 h-6 text-white" />
              </div>
            </div>
          </div>
        )
      })}
    </div>
  )
}

