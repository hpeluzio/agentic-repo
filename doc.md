Perfeito, Henrique! Vamos seguir com a estrutura **monorepo com 3 apps**: `backend` (NestJS), `frontend` (React), e `llama-bridge` (Python com LlamaIndex + Chroma).

---

## 🏗️ Estrutura final do monorepo:

```
ai-agentic/
├── apps/
│   ├── backend/         → NestJS (REST que chama o script Python)
│   ├── frontend/        → React + Tailwind
│   └── llama-bridge/    → Python (LlamaIndex, Chroma)
├── docker-compose.yml
├── README.md
```

---

## ✅ Comandos para criar o projeto do zero

### 📁 1. Crie o diretório do monorepo

```bash
mkdir ai-agentic && cd ai-agentic
mkdir -p apps/{backend,frontend,llama-bridge}
```

---

## 🔧 2. BACKEND - NestJS

```bash
cd apps/backend
npm i -g @nestjs/cli
nest new . --package-manager npm
```

> Ao ser perguntado sobre a estrutura, escolha **"REST API"** (não GraphQL) e selecione "npm" como gerenciador.

---

### Crie o módulo do agente

```bash
nest generate module agent
nest generate controller agent
nest generate service agent
```

> Depois, vamos editar os arquivos com a lógica que te mostrei antes (`agent.service.ts`, etc.)

---

## 🎨 3. FRONTEND - React + Vite + Tailwind

```bash
cd ../frontend
npm create vite@latest . -- --template react-ts
npm install
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

### Configure o Tailwind

No `tailwind.config.js`:

```js
content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"]
```

No `src/index.css`:

```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

---

## 🐍 4. LLAMA-BRIDGE - Python

```bash
cd ../llama-bridge
python3 -m venv venv
source venv/bin/activate  # Mac/Linux
# venv\Scripts\activate   # Windows

pip install llama-index chromadb openai
touch query_engine.py
```

> Depois edite `query_engine.py` com o código que te mostrei anteriormente.

---

## 🐳 5. docker-compose.yml (raiz do monorepo)

Crie esse arquivo na raiz:

```yaml
version: "3.9"
services:
  backend:
    build: ./apps/backend
    ports:
      - "3000:3000"
    volumes:
      - ./apps/backend:/app
    env_file:
      - ./apps/backend/.env

  frontend:
    build: ./apps/frontend
    ports:
      - "5173:5173"
    volumes:
      - ./apps/frontend:/app

  llama:
    build: ./apps/llama-bridge
    volumes:
      - ./apps/llama-bridge:/app
```

---

## 📝 6. .env (no `backend/`)

```env
OPENAI_API_KEY=sk-...
```

---

## 🧪 7. Teste Localmente

### Backend:

```bash
cd apps/backend
npm run start:dev
```

### Frontend:

```bash
cd apps/frontend
npm run dev
```

### Python:

```bash
cd apps/llama-bridge
source venv/bin/activate
python query_engine.py "Qual é o conteúdo do documento?"
```

---

## ✅ Pronto!

Quer que eu:

1. **Te gere os arquivos de forma automática em ZIP**, já com tudo isso pronto?
2. Ou você quer montar manualmente e ir me pedindo parte por parte?

Posso seguir como preferir.
