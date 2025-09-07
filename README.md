# 🤖 AI Agents

A powerful AI-powered system with dual agents: **Database Agent** for SQL analysis and **RAG Agent** for document search. Built with NestJS, React, and FastAPI. Features sophisticated role-based permissions and natural language querying.

## 🏗️ Architecture

```
ai-agents/
├── apps/
│   ├── backend/         → NestJS (REST API Gateway)
│   ├── frontend/        → React + Tailwind CSS (Dual Agent Interface)
│   └── agent/           → FastAPI + LangGraph (Database + RAG Agents)
├── docker-compose.yml
├── README.md
```

## ✨ Features

### 🗄️ Database Agent

- **SQL Generation**: Natural language to SQL conversion using LangGraph
- **Database Analysis**: Query e-commerce data with AI insights
- **Customer Analytics**: Top customers, purchase patterns, product analysis
- **Real-time Queries**: Direct database interaction via LangGraph
- **SQL Information**: Detailed query execution information
- **Multi-step Reasoning**: Complex queries broken down into logical steps
- **Role-based Access**: Admin and Manager roles with different permission levels

### 📚 RAG Agent

- **Document Search**: Search through company documents and policies
- **Intelligent Retrieval**: Smart document matching with relevance scoring
- **Multiple Categories**: Policies, procedures, benefits, and general information
- **Source Attribution**: Shows which documents were used for answers
- **Public Access**: All employees can access company documents
- **Real-time Search**: Instant answers from document knowledge base

### 🔐 Role-Based Permissions

- **Employee**: Access to RAG Agent (company documents)
- **Manager**: Access to RAG Agent + basic database metrics
- **Admin**: Full access to both Database and RAG Agents

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ and pnpm
- Python 3.8+
- OpenAI API Key (for database agent)

### Installation

1. **Clone and install dependencies:**

```bash
git clone <repository>
cd ai-agents
pnpm install
```

2. **Install Python dependencies:**

```bash
# For AI Agents
cd apps/agent
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Running the System

1. **Set up environment variables:**

```bash
# Create .env file for AI agents
cd apps/agent
echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
echo "PORT=8000" >> .env
echo "HOST=0.0.0.0" >> .env
```

2. **Start the AI agents:**

```bash
cd apps/agent
source venv/bin/activate
python3 main.py
```

3. **Start the backend:**

```bash
cd apps/backend
pnpm run start:dev
```

4. **Start the frontend:**

```bash
cd apps/frontend
pnpm run dev
```

5. **Access the application:**

- Frontend: http://localhost:5173 (Dual Agent Interface)
- Backend API: http://localhost:3000
- AI Agents: http://localhost:8000

## 🤖 AI Models

### Supported Models

| Provider   | Models                            | Setup Required | Cost        |
| ---------- | --------------------------------- | -------------- | ----------- |
| **OpenAI** | gpt-3.5-turbo, gpt-4, gpt-4-turbo | API Key        | Pay-per-use |

### Model Setup

#### OpenAI

```bash
# Set your API key
export OPENAI_API_KEY=sk-your-key-here

