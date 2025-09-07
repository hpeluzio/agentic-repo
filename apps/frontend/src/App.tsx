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
  const [activeTab, setActiveTab] = useState<'direct' | 'backend'>('direct');

  // Direct Agent Tab State
  const [directQuestion, setDirectQuestion] = useState('');
  const [directResponse, setDirectResponse] = useState('');
  const [directLoading, setDirectLoading] = useState(false);
  const [directStatus, setDirectStatus] = useState('');

  // Backend Tab State (existing functionality)
  const [question, setQuestion] = useState('');
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState('');
  const [availableModels, setAvailableModels] = useState<AvailableModels>({});
  const [selectedModel, setSelectedModel] = useState<ModelConfig>({
    provider: 'ollama',
    model: 'llama3.1:8b',
  });

  useEffect(() => {
    loadAvailableModels();
    checkStatus();
    checkDirectStatus();
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

  const handleQuery = async () => {
    if (!question.trim()) return;

    setLoading(true);
    try {
      const requestBody: { question: string; modelConfig?: ModelConfig } = {
        question,
      };

      // Only send modelConfig for non-Ollama models (API keys are handled server-side)
      if (selectedModel.provider !== 'ollama') {
        requestBody.modelConfig = selectedModel;
      }

      const res = await fetch('http://localhost:3000/agent/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });

      const data = await res.json();
      if (data.success) {
        setResponse(data.response);
      } else {
        setResponse('Error: ' + data.message);
      }
    } catch {
      setResponse('Error connecting to backend');
    } finally {
      setLoading(false);
    }
  };

  const checkStatus = async () => {
    try {
      const res = await fetch('http://localhost:3000/agent/status');
      const data = await res.json();
      setStatus(`Status: ${data.status} (${data.timestamp})`);
    } catch {
      setStatus('Error checking status');
    }
  };

  const handleModelChange = (provider: string, model: string) => {
    setSelectedModel({ provider, model });
  };

  // Direct Agent functions
  const handleDirectQuery = async () => {
    if (!directQuestion.trim()) return;

    setDirectLoading(true);
    try {
      const res = await fetch('http://localhost:3000/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: 'Bearer test-token',
        },
        body: JSON.stringify({
          message: directQuestion,
        }),
      });

      const data = await res.json();
      if (data.success) {
        setDirectResponse(data.response);
      } else {
        setDirectResponse(
          'Error: ' + (data.message || data.response || 'Unknown error'),
        );
      }
    } catch (error) {
      setDirectResponse('Error connecting to chat endpoint');
    } finally {
      setDirectLoading(false);
    }
  };

  const checkDirectStatus = async () => {
    try {
      const res = await fetch('http://localhost:3000/chat/health', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      const data = await res.json();
      setDirectStatus(
        `Chat Service: ${data.status} (${
          data.services ? Object.keys(data.services).join(', ') : 'N/A'
        })`,
      );
    } catch {
      setDirectStatus('Chat Service: Error checking status');
    }
  };

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

        {/* Tabs */}
        <div className="bg-white rounded-lg shadow-md mb-6">
          <div className="flex border-b">
            <button
              onClick={() => setActiveTab('direct')}
              className={`flex-1 px-6 py-3 text-sm font-medium transition-colors ${
                activeTab === 'direct'
                  ? 'text-indigo-600 border-b-2 border-indigo-600 bg-indigo-50'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              🚀 Chat Service (Port 3000)
            </button>
            <button
              onClick={() => setActiveTab('backend')}
              className={`flex-1 px-6 py-3 text-sm font-medium transition-colors ${
                activeTab === 'backend'
                  ? 'text-indigo-600 border-b-2 border-indigo-600 bg-indigo-50'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              🔧 Backend System (Port 3000)
            </button>
          </div>
        </div>

        {/* Tab Content */}
        {activeTab === 'direct' ? (
          /* Direct Agent Tab */
          <>
            {/* Direct Agent Status */}
            <div className="bg-white rounded-lg shadow-md p-6 mb-6">
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-semibold text-gray-700">
                  Chat Service Status
                </h2>
                <button
                  onClick={checkDirectStatus}
                  className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors"
                >
                  Check Status
                </button>
              </div>
              {directStatus && (
                <p className="mt-2 text-sm text-gray-600">{directStatus}</p>
              )}
            </div>

            {/* Direct Agent Query Interface */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-xl font-semibold text-gray-700 mb-4">
                Ask Chat Service (LangGraph + Database Tools)
              </h2>

              <div className="space-y-4">
                <div>
                  <label
                    htmlFor="directQuestion"
                    className="block text-sm font-medium text-gray-700 mb-2"
                  >
                    Your Question
                  </label>
                  <textarea
                    id="directQuestion"
                    value={directQuestion}
                    onChange={(e) => setDirectQuestion(e.target.value)}
                    placeholder="Ask anything about the database or general questions..."
                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent resize-none"
                    rows={4}
                  />
                </div>

                <div className="text-sm text-gray-600 bg-green-50 p-3 rounded-lg">
                  <strong>Chat Service Features:</strong> Database queries, SQL
                  generation, customer analysis, product information, and
                  general AI assistance via python-agent.
                </div>

                <button
                  onClick={handleDirectQuery}
                  disabled={directLoading || !directQuestion.trim()}
                  className="w-full px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  {directLoading ? '🤔 Thinking...' : '🚀 Ask Chat Service'}
                </button>
              </div>

              {/* Direct Response */}
              {directResponse && (
                <div className="mt-6">
                  <h3 className="text-lg font-semibold text-gray-700 mb-2">
                    Response
                  </h3>
                  <div className="bg-gray-50 rounded-lg p-4 border-l-4 border-green-500">
                    <p className="text-gray-800 whitespace-pre-wrap">
                      {directResponse}
                    </p>
                  </div>
                </div>
              )}
            </div>
          </>
        ) : (
          /* Backend Tab (existing functionality) */
          <>
            {/* Status Check */}
            <div className="bg-white rounded-lg shadow-md p-6 mb-6">
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-semibold text-gray-700">
                  Backend System Status
                </h2>
                <button
                  onClick={checkStatus}
                  className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
                >
                  Check Status
                </button>
              </div>
              {status && <p className="mt-2 text-sm text-gray-600">{status}</p>}
            </div>

            {/* Model Selection */}
            <div className="bg-white rounded-lg shadow-md p-6 mb-6">
              <h2 className="text-xl font-semibold text-gray-700 mb-4">
                AI Model Selection
              </h2>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {Object.entries(availableModels).map(([provider, info]) => (
                  <div key={provider} className="border rounded-lg p-4">
                    <h3 className="font-semibold text-gray-700 mb-2 capitalize">
                      {provider} {info.available ? '✅' : '❌'}
                    </h3>
                    {info.available && (
                      <div className="space-y-2">
                        {info.models.map((model) => (
                          <button
                            key={model}
                            onClick={() => handleModelChange(provider, model)}
                            className={`w-full text-left p-2 rounded text-sm transition-colors ${
                              selectedModel.provider === provider &&
                              selectedModel.model === model
                                ? 'bg-indigo-100 text-indigo-700 border border-indigo-300'
                                : 'bg-gray-50 text-gray-700 hover:bg-gray-100'
                            }`}
                          >
                            {model}
                          </button>
                        ))}
                        {info.requiresApiKey && (
                          <div className="text-xs text-gray-500 mt-2 p-2 bg-gray-50 rounded">
                            API key configured in backend
                          </div>
                        )}
                      </div>
                    )}
                    {!info.available && (
                      <p className="text-sm text-gray-500">
                        {provider === 'ollama'
                          ? 'Install Ollama first'
                          : 'Install required packages'}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* Query Interface */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-xl font-semibold text-gray-700 mb-4">
                Ask a Question
              </h2>

              <div className="space-y-4">
                <div>
                  <label
                    htmlFor="question"
                    className="block text-sm font-medium text-gray-700 mb-2"
                  >
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

                <div className="text-sm text-gray-600">
                  Selected Model:{' '}
                  <span className="font-medium">
                    {selectedModel.provider}:{selectedModel.model}
                  </span>
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
                    <p className="text-gray-800 whitespace-pre-wrap">
                      {response}
                    </p>
                  </div>
                </div>
              )}
            </div>
          </>
        )}

        {/* Footer */}
        <div className="text-center mt-8 text-gray-500 text-sm">
          <p>
            {activeTab === 'direct'
              ? 'Powered by NestJS + FastAPI + LangGraph + OpenAI + SQLite Database'
              : 'Powered by NestJS + React + LlamaIndex + Multiple AI Models'}
          </p>
        </div>
      </div>
    </div>
  );
}

export default App;
