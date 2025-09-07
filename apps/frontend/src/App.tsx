import { useState, useEffect } from 'react';
import './App.css';

interface ModelConfig {
  provider: string;
  model: string;
}

interface AvailableModels {
  [key: string]: {
    available: boolean;
    models: string[];
    requiresApiKey: boolean;
  };
}

function App() {
  const [activeTab, setActiveTab] = useState<'database' | 'backend'>(
    'database',
  );

  // Database Agent Tab State
  const [question, setQuestion] = useState('');
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState('');

  // Backend Tab State (existing functionality)
  const [backendQuestion, setBackendQuestion] = useState('');
  const [backendResponse, setBackendResponse] = useState('');
  const [backendLoading, setBackendLoading] = useState(false);
  const [backendStatus, setBackendStatus] = useState('');
  const [availableModels, setAvailableModels] = useState<AvailableModels>({});
  const [selectedModel, setSelectedModel] = useState<ModelConfig>({
    provider: 'openai',
    model: 'gpt-3.5-turbo',
  });

  useEffect(() => {
    loadAvailableModels();
    checkStatus();
  }, []);

  const loadAvailableModels = async () => {
    try {
      const res = await fetch('http://localhost:3000/agent/models');
      const data = await res.json();
      if (data.success) {
        setAvailableModels(data.models);
      }
    } catch (error) {
      console.error('Error loading models:', error);
    }
  };

  const checkStatus = async () => {
    try {
      const res = await fetch('http://localhost:3000/agent/status');
      const data = await res.json();
      if (data.success) {
        setStatus('✅ Backend System: Connected');
      } else {
        setStatus('❌ Backend System: Error');
      }
    } catch (error) {
      setStatus('❌ Backend System: Connection Error');
    }
  };

  const checkDatabaseStatus = async () => {
    try {
      const res = await fetch('http://localhost:3000/chat/health');
      const data = await res.json();
      if (data.status === 'healthy') {
        setStatus('✅ Database Agent: Connected');
      } else {
        setStatus('❌ Database Agent: Error');
      }
    } catch (error) {
      setStatus('❌ Database Agent: Connection Error');
    }
  };

  // Database Agent Functions
  const handleDatabaseQuery = async () => {
    if (!question.trim()) return;

    setLoading(true);
    try {
      const res = await fetch('http://localhost:3000/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: 'Bearer test-token',
        },
        body: JSON.stringify({
          message: question,
        }),
      });
      const data = await res.json();
      if (data.success) {
        setResponse(data.response);
      } else {
        setResponse(`Error: ${data.message}`);
      }
    } catch (error) {
      setResponse('Error: Failed to connect to database agent');
    } finally {
      setLoading(false);
    }
  };

  // Backend Functions (existing functionality)
  const handleBackendQuery = async () => {
    if (!backendQuestion.trim()) return;

    setBackendLoading(true);
    try {
      const res = await fetch('http://localhost:3000/agent/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question: backendQuestion,
          modelConfig: selectedModel,
        }),
      });
      const data = await res.json();
      if (data.success) {
        setBackendResponse(data.response);
      } else {
        setBackendResponse(`Error: ${data.message}`);
      }
    } catch (error) {
      setBackendResponse('Error: Failed to connect to backend');
    } finally {
      setBackendLoading(false);
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
              onClick={() => setActiveTab('backend')}
              className={`px-6 py-2 rounded-md font-medium transition-colors ${
                activeTab === 'backend'
                  ? 'bg-blue-500 text-white'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              🔧 Backend System
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

        {/* Backend System Tab */}
        {activeTab === 'backend' && (
          <div className="max-w-4xl mx-auto">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-semibold text-gray-900">
                  🔧 Backend System
                </h2>
                <button
                  onClick={checkStatus}
                  className="px-4 py-2 bg-green-500 text-white rounded-md hover:bg-green-600 transition-colors"
                >
                  Check Status
                </button>
              </div>

              {backendStatus && (
                <p className="mb-4 text-sm text-gray-600">{backendStatus}</p>
              )}

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Model Configuration:
                  </label>
                  <div className="grid grid-cols-2 gap-4">
                    <select
                      className="p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      value={selectedModel.provider}
                      onChange={(e) =>
                        setSelectedModel({
                          ...selectedModel,
                          provider: e.target.value,
                          model:
                            availableModels[e.target.value]?.models[0] || '',
                        })
                      }
                    >
                      {Object.entries(availableModels).map(
                        ([provider, info]) => (
                          <option key={provider} value={provider}>
                            {provider} {info.available ? '✅' : '❌'}
                          </option>
                        ),
                      )}
                    </select>
                    <select
                      className="p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      value={selectedModel.model}
                      onChange={(e) =>
                        setSelectedModel({
                          ...selectedModel,
                          model: e.target.value,
                        })
                      }
                    >
                      {availableModels[selectedModel.provider]?.models.map(
                        (model) => (
                          <option key={model} value={model}>
                            {model}
                          </option>
                        ),
                      )}
                    </select>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Ask a question:
                  </label>
                  <textarea
                    className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    rows={3}
                    placeholder="Enter your question here..."
                    value={backendQuestion}
                    onChange={(e) => setBackendQuestion(e.target.value)}
                  />
                </div>

                <button
                  onClick={handleBackendQuery}
                  disabled={backendLoading || !backendQuestion.trim()}
                  className="w-full py-3 px-4 bg-blue-500 text-white rounded-md hover:bg-blue-600 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
                >
                  {backendLoading ? '🤔 Thinking...' : '🔧 Ask Backend'}
                </button>

                {backendResponse && (
                  <div className="mt-6 p-4 bg-gray-50 rounded-md">
                    <h3 className="font-medium text-gray-900 mb-2">
                      Response:
                    </h3>
                    <p className="text-gray-700 whitespace-pre-wrap">
                      {backendResponse}
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
            Database Agent: OpenAI GPT models | Document processing: Coming soon
          </p>
        </div>
      </div>
    </div>
  );
}

export default App;
