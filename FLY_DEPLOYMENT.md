# Fly.io Deployment Guide

This guide explains how to deploy the Audience Agent to Fly.io with proper configuration and secrets management.

## Prerequisites

1. Install the Fly CLI:
```bash
curl -L https://fly.io/install.sh | sh
```

2. Sign up/login to Fly.io:
```bash
fly auth login
```

## Initial Setup

The fly.toml file has already been created. Review the configuration:
- App name: `audience-agent`
- Region: `fra` (Frankfurt)
- Memory: 1GB
- Auto-stop enabled to save costs

## Configuration and Secrets

### Option 1: Using Fly Secrets (Recommended for Production)

1. Set your Gemini API key as a secret:
```bash
fly secrets set GEMINI_API_KEY="your-gemini-api-key-here"
```

2. Set Index Exchange credentials (if using):
```bash
fly secrets set IX_USERNAME="your-ix-username"
fly secrets set IX_PASSWORD="your-ix-password"
```

3. Set LiveRamp credentials (if using):
```bash
fly secrets set LIVERAMP_CLIENT_ID="your-liveramp-client-id"
fly secrets set LIVERAMP_CLIENT_SECRET="your-liveramp-client-secret"
```

3. Update the application to read from environment variables. Create a file `config_loader.py`:
```python
import os
import json

def load_config():
    """Load config with environment variable overrides."""
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    # Override with environment variables if present
    if gemini_key := os.environ.get('GEMINI_API_KEY'):
        config['gemini_api_key'] = gemini_key
    
    if ix_username := os.environ.get('IX_USERNAME'):
        config['platforms']['index-exchange']['username'] = ix_username
    
    if ix_password := os.environ.get('IX_PASSWORD'):
        config['platforms']['index-exchange']['password'] = ix_password
    
    return config
```

### Option 2: Build-time Configuration

1. Create a production config file locally:
```bash
cp config.json.sample config.prod.json
# Edit config.prod.json with your actual credentials
```

2. Update Dockerfile to use production config:
```dockerfile
# Replace the config copy line with:
COPY config.prod.json config.json
```

3. **Important**: Add `config.prod.json` to `.gitignore` to avoid committing secrets:
```bash
echo "config.prod.json" >> .gitignore
```

## Deployment Steps

1. Deploy the application:
```bash
fly deploy
```

2. Check deployment status:
```bash
fly status
```

3. View logs:
```bash
fly logs
```

4. SSH into the running container (for debugging):
```bash
fly ssh console
```

## Unified Server Setup

The server now supports both MCP and A2A protocols on a single HTTP endpoint, providing maximum flexibility for different client types.

### How it Works

The Dockerfile runs a unified FastAPI server:
```dockerfile
CMD ["uvicorn", "unified_server:app", "--host", "0.0.0.0", "--port", "8000"]
```

This provides:
- **Dual Protocol Support**: Both MCP (JSON-RPC) and A2A (REST) on one server
- **Direct Web Access**: Accessible via HTTP on port 8000
- **Protocol Endpoints**:
  - `/mcp` - MCP JSON-RPC endpoint
  - `/a2a/task` - A2A task execution endpoint
  - `/agent-card` - A2A agent capabilities
  - `/health` - Health check for both protocols

### Accessing the Server

Once deployed, your unified server will be available at:
```
https://audience-agent.fly.dev
```

Clients can connect using:
- **MCP Clients**: Send JSON-RPC requests to `https://audience-agent.fly.dev/mcp`
- **A2A Clients**: Send task requests to `https://audience-agent.fly.dev/a2a/task`
- **Health Monitoring**: Check `https://audience-agent.fly.dev/health`

### Testing the Deployment

Test MCP protocol:
```bash
curl -X POST https://audience-agent.fly.dev/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "method": "tools/list", "id": 1}'
```

Test A2A protocol:
```bash
curl https://audience-agent.fly.dev/agent-card
```

### Health Checks

Fly.io will automatically monitor the `/health` endpoint which returns:
```json
{
  "status": "healthy",
  "protocols": ["mcp", "a2a"],
  "timestamp": "2025-08-05T12:00:00Z"
}
```

## Managing Multiple Environments

### Development
```bash
# Use config.json locally
cp config.json.sample config.json
# Edit with test credentials
```

### Staging
```bash
fly deploy --app audience-agent-staging
fly secrets set GEMINI_API_KEY="staging-key" --app audience-agent-staging
```

### Production
```bash
fly deploy --app audience-agent
fly secrets set GEMINI_API_KEY="production-key" --app audience-agent
```

## Security Best Practices

1. **Never commit secrets to git**
   - Use environment variables via `fly secrets`
   - Add sensitive files to `.gitignore`

2. **Rotate credentials regularly**
   ```bash
   fly secrets set GEMINI_API_KEY="new-key-value"
   ```

3. **Use different credentials per environment**
   - Development: Test credentials
   - Staging: Separate staging credentials
   - Production: Production-only credentials

4. **Monitor access**
   ```bash
   fly logs | grep "authentication"
   ```

## Updating Configuration

To update configuration without redeploying:

1. For secrets:
```bash
fly secrets set KEY="new-value"
# This will restart the app automatically
```

2. For non-secret config changes:
```bash
# SSH into the container
fly ssh console

# Edit config file
vi config.json

# Restart the app
fly apps restart
```

## Troubleshooting

1. **App won't start**: Check logs for missing config
```bash
fly logs
```

2. **Authentication failures**: Verify secrets are set
```bash
fly secrets list
```

3. **Database issues**: The SQLite database is ephemeral. For production, consider:
   - Using Fly Volumes for persistence
   - Migrating to PostgreSQL

## Cost Optimization

The current configuration uses:
- Auto-stop machines (stops when idle)
- Minimal resources (1GB RAM, shared CPU)
- Single region deployment

To further optimize:
```toml
[http_service]
  min_machines_running = 0  # Scale to zero when idle
  auto_stop_machines = 'stop'
  auto_start_machines = true
```

## Next Steps

1. Set up monitoring:
```bash
fly logs --tail
```

2. Configure alerts:
   - Set up Fly.io monitoring
   - Add health check endpoints

3. Scale as needed:
```bash
fly scale count 2  # Run 2 instances
fly scale memory 2048  # Increase to 2GB RAM
```