import React, { useState, useEffect } from 'react'
import axios from 'axios'

const API_BASE = '/api'

function App() {
  const [candidates, setCandidates] = useState([])
  const [loading, setLoading] = useState(false)
  const [signalFusionLoading, setSignalFusionLoading] = useState(false)
  const [stats, setStats] = useState({ total: 0, avgScore: 0 })

  useEffect(() => {
    loadCandidates()
  }, [])

  const loadCandidates = async () => {
    setLoading(true)
    try {
      const response = await axios.get(`${API_BASE}/candidates?min_score=70`)
      setCandidates(response.data)
      calculateStats(response.data)
    } catch (error) {
      console.error('Error loading candidates:', error)
    } finally {
      setLoading(false)
    }
  }

  const calculateStats = (candidates) => {
    const total = candidates.length
    const avgScore = total > 0
      ? candidates.reduce((sum, c) => sum + c.openness_score, 0) / total
      : 0
    setStats({ total, avgScore: avgScore.toFixed(1) })
  }

  const runSignalFusion = async () => {
    setSignalFusionLoading(true)
    try {
      const response = await axios.post(`${API_BASE}/signal-fusion/run`, {
        industry: 'fintech',
        role_level: 'VP',
        min_score: 70,
        limit: 50
      })
      alert(`Found ${response.data.count} candidates!`)
      loadCandidates()
    } catch (error) {
      console.error('Error running signal fusion:', error)
      alert('Error: ' + (error.response?.data?.detail || error.message))
    } finally {
      setSignalFusionLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">AcquiTalent AI</h1>
              <p className="text-sm text-gray-500">Executive Talent Intelligence Platform</p>
            </div>
            <button
              onClick={runSignalFusion}
              disabled={signalFusionLoading}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
            >
              {signalFusionLoading ? 'Running...' : 'Run Signal Fusion'}
            </button>
          </div>
        </div>
      </header>

      {/* Stats */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-sm font-medium text-gray-500">Total Candidates</h3>
            <p className="text-3xl font-bold text-gray-900 mt-2">{stats.total}</p>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-sm font-medium text-gray-500">Avg Openness Score</h3>
            <p className="text-3xl font-bold text-gray-900 mt-2">{stats.avgScore}</p>
          </div>
        </div>

        {/* Candidates List */}
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">High-Score Candidates (70+)</h2>
          </div>
          {loading ? (
            <div className="p-8 text-center text-gray-500">Loading candidates...</div>
          ) : candidates.length === 0 ? (
            <div className="p-8 text-center text-gray-500">
              No candidates found. Run Signal Fusion to find candidates.
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Name
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Title
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Company
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Openness Score
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {candidates.map((candidate) => (
                    <tr key={candidate.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">
                          {candidate.first_name} {candidate.last_name}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">{candidate.current_title || 'N/A'}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">{candidate.current_company || 'N/A'}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div className="text-sm font-semibold text-gray-900">
                            {candidate.openness_score.toFixed(1)}
                          </div>
                          <div className="ml-2 w-24 bg-gray-200 rounded-full h-2">
                            <div
                              className="bg-blue-600 h-2 rounded-full"
                              style={{ width: `${candidate.openness_score}%` }}
                            ></div>
                          </div>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default App

