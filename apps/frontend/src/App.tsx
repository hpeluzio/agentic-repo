import { useState } from 'react'
import './App.css'

function App() {
  const [question, setQuestion] = useState('')
  const [response, setResponse] = useState('')
  const [loading, setLoading] = useState(false)
  const [status, setStatus] = useState('')

  const handleQuery = async () => {
    if (!question.trim()) return

    setLoading(true)
    try {
      const res = await fetch('http://localhost:3000/agent/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question }),
      })

      const data = await res.json()
      if (data.success) {
        setResponse(data.response)
      } else {
        setResponse('Error: ' + data.message)
      }
    } catch {
      setResponse('Error connecting to backend')
    } finally {
      setLoading(false)
    }
  }

  const checkStatus = async () => {
    try {
      const res = await fetch('http://localhost:3000/agent/status')
      const data = await res.json()
      setStatus(`Status: ${data.status} (${data.timestamp})`)
    } catch {
      setStatus('Error checking status')
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">
            🤖 AI Agentic System
          </h1>
          <p className="text-gray-600">
            Query your documents with AI-powered insights
          </p>
        </div>

        {/* Status Check */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold text-gray-700">System Status</h2>
            <button
              onClick={checkStatus}
              className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
            >
              Check Status
            </button>
          </div>
          {status && (
            <p className="mt-2 text-sm text-gray-600">{status}</p>
          )}
        </div>

        {/* Query Interface */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold text-gray-700 mb-4">
            Ask a Question
          </h2>
          
          <div className="space-y-4">
            <div>
              <label htmlFor="question" className="block text-sm font-medium text-gray-700 mb-2">
                Your Question
              </label>
              <textarea
                id="question"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder="Ask anything about your documents..."
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                rows={4}
              />
            </div>

            <button
              onClick={handleQuery}
              disabled={loading || !question.trim()}
              className="w-full px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? '🤔 Thinking...' : '🚀 Ask Question'}
            </button>
          </div>

          {/* Response */}
          {response && (
            <div className="mt-6">
              <h3 className="text-lg font-semibold text-gray-700 mb-2">
                Response
              </h3>
              <div className="bg-gray-50 rounded-lg p-4 border-l-4 border-indigo-500">
                <p className="text-gray-800 whitespace-pre-wrap">{response}</p>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="text-center mt-8 text-gray-500 text-sm">
          <p>Powered by NestJS + React + LlamaIndex + ChromaDB</p>
        </div>
      </div>
    </div>
  )
}

export default App
