import { useState } from 'react'
import { Settings, DollarSign, GraduationCap, FileText } from 'lucide-react'
import SettingsPage from './SettingsPage'
import ApiCostsPage from './ApiCostsPage'
import LearningPage from './LearningPage'
import ReleaseNotesPage from './ReleaseNotesPage'

const tabs = [
  { id: 'settings', label: 'Settings', icon: Settings },
  { id: 'costs', label: 'API Costs', icon: DollarSign },
  { id: 'learning', label: 'Learning', icon: GraduationCap },
  { id: 'releases', label: 'Release Notes', icon: FileText },
]

export default function MorePage() {
  const [activeTab, setActiveTab] = useState('settings')

  return (
    <div className="space-y-6">
      {/* Tab bar */}
      <div className="flex gap-1 p-1 rounded-xl bg-surface-tertiary">
        {tabs.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            onClick={() => setActiveTab(id)}
            className={`flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium transition-colors flex-1 justify-center ${
              activeTab === id
                ? 'bg-surface-secondary text-primary shadow-sm'
                : 'text-muted hover:text-primary'
            }`}
          >
            <Icon className="w-4 h-4" />
            {label}
          </button>
        ))}
      </div>

      {/* Tab content */}
      {activeTab === 'settings' && <SettingsPage />}
      {activeTab === 'costs' && <ApiCostsPage />}
      {activeTab === 'learning' && <LearningPage />}
      {activeTab === 'releases' && <ReleaseNotesPage />}
    </div>
  )
}
