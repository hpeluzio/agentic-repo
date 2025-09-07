import { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [activeTab, setActiveTab] = useState<'database' | 'rag'>('database');

  // User Role State
  const [userRole, setUserRole] = useState<'employee' | 'manager' | 'admin'>(
    'employee',
  );

  // Database Agent Tab State
  const [question, setQuestion] = useState('');
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState('');

  // RAG Tab State
  const [ragQuestion, setRagQuestion] = useState('');
  const [ragResponse, setRagResponse] = useState('');
  const [ragLoading, setRagLoading] = useState(false);
  const [ragStatus, setRagStatus] = useState('');

  useEffect(() => {
    checkDatabaseStatus();
    checkRagStatus();
  }, []);

  const checkDatabaseStatus = async () => {
    try {
      const res = await fetch('http://localhost:3000/chat/health');
      const data = await res.json();
      if (data.status === 'healthy') {
        setStatus('✅ Database Agent: Connected');
      } else {
        setStatus('❌ Database Agent: Error');
      }
    } catch {
      setStatus('❌ Database Agent: Connection Error');
    }
  };

  const checkRagStatus = async () => {
    try {
      const res = await fetch('http://localhost:3000/chat/health');
      const data = await res.json();
      if (data.status === 'healthy') {
        setRagStatus('✅ RAG Agent: Ready (Coming Soon)');
      } else {
        setRagStatus('❌ RAG Agent: Error');
      }
    } catch {
      setRagStatus('❌ RAG Agent: Connection Error');
    }
  };

  // RAG Functions
  const handleRagQuery = async () => {
    if (!ragQuestion.trim()) return;

    setRagLoading(true);
    try {
      const res = await fetch('http://localhost:3000/chat/rag', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: 'Bearer test-token',
        },
        body: JSON.stringify({
          message: ragQuestion,
          user_role: userRole,
        }),
      });
      const data = await res.json();
      if (data.success) {
        setRagResponse(data.response);
      } else {
        setRagResponse(`Error: ${data.message}`);
      }
    } catch {
      setRagResponse('Error: Failed to connect to RAG agent');
    } finally {
      setRagLoading(false);
    }
  };

  // Database Agent Functions
  const handleDatabaseQuery = async () => {
    if (!question.trim()) return;

    setLoading(true);
    try {
      const res = await fetch('http://localhost:3000/chat/database', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: 'Bearer test-token',
        },
        body: JSON.stringify({
          message: question,
          user_role: userRole,
        }),
      });
      const data = await res.json();
      if (data.success) {
        setResponse(data.response);
      } else {
        setResponse(`Error: ${data.message}`);
      }
    } catch {
      setResponse('Error: Failed to connect to database agent');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            🤖 AI Agentic System
          </h1>
          <p className="text-lg text-gray-600">
            Database Analysis with LangGraph Agent
          </p>
        </div>

        {/* Tab Navigation */}
        <div className="flex justify-center mb-8">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-1">
            <button
              onClick={() => setActiveTab('database')}
              className={`px-6 py-2 rounded-md font-medium transition-colors ${
                activeTab === 'database'
                  ? 'bg-blue-500 text-white'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              🗄️ Database Agent
            </button>
            <button
              onClick={() => setActiveTab('rag')}
              className={`px-6 py-2 rounded-md font-medium transition-colors ${
                activeTab === 'rag'
                  ? 'bg-blue-500 text-white'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              📚 RAG Agent
            </button>
          </div>
        </div>

        {/* Database Agent Tab */}
        {activeTab === 'database' && (
          <div className="max-w-4xl mx-auto">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-semibold text-gray-900">
                  🗄️ Database Agent
                </h2>
                <button
                  onClick={checkDatabaseStatus}
                  className="px-4 py-2 bg-green-500 text-white rounded-md hover:bg-green-600 transition-colors"
                >
                  Check Status
                </button>
              </div>

              {status && <p className="mb-4 text-sm text-gray-600">{status}</p>}

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Ask about the database:
                  </label>
                  <textarea
                    className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    rows={3}
                    placeholder="e.g., Which customer bought products from all categories?"
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                  />
                </div>

                <div className="flex items-center gap-4">
                  <div className="flex items-center gap-2">
                    <label className="text-sm font-medium text-gray-700">
                      Role:
                    </label>
                    <select
                      value={userRole}
                      onChange={(e) =>
                        setUserRole(
                          e.target.value as 'employee' | 'manager' | 'admin',
                        )
                      }
                      className="px-3 py-1 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    >
                      <option value="employee">Employee</option>
                      <option value="manager">Manager</option>
                      <option value="admin">Admin</option>
                    </select>
                  </div>
                </div>

                <button
                  onClick={handleDatabaseQuery}
                  disabled={loading || !question.trim()}
                  className="w-full py-3 px-4 bg-blue-500 text-white rounded-md hover:bg-blue-600 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
                >
                  {loading ? '🤔 Thinking...' : '🗄️ Ask Database Agent'}
                </button>

                {response && (
                  <div className="mt-6 p-4 bg-gray-50 rounded-md">
                    <h3 className="font-medium text-gray-900 mb-2">
                      Response:
                    </h3>
                    <p className="text-gray-700 whitespace-pre-wrap">
                      {response}
                    </p>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* RAG Agent Tab */}
        {activeTab === 'rag' && (
          <div className="max-w-4xl mx-auto">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-semibold text-gray-900">
                  📚 RAG Agent
                </h2>
                <button
                  onClick={checkRagStatus}
                  className="px-4 py-2 bg-green-500 text-white rounded-md hover:bg-green-600 transition-colors"
                >
                  Check Status
                </button>
              </div>

              {ragStatus && (
                <p className="mb-4 text-sm text-gray-600">{ragStatus}</p>
              )}

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Ask about documents:
                  </label>
                  <textarea
                    className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    rows={3}
                    placeholder="e.g., What is the main topic of the documents?"
                    value={ragQuestion}
                    onChange={(e) => setRagQuestion(e.target.value)}
                  />
                </div>

                <div className="flex items-center gap-4">
                  <div className="flex items-center gap-2">
                    <label className="text-sm font-medium text-gray-700">
                      Role:
                    </label>
                    <select
                      value={userRole}
                      onChange={(e) =>
                        setUserRole(
                          e.target.value as 'employee' | 'manager' | 'admin',
                        )
                      }
                      className="px-3 py-1 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    >
                      <option value="employee">Employee</option>
                      <option value="manager">Manager</option>
                      <option value="admin">Admin</option>
                    </select>
                  </div>
                </div>

                <button
                  onClick={handleRagQuery}
                  disabled={ragLoading || !ragQuestion.trim()}
                  className="w-full py-3 px-4 bg-blue-500 text-white rounded-md hover:bg-blue-600 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
                >
                  {ragLoading ? '🤔 Thinking...' : '📚 Ask RAG Agent'}
                </button>

                {ragResponse && (
                  <div className="mt-6 p-4 bg-gray-50 rounded-md">
                    <h3 className="font-medium text-gray-900 mb-2">
                      Response:
                    </h3>
                    <p className="text-gray-700 whitespace-pre-wrap">
                      {ragResponse}
                    </p>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Footer */}
        <div className="text-center mt-12 text-gray-500">
          <p>Built with ❤️ using NestJS, React, FastAPI, and LangGraph</p>
          <p className="text-sm mt-2">
            Database Agent: OpenAI GPT models | RAG Agent: Coming soon
          </p>
        </div>
      </div>
    </div>
  );
}

export default App;
