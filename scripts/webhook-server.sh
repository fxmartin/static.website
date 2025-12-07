#!/bin/bash
# webhook-server.sh - Simple webhook server for GitHub webhooks
# This provides an alternative to cron-based updates
#
# Usage: ./webhook-server.sh [port]
# Default port: 9000
#
# Configure GitHub webhook:
#   URL: http://your-server:9000/webhook
#   Content type: application/json
#   Events: Push events

PORT="${1:-9000}"
REPO_DIR="${REPO_DIR:-/opt/static.website}"
SECRET="${WEBHOOK_SECRET:-}"  # Set this for security

log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

# Check if webhook tool is installed
if ! command -v webhook &> /dev/null; then
    echo "Installing webhook tool..."
    apt-get update && apt-get install -y webhook
fi

# Create webhook configuration
HOOKS_FILE="/tmp/hooks.json"
cat > "$HOOKS_FILE" << EOF
[
  {
    "id": "deploy",
    "execute-command": "$REPO_DIR/scripts/deploy.sh",
    "command-working-directory": "$REPO_DIR",
    "response-message": "Deployment triggered",
    "trigger-rule": {
      "match": {
        "type": "payload-hmac-sha256",
        "secret": "$SECRET",
        "parameter": {
          "source": "header",
          "name": "X-Hub-Signature-256"
        }
      }
    }
  }
]
EOF

# If no secret, use simpler config
if [ -z "$SECRET" ]; then
    cat > "$HOOKS_FILE" << EOF
[
  {
    "id": "deploy",
    "execute-command": "$REPO_DIR/scripts/deploy.sh",
    "command-working-directory": "$REPO_DIR",
    "response-message": "Deployment triggered"
  }
]
EOF
    log "WARNING: Running without webhook secret. Set WEBHOOK_SECRET for security."
fi

log "Starting webhook server on port $PORT..."
log "Webhook URL: http://your-server:$PORT/hooks/deploy"

webhook -hooks "$HOOKS_FILE" -port "$PORT" -verbose
