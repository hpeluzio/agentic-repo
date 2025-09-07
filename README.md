# 🤖 AI Agentic System

A powerful AI-powered system focused on database analysis using LangGraph. Built with NestJS, React, and FastAPI. Features a sophisticated database agent with SQL generation capabilities and natural language querying.

## 🏗️ Architecture

```
ai-agentic/
├── apps/
│   ├── backend/         → NestJS (REST API Gateway)
│   ├── frontend/        → React + Tailwind CSS (Database Chat Interface)
│   └── agent/           → FastAPI + LangGraph (Database Agent)
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

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ and pnpm
- Python 3.8+
- OpenAI API Key (for database agent)

### Installation

1. **Clone and install dependencies:**

```bash
git clone <repository>
cd agentic-repo
pnpm install
```

2. **Install Python dependencies:**

```bash
# For Database Agent
cd apps/agent
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Running the System

1. **Set up environment variables:**

```bash
# Create .env file for database agent
cd apps/agent
echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
echo "PORT=8000" >> .env
echo "HOST=0.0.0.0" >> .env
```

2. **Start the database agent:**

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

- Frontend: http://localhost:5173 (Database Chat Interface)
- Backend API: http://localhost:3000
- Database Agent: http://localhost:8000

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

- **customers**: Customer information
- **products**: Product catalog with categories
- **orders**: Order records with dates and amounts
- **order_items**: Individual items within orders

Sample data is automatically loaded when the agent starts.

## 🔌 API Endpoints

### 🗄️ Database Agent

#### Chat with Database Agent

```bash
POST /chat/database
Authorization: Bearer test-token
{
  "message": "Which customer bought products from all categories?"
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

### 📚 RAG Agent (Coming Soon)

#### Chat with RAG Agent

```bash
POST /chat/rag
Authorization: Bearer test-token
{
  "message": "What is the main topic of the documents?"
}
```

### System Health Check

```bash
POST /chat/health
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

### Database Agent

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
  -d '{"message": "How many orders were made in September 2025?"}'

# Test RAG agent (placeholder)
curl -X POST http://localhost:3000/chat/rag \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test-token" \
  -d '{"message": "What is the main topic?"}'

# Test health check
curl -X POST http://localhost:3000/chat/health
```

### Test Database Agent Directly

```bash
# Test database agent directly (bypassing NestJS)
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "How many customers do we have?"}'
```

## 💡 Example Queries

### Database Agent Examples

- "Which customer bought products from all categories?"
- "How many orders were made in September 2025?"
- "What are the top 5 customers who spent the most?"
- "How many products do we have in the Electronics category?"
- "Who bought an iPhone?"
- "What is the most expensive product?"

### Advanced Database Queries

- "Show me the customer with the highest total spending"
- "What products are most popular in each category?"
- "Find customers who haven't made any orders"
- "Calculate the average order value by month"

## 🏗️ Tech Stack

- **Backend**: NestJS, TypeScript
- **Frontend**: React, Vite, Tailwind CSS
- **Database Agent**: FastAPI, LangGraph, Python
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

- [ ] RAG (Retrieval-Augmented Generation) for document processing
- [ ] Conversation history
- [ ] Advanced SQL query visualization
- [ ] Export functionality
- [ ] User authentication
- [ ] Multi-user support
- [ ] API rate limiting
- [ ] WebSocket real-time updates
- [ ] Database schema visualization
- [ ] Query performance analytics

## 🎯 Why This System?

- **Database Intelligence**: Natural language to SQL conversion with AI
- **LangGraph Integration**: Multi-step reasoning for complex queries
- **Real-time Analytics**: Get instant insights from your data
- **Modern Architecture**: Clean separation between frontend, backend, and AI agent
- **Scalability**: Easy to add new features and database connections
- **Learning Platform**: Perfect for understanding AI agents and database interactions
- **Open Source**: Full control over your AI system
- **Production Ready**: Built with enterprise-grade technologies

---

**Built with ❤️ using NestJS, React, FastAPI, and LangGraph**
