# OMNIAI - Autonomous AI Agent System

A production-style autonomous AI agent that can plan, execute, remember, and generate applications.

## 🚀 Features

- **Autonomous Planning**: Breaks down goals into executable steps using LLM
- **Tool Execution**: Routes tasks to appropriate tools (calculator, file writer, app builder)
- **Persistent Memory**: SQLite-backed memory system to store goals, steps, and results
- **App Generation**: Creates simple HTML/CSS/JS applications on-demand
- **FastAPI Backend**: RESTful API for agent orchestration
- **Web Dashboard**: Simple frontend interface for interaction
- **Token Authentication**: Basic security with API token validation

## ⚙️ Tech Stack

- Python 3.11+
- FastAPI & Uvicorn
- SQLite
- OpenAI API (HTTP requests)
- Vanilla HTML/CSS/JavaScript frontend

## 📁 Project Structure

```
OMMIAI/
├── backend/
│   ├── __init__.py
│   ├── main.py              # FastAPI server entry point
│   ├── agent.py             # Core autonomous agent loop
│   ├── planner.py           # LLM-based planning module
│   ├── tools.py             # Tool router and implementations
│   ├── builder.py           # Web app generator
│   ├── memory.py            # SQLite memory system
│   ├── config.py            # Configuration and settings
│   ├── auth.py              # Token authentication
│   └── utils.py             # Helper functions and logging
├── frontend/
│   ├── index.html           # Dashboard UI
│   ├── app.js               # Frontend logic
│   └── style.css            # Styling
├── sandbox/
│   └── apps/                # Generated applications
├── data/
│   └── memory.db            # SQLite database (created at runtime)
├── requirements.txt
├── README.md
└── .env.example
```

## 🚀 Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/eclipsek79/OMNIAI.git
cd OMNIAI
```

### 2. Create and activate virtual environment
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment
```bash
cp .env.example .env
# Edit .env and optionally add your OpenAI API key for LLM planning
```

### 5. Run the server
```bash
uvicorn backend.main:app --reload
```

The server will start at `http://localhost:8000`

### 6. Access the dashboard

**Option A: Open frontend directly**
```bash
# In another terminal, serve the frontend:
python3 -m http.server 8080 --directory .
# Then visit http://localhost:8080/frontend/index.html
```

**Option B: Modify frontend for CORS or use proxy**
The default frontend tries to call `/run` at the same origin. When running uvicorn on port 8000, update the fetch URL if needed or use a reverse proxy.

**Option C: Use curl to test API directly**
```bash
curl -X POST "http://localhost:8000/run" \
  -H "Content-Type: application/json" \
  -H "Authorization: 1234" \
  -d '{"goal":"Create a simple todo app"}'
```

## 🌐 API Endpoints

### Health Check
```http
GET /
```

Response:
```json
{
  "status": "OMNIAI running"
}
```

### Run Agent
```http
POST /run
Authorization: 1234
Content-Type: application/json

{
  "goal": "Create a todo app"
}
```

Response:
```json
{
  "goal": "Create a todo app",
  "steps": ["Step 1", "Step 2", ...],
  "results": ["Result 1", "Result 2", ...],
  "details": [{"step": "...", "tool": "...", "result": "..."}, ...],
  "recent_memory": [{...}, ...],
  "success": true
}
```

### Get Memory
```http
GET /memory
Authorization: 1234
```

Response:
```json
{
  "memory": [last 20 entries from SQLite]
}
```

## 🧠 How It Works

1. **User submits a goal** via POST /run with an Authorization token
2. **Planner module** uses OpenAI (if configured) or heuristics to break goal into steps
3. **Agent loop** executes each step sequentially
4. **Tool router** selects appropriate tool based on step content:
   - `calculator`: Safe arithmetic evaluation
   - `file_writer`: Write content to sandbox files
   - `app_builder`: Generate interactive HTML/CSS/JS apps
   - `echo`: Default fallback for unmatched steps
5. **Memory system** persists each step and result to SQLite
6. **Results** returned as structured JSON with all steps, results, and recent memory
7. **Generated apps** saved to sandbox/apps/<slug>/

## 🧰 Available Tools

### Calculator
Evaluates safe mathematical expressions (supports +, -, *, /, **, parentheses, mod).

**Triggered by**: Step containing "calculate", "compute", or math operators

### File Writer
Writes content to files within the sandbox directory (prevents path traversal).

**Triggered by**: Step containing "write file", "create file", "save to", "write to"

### App Builder
Generates a simple interactive todo-like app with HTML, CSS, and JavaScript.

**Triggered by**: Step containing "build" and "app"

## 🔐 Security

- **Token Authentication**: Simple bearer token validation (default: `1234`)
- **Path Validation**: File writer prevents path traversal attacks
- **Safe Math**: Calculator uses AST parsing instead of eval()
- **Sandboxed Output**: Generated apps stored in isolated sandbox/apps directory

## 📝 Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | (none) | OpenAI API key for LLM planning |
| `OPENAI_MODEL` | `gpt-4o-mini` | OpenAI model to use |
| `AUTH_TOKEN` | `1234` | API authentication token |
| `DATABASE_PATH` | `data/memory.db` | SQLite database location |
| `SANDBOX_DIR` | `sandbox/apps` | Directory for generated apps |
| `HTTP_TIMEOUT` | `15` | Timeout for HTTP requests (seconds) |
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |

## 🛠️ Development

### Run with auto-reload
```bash
uvicorn backend.main:app --reload
```

### Run in production
```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

### Run tests (if added)
```bash
python -m pytest
```

## 📚 Example Usage

### Via API
```bash
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -H "Authorization: 1234" \
  -d '{
    "goal": "Calculate the area of a circle with radius 5 and then build a simple calculator app"
  }'
```

### Via Frontend Dashboard
1. Open `frontend/index.html` in browser
2. Enter goal: "Build a weather dashboard"
3. Set token to `1234`
4. Click "Run Agent"
5. View results and check `sandbox/apps/` for generated app

## 🔄 Memory Storage

All steps and results are persisted to SQLite with the following schema:

```sql
CREATE TABLE memory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    goal TEXT,
    step TEXT,
    result TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

Query recent memory:
```bash
sqlite3 data/memory.db "SELECT goal, step, result FROM memory ORDER BY id DESC LIMIT 10;"
```

## 🐛 Troubleshooting

### Port 8000 already in use
```bash
uvicorn backend.main:app --reload --port 8001
```

### OpenAI API errors
If planning fails due to missing/invalid API key, the planner automatically falls back to heuristic-based splitting. No error is raised.

### Database locked
If you get "database is locked" errors, ensure only one uvicorn process is running. Kill any orphaned processes:
```bash
lsof -i :8000
kill -9 <PID>
```

### CORS errors in frontend
If the frontend can't reach the API, ensure:
1. Uvicorn is running on localhost:8000
2. Frontend is served from the same origin or configure CORS (already enabled in main.py)

## 📄 License

MIT License - feel free to use and modify

## 🤝 Contributing

Contributions welcome! This is a minimal autonomous agent demo. Ideas for extensions:
- Web scraping tool
- Database query tool
- Code execution tool (sandboxed)
- Image generation tool
- Multi-step planning with feedback loops
- Persistent conversation memory across sessions

---

**Built with ❤️ by eclipsek79**
