# Configuration Directory

This directory contains all project configuration files.

## Files

### Agent Configuration
- `.agent-config.json` - Multi-agent configuration and coordination settings
- `.agent-*.id` - Agent identification files (4 files, one per agent)

### Cursor Rules
- `.cursorrules` - Global cursor rules for the project (base rules)
- `.cursorrules-backend.md` - Backend development rules
- `.cursorrules-database.md` - Database/scripts development rules
- `.cursorrules-frontend.md` - Frontend development rules
- `.cursorrules-frontend-uiux.md` - Frontend UI/UX development rules
- `.cursorrules-fullstack.md` - Full-stack engineering rules
- `.cursorrules-uiux.md` - UI/UX design rules

### Infrastructure
- `docker-compose.yml` - PostgreSQL service configuration

## Usage

### Agent Configuration
Agents should read their configuration from:
- Agent ID: `config/.agent-[N].id`
- Agent config: `config/.agent-config.json`
- Rules file: `config/.cursorrules-[role].md`

### Docker Compose
Run from project root:
```bash
docker-compose -f config/docker-compose.yml up -d
```

Or create a symlink at root for convenience:
```bash
ln -s config/docker-compose.yml docker-compose.yml
```

