# 🤖 AI Agentic System

A modern monorepo architecture for AI-powered document querying using NestJS, React, and LlamaIndex with ChromaDB.

## 🏗️ Architecture

```
ai-agentic/
├── apps/
│   ├── backend/         → NestJS (REST API)
│   ├── frontend/        → React + Tailwind CSS
│   └── llama-bridge/    → Python (LlamaIndex + ChromaDB)
├── docker-compose.yml
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ and pnpm
- Python 3.8+
- Docker (optional)

### Installation

1. **Install pnpm globally:**
   ```bash
   npm install -g pnpm
   ```

2. **Clone and setup:**
   ```bash
   git clone <repository-url>
   cd ai-agentic
   ```

3. **Setup Backend:**
   ```bash
   cd apps/backend
   pnpm install
   ```

4. **Setup Frontend:**
   ```bash
   cd ../frontend
   pnpm install
   ```

5. **Setup Python Environment:**
   ```bash
   cd ../llama-bridge
   python3 -m venv venv
   source venv/bin/activate  # Mac/Linux
   # venv\Scripts\activate   # Windows
   pip install llama-index chromadb openai
   ```

6. **Configure Environment:**
   ```bash
   # In apps/backend/.env
   OPENAI_API_KEY=your-openai-api-key-here
   ```

## 🧪 Running Locally

### Backend (NestJS)
```bash
cd apps/backend
pnpm run start:dev
```
Backend will be available at `http://localhost:3000`

### Frontend (React)
```bash
cd apps/frontend
pnpm run dev
```
Frontend will be available at `http://localhost:5173`

### Python Query Engine
```bash
cd apps/llama-bridge
source venv/bin/activate
python query_engine.py "Your question here"
```

## 🐳 Docker Setup

Run the entire system with Docker:

```bash
docker-compose up --build
```

## 📁 Adding Documents

1. Create a `documents` folder in `apps/llama-bridge/`
2. Add your documents (PDF, TXT, DOCX, etc.)
3. The system will automatically index them

## 🔧 API Endpoints

### Backend API (`http://localhost:3000`)

- `POST /agent/query` - Query documents
  ```json
  {
    "question": "What is the content about?"
  }
  ```

- `GET /agent/status` - Check system status

- `POST /agent/add-document` - Add document (placeholder)

## 🛠️ Development

### Backend Development
- Built with NestJS
- TypeScript support
- REST API endpoints
- Python script integration

### Frontend Development
- React 19 with TypeScript
- Tailwind CSS for styling
- Modern UI with responsive design
- Real-time status checking

### Python Bridge
- LlamaIndex for document processing
- ChromaDB for vector storage
- OpenAI integration for embeddings and LLM

## 📦 Tech Stack

- **Backend:** NestJS, TypeScript, Node.js
- **Frontend:** React 19, TypeScript, Tailwind CSS
- **AI/ML:** LlamaIndex, ChromaDB, OpenAI
- **Package Manager:** pnpm
- **Containerization:** Docker

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support

If you encounter any issues:

1. Check the logs in each service
2. Ensure all dependencies are installed
3. Verify your OpenAI API key is set correctly
4. Make sure the Python virtual environment is activated

## 🔮 Future Enhancements

- [ ] File upload interface
- [ ] Document management dashboard
- [ ] Advanced query options
- [ ] User authentication
- [ ] Multi-language support
- [ ] Real-time document processing 