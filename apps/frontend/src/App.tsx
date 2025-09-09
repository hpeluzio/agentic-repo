import { useState, useEffect } from 'react';
import './App.css';

interface Message {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: Date;
  agent: 'database' | 'rag' | 'smart' | 'ocr';
  sources?: Array<{
    title: string;
    category: string;
    relevance_score: number;
  }>;
  sql_info?: {
    queries_executed: Array<{
      type: string;
      description: string;
      sql_query: string | null;
    }>;
    total_execution_time: number;
    queries_count: number;
  };
  agent_used?: string;
  routing_info?: {
    agent: string;
    confidence: string;
    reasoning: string;
  };
  extracted_text?: string;
  recommendations?: string[];
  alerts?: string[];
}

function App() {
  const [activeAgent, setActiveAgent] = useState<
    'database' | 'rag' | 'smart' | 'ocr'
  >('database');
  const [userRole, setUserRole] = useState<'employee' | 'manager' | 'admin'>(
    'employee',
  );
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  useEffect(() => {
    checkSystemStatus();
  }, []);

  const checkSystemStatus = async () => {
    try {
      const res = await fetch('http://localhost:3000/chat/health');
      const data = await res.json();
      console.log('System status:', data);
    } catch {
      console.error('System status check failed');
    }
  };

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || loading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputMessage,
      role: 'user',
      timestamp: new Date(),
      agent: activeAgent,
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputMessage('');
    setLoading(true);

    try {
      const endpoint =
        activeAgent === 'database'
          ? '/chat/database'
          : activeAgent === 'rag'
          ? '/chat/rag'
          : '/chat/smart';
      const body =
        activeAgent === 'database' || activeAgent === 'smart'
          ? { message: inputMessage, user_role: userRole }
          : { message: inputMessage };

      const res = await fetch(`http://localhost:3000${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: 'Bearer test-token',
        },
        body: JSON.stringify(body),
      });

      const data = await res.json();

      // Check if the response indicates an error
      if (!res.ok) {
        let errorContent = `❌ Error: ${data.message || 'Request failed'}`;

        // Special handling for permission errors
        if (res.status === 403) {
          errorContent = `🚫 **Access Denied**\n\n${data.message}\n\n**Current Role:** ${userRole}\n**Required Roles:** Admin or Manager\n\n💡 **Tip:** Switch to Admin or Manager role in the sidebar to access database queries.`;
        } else if (res.status === 401) {
          errorContent = `🔐 **Unauthorized**\n\n${data.message}\n\nPlease check your authentication.`;
        } else if (res.status === 500) {
          errorContent = `⚠️ **Server Error**\n\n${data.message}\n\nPlease try again later or contact support.`;
        }

        const errorMessage: Message = {
          id: (Date.now() + 1).toString(),
          content: errorContent,
          role: 'assistant',
          timestamp: new Date(),
          agent: activeAgent,
        };
        setMessages((prev) => [...prev, errorMessage]);
        return;
      }

      // Check if the response is successful
      if (!data.success) {
        const errorMessage: Message = {
          id: (Date.now() + 1).toString(),
          content: `❌ Error: ${data.message || 'Request failed'}`,
          role: 'assistant',
          timestamp: new Date(),
          agent: activeAgent,
        };
        setMessages((prev) => [...prev, errorMessage]);
        return;
      }

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: data.response || 'No response received',
        role: 'assistant',
        timestamp: new Date(),
        agent: activeAgent,
        sources: data.sources,
        sql_info: data.sql_info,
        agent_used: data.agent_used,
        routing_info: data.routing_info,
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: 'Error: Failed to connect to the agent. Please try again.',
        role: 'assistant',
        timestamp: new Date(),
        agent: activeAgent,
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const clearChat = () => {
    setMessages([]);
  };

  const newChat = () => {
    setMessages([]);
    setInputMessage('');
  };

  const handleFileUpload = async () => {
    if (!selectedFile || loading) return;

    setLoading(true);
    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const response = await fetch('http://localhost:3000/chat/ocr', {
        method: 'POST',
        headers: {
          Authorization: 'Bearer test-token',
        },
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.message || 'Failed to process file');
      }

      if (data.success) {
        // Add OCR result as a message
        const ocrMessage: Message = {
          id: Date.now().toString(),
          content: data.analysis,
          role: 'assistant',
          timestamp: new Date(),
          agent: 'ocr',
          extracted_text: data.extracted_text,
          recommendations: data.recommendations,
          alerts: data.alerts,
        };

        setMessages((prev) => [...prev, ocrMessage]);
      }
    } catch (error) {
      console.error('Error processing file:', error);
      const errorMessage: Message = {
        id: Date.now().toString(),
        content: `❌ Error processing file: ${
          error instanceof Error ? error.message : 'Unknown error'
        }`,
        role: 'assistant',
        timestamp: new Date(),
        agent: 'ocr',
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-screen bg-gray-900 text-white">
      {/* Sidebar */}
      <div
        className={`${
          sidebarOpen ? 'w-64' : 'w-0'
        } transition-all duration-300 bg-gray-800 border-r border-gray-700 flex flex-col overflow-hidden`}
      >
        <div className="header-container sidebar-header">
          <div className="header-content">
            <h1 className="header-title">AI Agents</h1>
            <button
              onClick={() => setSidebarOpen(false)}
              className="p-1 hover:bg-gray-700 rounded"
            >
              ✕
            </button>
          </div>
        </div>

        <div className="flex-1 p-4 space-y-4">
          {/* Agent Selection */}
          <div>
            <h3 className="text-sm font-medium text-gray-400 mb-2">
              Select Agent
            </h3>
            <div className="space-y-2">
              <button
                onClick={() => setActiveAgent('database')}
                className={`w-full text-left p-3 rounded-lg transition-colors ${
                  activeAgent === 'database'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-700 hover:bg-gray-600 text-gray-300'
                }`}
              >
                <div className="flex items-center gap-2">
                  <span>🗄️</span>
                  <div>
                    <div className="font-medium">Database Agent</div>
                    <div className="text-xs text-gray-400">SQL Analysis</div>
                  </div>
                </div>
              </button>

              <button
                onClick={() => setActiveAgent('rag')}
                className={`w-full text-left p-3 rounded-lg transition-colors ${
                  activeAgent === 'rag'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-700 hover:bg-gray-600 text-gray-300'
                }`}
              >
                <div className="flex items-center gap-2">
                  <span>📚</span>
                  <div>
                    <div className="font-medium">RAG Agent</div>
                    <div className="text-xs text-gray-400">Document Search</div>
                  </div>
                </div>
              </button>

              <button
                onClick={() => setActiveAgent('smart')}
                className={`w-full text-left p-3 rounded-lg transition-colors ${
                  activeAgent === 'smart'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-700 hover:bg-gray-600 text-gray-300'
                }`}
              >
                <div className="flex items-center gap-2">
                  <span>🧠</span>
                  <div>
                    <div className="font-medium">Smart Agent</div>
                    <div className="text-xs text-gray-400">Auto-Route</div>
                  </div>
                </div>
              </button>

              <button
                onClick={() => setActiveAgent('ocr')}
                className={`w-full text-left p-3 rounded-lg transition-colors ${
                  activeAgent === 'ocr'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-700 hover:bg-gray-600 text-gray-300'
                }`}
              >
                <div className="flex items-center gap-2">
                  <span>🏥</span>
                  <div>
                    <div className="font-medium">OCR Agent</div>
                    <div className="text-xs text-gray-400">Lab Analysis</div>
                  </div>
                </div>
              </button>
            </div>
          </div>

          {/* Role Selection (Database and Smart Agents) */}
          {(activeAgent === 'database' || activeAgent === 'smart') && (
            <div>
              <h3 className="text-sm font-medium text-gray-400 mb-2">
                User Role
              </h3>
              <select
                value={userRole}
                onChange={(e) =>
                  setUserRole(
                    e.target.value as 'employee' | 'manager' | 'admin',
                  )
                }
                className={`w-full p-2 bg-gray-700 border rounded text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                  userRole === 'employee'
                    ? 'border-red-500 bg-red-900/20'
                    : 'border-gray-600'
                }`}
              >
                <option value="employee">👤 Employee (Limited)</option>
                <option value="manager">👔 Manager (Moderate)</option>
                <option value="admin">👑 Admin (Full Access)</option>
              </select>
              {userRole === 'employee' && (
                <div className="mt-2 p-2 bg-red-900/30 border border-red-500/50 rounded text-xs text-red-300">
                  ⚠️ Employee role has limited database access. Switch to
                  Manager for moderate access or Admin for full access.
                </div>
              )}
              {userRole === 'manager' && (
                <div className="mt-2 p-2 bg-yellow-900/30 border border-yellow-500/50 rounded text-xs text-yellow-300">
                  ⚠️ Manager role has moderate access. Some sensitive data may
                  be restricted. Switch to Admin for full access.
                </div>
              )}
            </div>
          )}

          {/* Chat Actions */}
          <div className="space-y-2">
            <button
              onClick={newChat}
              className="w-full p-2 bg-gray-700 hover:bg-gray-600 rounded text-sm transition-colors"
            >
              + New Chat
            </button>
            <button
              onClick={clearChat}
              className="w-full p-2 bg-gray-700 hover:bg-gray-600 rounded text-sm transition-colors"
            >
              Clear History
            </button>
          </div>
        </div>

        {/* User Profile */}
        <div className="p-4 border-t border-gray-700">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center text-sm font-medium">
              US
            </div>
            <div>
              <div className="text-sm font-medium">User</div>
              <div className="text-xs text-gray-400">
                {userRole.charAt(0).toUpperCase() + userRole.slice(1)} Role
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="header-container main-header">
          <div className="header-content">
            <div className="flex items-center gap-3">
              {!sidebarOpen && (
                <button
                  onClick={() => setSidebarOpen(true)}
                  className="p-2 hover:bg-gray-700 rounded"
                >
                  ☰
                </button>
              )}
              <div>
                <h2 className="header-title">
                  {activeAgent === 'database'
                    ? '🗄️ Database Agent'
                    : activeAgent === 'rag'
                    ? '📚 RAG Agent'
                    : activeAgent === 'smart'
                    ? '🧠 Smart Agent'
                    : '🏥 OCR Agent'}
                </h2>
                <p className="header-subtitle">
                  {activeAgent === 'database'
                    ? 'Ask questions about your database and get SQL insights'
                    : activeAgent === 'rag'
                    ? 'Search through company documents and policies'
                    : activeAgent === 'smart'
                    ? 'Intelligent agent that automatically routes your queries'
                    : 'Upload lab exam PDFs for intelligent analysis'}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              <span className="text-sm text-gray-400">Online</span>
            </div>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.length === 0 ? (
            <div className="flex items-center justify-center h-full">
              <div className="text-center">
                <div className="text-6xl mb-4">
                  {activeAgent === 'database'
                    ? '🗄️'
                    : activeAgent === 'rag'
                    ? '📚'
                    : activeAgent === 'smart'
                    ? '🧠'
                    : '🏥'}
                </div>
                <h3 className="text-xl font-semibold mb-2">
                  {activeAgent === 'database'
                    ? 'Database Agent'
                    : activeAgent === 'rag'
                    ? 'RAG Agent'
                    : activeAgent === 'smart'
                    ? 'Smart Agent'
                    : 'OCR Agent'}
                </h3>
                <p className="text-gray-400 mb-4">
                  {activeAgent === 'database'
                    ? 'Ask me anything about your database. I can help with SQL queries, data analysis, and insights.'
                    : activeAgent === 'rag'
                    ? 'Ask me anything about company documents, policies, and procedures.'
                    : activeAgent === 'smart'
                    ? "Ask me anything! I'll automatically choose the best agent (Database or RAG) to answer your question."
                    : 'Upload lab exam PDFs or images for intelligent analysis. I can extract text and provide medical insights.'}
                </p>
                <div className="text-sm text-gray-500">
                  {(activeAgent === 'database' || activeAgent === 'smart') &&
                    userRole === 'employee' && (
                      <div className="mb-4 p-3 bg-red-900/20 border border-red-500/50 rounded-lg">
                        <p className="text-red-300 font-medium mb-1">
                          ⚠️ Limited Access - Employee Role
                        </p>
                        <p className="text-red-200 text-xs">
                          You can only ask general questions. For detailed
                          database analysis, switch to Manager or Admin role in
                          the sidebar.
                        </p>
                      </div>
                    )}
                  {activeAgent === 'database' && userRole === 'admin' && (
                    <p className="mb-2 text-green-300">
                      ✅ Full Access - Admin Role
                    </p>
                  )}
                  {activeAgent === 'database' && userRole === 'manager' && (
                    <p className="mb-2 text-yellow-300">
                      ⚠️ Moderate Access - Manager Role
                    </p>
                  )}
                  {activeAgent === 'ocr' ? (
                    <div className="mt-6">
                      <div className="mb-4">
                        <input
                          type="file"
                          accept=".pdf,.png,.jpg,.jpeg"
                          onChange={(e) =>
                            setSelectedFile(e.target.files?.[0] || null)
                          }
                          className="mb-4 p-2 bg-gray-700 border border-gray-600 rounded text-white"
                        />
                        <button
                          onClick={handleFileUpload}
                          disabled={!selectedFile || loading}
                          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed"
                        >
                          {loading ? 'Processing...' : 'Analyze Lab Results'}
                        </button>
                      </div>
                      <p className="text-sm text-gray-400">
                        Upload PDF or image files of lab exams for intelligent
                        analysis.
                      </p>
                    </div>
                  ) : (
                    <p>Type your question below to get started.</p>
                  )}
                </div>
              </div>
            </div>
          ) : (
            messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${
                  message.role === 'user' ? 'justify-end' : 'justify-start'
                }`}
              >
                <div
                  className={`max-w-3xl p-4 rounded-lg ${
                    message.role === 'user'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-700 text-gray-100'
                  }`}
                >
                  <div className="whitespace-pre-wrap">{message.content}</div>

                  {/* SQL Info for Database Agent and Smart Agent (when using database) */}
                  {message.role === 'assistant' &&
                    (message.agent === 'database' ||
                      (message.agent === 'smart' &&
                        message.agent_used === 'database')) &&
                    message.sql_info && (
                      <div className="mt-3 p-3 bg-gray-800 rounded border-l-4 border-blue-500">
                        <div className="text-sm font-medium text-blue-400 mb-2">
                          SQL Execution Info
                        </div>
                        <div className="text-xs text-gray-300">
                          <div>
                            Queries executed: {message.sql_info.queries_count}
                          </div>
                          <div>
                            Execution time:{' '}
                            {message.sql_info.total_execution_time}ms
                          </div>
                        </div>
                      </div>
                    )}

                  {/* Sources for RAG Agent and Smart Agent (when using RAG) */}
                  {message.role === 'assistant' &&
                    (message.agent === 'rag' ||
                      (message.agent === 'smart' &&
                        message.agent_used === 'rag')) &&
                    message.sources && (
                      <div className="mt-3 p-3 bg-gray-800 rounded border-l-4 border-green-500">
                        <div className="text-sm font-medium text-green-400 mb-2">
                          Sources
                        </div>
                        <div className="space-y-1">
                          {message.sources.map((source, index) => (
                            <div key={index} className="text-xs text-gray-300">
                              📄 {source.title} ({source.category}) - Score:{' '}
                              {source.relevance_score}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                  {/* Routing Info for Smart Agent */}
                  {message.role === 'assistant' &&
                    message.agent === 'smart' &&
                    message.routing_info && (
                      <div className="mt-3 p-3 bg-gray-800 rounded border-l-4 border-purple-500">
                        <div className="text-sm font-medium text-purple-400 mb-2">
                          🧠 Smart Routing
                        </div>
                        <div className="text-xs text-gray-300 space-y-1">
                          <div>
                            <span className="font-medium">Agent Used:</span>{' '}
                            {message.agent_used}
                          </div>
                          <div>
                            <span className="font-medium">Confidence:</span>{' '}
                            {message.routing_info.confidence}
                          </div>
                          <div>
                            <span className="font-medium">Reasoning:</span>{' '}
                            {message.routing_info.reasoning}
                          </div>
                        </div>
                      </div>
                    )}

                  {/* OCR Info for OCR Agent */}
                  {message.role === 'assistant' && message.agent === 'ocr' && (
                    <div className="mt-3 space-y-3">
                      {/* Extracted Text */}
                      {message.extracted_text && (
                        <div className="p-3 bg-gray-800 rounded border-l-4 border-orange-500">
                          <div className="text-sm font-medium text-orange-400 mb-2">
                            📄 Extracted Text
                          </div>
                          <div className="text-xs text-gray-300 max-h-32 overflow-y-auto">
                            {message.extracted_text}
                          </div>
                        </div>
                      )}

                      {/* Recommendations */}
                      {message.recommendations &&
                        message.recommendations.length > 0 && (
                          <div className="p-3 bg-gray-800 rounded border-l-4 border-green-500">
                            <div className="text-sm font-medium text-green-400 mb-2">
                              💡 Recommendations
                            </div>
                            <div className="text-xs text-gray-300 space-y-1">
                              {message.recommendations.map((rec, index) => (
                                <div key={index}>• {rec}</div>
                              ))}
                            </div>
                          </div>
                        )}

                      {/* Alerts */}
                      {message.alerts && message.alerts.length > 0 && (
                        <div className="p-3 bg-gray-800 rounded border-l-4 border-red-500">
                          <div className="text-sm font-medium text-red-400 mb-2">
                            🚨 Alerts
                          </div>
                          <div className="text-xs text-gray-300 space-y-1">
                            {message.alerts.map((alert, index) => (
                              <div key={index}>⚠️ {alert}</div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  )}

                  <div className="text-xs text-gray-400 mt-2">
                    {message.timestamp.toLocaleTimeString()}
                  </div>
                </div>
              </div>
            ))
          )}

          {loading && (
            <div className="flex justify-start">
              <div className="bg-gray-700 p-4 rounded-lg">
                <div className="flex items-center gap-2">
                  <div className="animate-spin w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full"></div>
                  <span className="text-gray-300">Thinking...</span>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Input Area */}
        <div className="p-4 border-t border-gray-700 bg-gray-800">
          <div className="input-container">
            <textarea
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder={`Ask ${
                activeAgent === 'database'
                  ? 'about your database'
                  : activeAgent === 'rag'
                  ? 'about documents'
                  : activeAgent === 'smart'
                  ? "anything - I'll route it automatically"
                  : 'about your uploaded lab results'
              }...`}
              className="input-field"
              rows={1}
            />
            <button
              onClick={handleSendMessage}
              disabled={!inputMessage.trim() || loading}
              className="send-button"
            >
              <span>Send</span>
              <span>→</span>
            </button>
          </div>
          <div className="text-xs text-gray-500 mt-2">
            Press Enter to send, Shift+Enter for new line
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
