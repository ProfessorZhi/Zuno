# Zuno

Zuno is an agent workspace platform for building and running AI assistants with a unified capability layer.

It combines agent execution, MCP integration, skills, tools, knowledge base retrieval, and desktop runtime into one system across Web and Electron clients.

## Core Features

### Workspace

- Chat mode
- Agent mode
- Terminal / local execution mode
- Session history and context persistence
- Attachment support for images, PDF, Word, PPT, TXT, Markdown and Excel

### MCP

- Built-in and custom MCP server management
- `STDIO` and `Streamable HTTP` support
- Connection testing and tool discovery
- User-level configuration for credential-based services
- Unified MCP configuration interface

### Skills, Tools and Knowledge

- Skill binding and execution
- Built-in tool management
- Custom tool integration
- Knowledge base upload, parsing, indexing and retrieval
- Retrieval-augmented answering

### Desktop Runtime

- Electron desktop client
- Local startup / stop / rebuild workflow
- Integration with local files and execution environment

## Tech Stack

### Backend

- Python
- FastAPI
- LangChain
- LangGraph
- SQLModel
- MCP runtime and adapters
- RAG pipeline

### Frontend

- Vue 3
- TypeScript
- Vite
- Element Plus

### Desktop

- Electron
- Node.js

### Infrastructure

- MySQL
- Redis
- MinIO
- Docker

## Repository Structure

```text
Zuno/
|-- src/
|   |-- backend/      # FastAPI backend, agent runtime, MCP, RAG
|   `-- frontend/     # Vue-based console and workspace UI
|-- desktop/          # Electron client
|-- docker/           # Docker deployment files
|-- docs/             # Project documentation
|-- scripts/          # Startup / stop / rebuild scripts
|-- cli_tools/        # Local CLI tool directory
`-- README.md
```

## Getting Started

### Run services separately

Backend:

```bash
cd src/backend
python -m agentchat.main
```

Frontend:

```bash
cd src/frontend
npm install
npm run dev
```

Desktop:

```bash
cd desktop
npm install
npm run dev
```

### Run with scripts

Windows helper scripts are included in `scripts/`:

- `zuno-start.bat`
- `zuno-stop.bat`
- `zuno-rebuild-start.bat`
- `zuno-clean-rebuild-start.bat`

### Run with Docker

```bash
cd docker
docker compose up -d
```

## Documentation

- Repository: <https://github.com/ProfessorZhi/Zuno>
- Docs directory: [docs](./docs)

## License

MIT