# Or add to .env file
echo "OPENAI_API_KEY=sk-your-key-here" >> apps/agent/.env
```

## 📊 Database Schema

The system includes a mock e-commerce database with the following tables:

- **users**: Customer information
- **products**: Product catalog with categories
- **orders**: Order records with dates and amounts

Sample data includes orders from August and September 2025 for comprehensive analysis.

## 📚 Available Documents

The RAG Agent has access to 11 company documents across 4 categories:

### Policies

- Vacation Policy
- Remote Work Policy
- Code of Conduct

### Procedures

- Employee Onboarding Process
- Expense Reimbursement Procedure
- Performance Review Process

### Benefits

- Health Insurance Benefits
- Retirement Plan Benefits
- Professional Development Benefits

### General

- Company History
- Mission, Vision & Values

## 🔌 API Endpoints

### 🗄️ Database Agent

#### Chat with Database Agent

```bash
POST /chat/database
Authorization: Bearer test-token
{
  "message": "Which customer bought products from all categories?",
  "user_role": "admin"
}
```

Response:

```json
{
  "success": true,
  "response": "No customers have bought products from all available categories.",
  "timestamp": "2025-09-07T02:10:25.313749",
  "sql_info": {
    "queries_executed": [
      {
        "type": "custom_query",
        "description": "Custom database query",
        "sql_query": "SELECT ..."
      }
    ],
    "total_execution_time": 0,
    "queries_count": 1
  }
}
```

### 📚 RAG Agent

#### Chat with RAG Agent

```bash
POST /chat/rag
Authorization: Bearer test-token
{
  "message": "What is the vacation policy?"
}
```

Response:

```json
{
  "success": true,
  "response": "Based on the company documents, here's what I found about 'vacation policy'...",
  "timestamp": "2025-09-07T16:24:03.988685",
  "sources": [
    {
      "title": "Vacation Policy",
      "category": "policies",
      "relevance_score": 5
    }
  ]
}
```

#### Get Available Documents

```bash
GET /rag/documents
```

### System Health Check

```bash
GET /chat/health
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

### AI Agents

```bash
cd apps/agent
source venv/bin/activate
python3 main.py
```

## 🧪 Testing

### Test Database Agent

```bash
# Test database queries through NestJS
curl -X POST http://localhost:3000/chat/database \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test-token" \
  -d '{"message": "How many orders were made in August 2025?", "user_role": "admin"}'

# Test with different roles
curl -X POST http://localhost:3000/chat/database \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test-token" \
  -d '{"message": "What is the total revenue?", "user_role": "employee"}'
# Response: Access denied for employees
```

### Test RAG Agent

```bash
# Test document search
curl -X POST http://localhost:3000/chat/rag \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test-token" \
  -d '{"message": "What are the health insurance benefits?"}'

# Test available documents
curl -X GET http://localhost:3000/rag/documents
```

### Test AI Agents Directly

```bash
# Test database agent directly
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "How many customers do we have?", "user_role": "admin"}'

# Test RAG agent directly
curl -X POST http://localhost:8000/rag \
  -H "Content-Type: application/json" \
  -d '{"message": "vacation policy"}'
```

## 💡 Example Queries

### Database Agent Examples

- "How many orders were made in August 2025?"
- "What is the total revenue for September?"
- "Which customer spent the most money?"
- "How many products do we have in the Electronics category?"
- "Compare revenue between August and September"
- "What are the top 5 customers by total spending?"

### RAG Agent Examples

- "What is the vacation policy?"
- "How does the onboarding process work?"
- "What are the health insurance benefits?"
- "What is the company's mission?"
- "How do I submit an expense report?"
- "What is the remote work policy?"

## 🏗️ Tech Stack

- **Backend**: NestJS, TypeScript
- **Frontend**: React, Vite, Tailwind CSS
- **AI Agents**: FastAPI, LangGraph, Python
- **Database**: SQLite (with mock e-commerce data)
- **AI Models**: OpenAI GPT models
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

- [ ] Advanced RAG with vector embeddings
- [ ] Conversation history
- [ ] Advanced SQL query visualization
- [ ] Export functionality
- [ ] User authentication system
- [ ] Multi-user support
- [ ] API rate limiting
- [ ] WebSocket real-time updates
- [ ] Database schema visualization
- [ ] Query performance analytics
- [ ] Document upload interface
- [ ] Advanced search filters

## 🎯 Why This System?

- **Dual Agent Architecture**: Database analysis + Document search
- **Role-based Security**: Different access levels for different users
- **Natural Language Interface**: Ask questions in plain English
- **LangGraph Integration**: Multi-step reasoning for complex queries
- **Real-time Analytics**: Get instant insights from your data
- **Modern Architecture**: Clean separation between frontend, backend, and AI agents
- **Scalability**: Easy to add new features and data sources
- **Learning Platform**: Perfect for understanding AI agents and RAG systems
- **Open Source**: Full control over your AI system
- **Production Ready**: Built with enterprise-grade technologies

---

**Built with ❤️ using NestJS, React, FastAPI, and LangGraph**
