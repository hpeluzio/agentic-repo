# 🤖 AI Agentic System

A powerful AI-powered document querying system built with NestJS, React, and LlamaIndex. Supports multiple AI models including OpenAI, Google Gemini, and local Ollama models.

## 🏗️ Architecture

```
ai-agentic/
├── apps/
│   ├── backend/         → NestJS (REST API)
│   ├── frontend/        → React + Tailwind CSS
│   └── llama-bridge/    → Python (LlamaIndex)
├── docker-compose.yml
├── README.md
```

## ✨ Features

- **Multi-Model Support**: Choose between OpenAI, Google Gemini, and local Ollama models
- **Document Processing**: Upload and query documents with AI-powered insights
- **Real-time UI**: Modern React interface with real-time status updates
- **Local & Cloud**: Run locally with Ollama or use cloud APIs
- **No Rate Limits**: Unlimited queries with local models
- **Privacy First**: Keep your data local with Ollama models

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ and pnpm
- Python 3.8+
- Ollama (for local models)

### Installation

1. **Clone and install dependencies:**
```bash
git clone <repository>
cd agentic-repo
pnpm install
```

2. **Install Python dependencies:**
```bash
cd apps/llama-bridge
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install llama-index llama-index-llms-ollama
```

3. **Install Ollama (for local models):**
```bash
# macOS
brew install ollama

# Linux
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama
brew services start ollama  # macOS
sudo systemctl start ollama  # Linux
```

4. **Download a model:**
```bash
ollama pull llama3.1:8b
```

### Running the System

1. **Start the backend:**
```bash
cd apps/backend
pnpm run start:dev
```

2. **Start the frontend:**
```bash
cd apps/frontend
pnpm run dev
```

3. **Access the application:**
- Frontend: http://localhost:5173 (or 5174 if 5173 is busy)
- Backend API: http://localhost:3000

## 🤖 AI Models

### Supported Models

| Provider | Models | Setup Required | Cost |
|----------|--------|----------------|------|
| **Ollama** | llama3.1:8b, llama3.1:70b, mistral:7b, codellama:7b | Install Ollama | Free |
| **OpenAI** | gpt-3.5-turbo, gpt-4, gpt-4-turbo | API Key | Pay-per-use |
| **Google Gemini** | gemini-pro, gemini-pro-vision | API Key | Pay-per-use |

### Model Setup

#### Ollama (Recommended - Free & Local)
```bash
# Install Ollama
brew install ollama  # macOS
curl -fsSL https://ollama.ai/install.sh | sh  # Linux

# Start Ollama service
brew services start ollama

# Download models
ollama pull llama3.1:8b
ollama pull mistral:7b
```

#### OpenAI
```bash
# Set your API key
export OPENAI_API_KEY=sk-your-key-here

# Or add to .env file
echo "OPENAI_API_KEY=sk-your-key-here" >> apps/backend/.env
```

#### Google Gemini
```bash
# Set your API key
export GEMINI_API_KEY=your-gemini-key-here

# Or add to .env file
echo "GEMINI_API_KEY=your-gemini-key-here" >> apps/backend/.env
```

## 📚 Adding Documents

1. **Create documents directory:**
```bash
mkdir apps/llama-bridge/documents
```

2. **Add your files:**
```bash
# Copy your documents to the directory
cp your-document.pdf apps/llama-bridge/documents/
cp your-text.txt apps/llama-bridge/documents/
```

3. **Supported formats:**
- Text files (.txt, .md)
- PDF files (.pdf)
- Word documents (.docx)
- And more via LlamaIndex

## 🔌 API Endpoints

### Query Documents
```bash
POST /agent/query
{
  "question": "What is the main topic?",
  "modelConfig": {
    "provider": "ollama",
    "model": "llama3.1:8b"
  }
}
```

### Get Available Models
```bash
GET /agent/models
```

### System Status
```bash
GET /agent/status
```

### Add Document
```bash
POST /agent/add-document
{
  "filePath": "/path/to/document.pdf"
}
```

## 🐳 Docker Setup

```bash
# Build and run with Docker Compose
docker-compose up --build
```

## 🛠️ Development

### Backend (NestJS)
```bash
cd apps/backend
pnpm run start:dev
```

### Frontend (React)
```bash
cd apps/frontend
pnpm run dev
```

### Python Bridge
```bash
cd apps/llama-bridge
source venv/bin/activate
python query_engine.py "Your question here"
```

## 🧪 Testing

### Test Python Script
```bash
cd apps/llama-bridge
source venv/bin/activate
python query_engine.py "What is in the sample document?"
```

### Test Backend API
```bash
curl -X POST http://localhost:3000/agent/query \
  -H "Content-Type: application/json" \
  -d '{"question": "Test question"}'
```

## 🏗️ Tech Stack

- **Backend**: NestJS, TypeScript
- **Frontend**: React, Vite, Tailwind CSS
- **AI Engine**: LlamaIndex, Python
- **Models**: OpenAI, Google Gemini, Ollama
- **Package Manager**: pnpm
- **Containerization**: Docker Compose

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

- **Issues**: Create an issue on GitHub
- **Documentation**: Check the docs folder
- **Community**: Join our Discord server

## 🔮 Future Enhancements

- [ ] File upload interface
- [ ] Document management UI
- [ ] Conversation history
- [ ] Multiple document collections
- [ ] Advanced search filters
- [ ] Export functionality
- [ ] User authentication
- [ ] Multi-user support
- [ ] API rate limiting
- [ ] WebSocket real-time updates

## 🎯 Why This System?

- **Flexibility**: Choose the AI model that fits your needs
- **Cost Control**: Use free local models or paid cloud APIs
- **Privacy**: Keep sensitive data local with Ollama
- **Scalability**: Easy to add new models and features
- **Modern Stack**: Built with the latest technologies
- **Open Source**: Full control over your AI system

---

**Built with ❤️ using NestJS, React, and LlamaIndex** 