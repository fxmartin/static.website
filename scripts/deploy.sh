#!/bin/bash
# deploy.sh - Auto-update and deploy script for m4rt1n.eu
# Run this script to pull latest changes and rebuild the container

set -e

# Configuration
REPO_DIR="${REPO_DIR:-/opt/static.website}"
BRANCH="${BRANCH:-main}"
COMPOSE_FILE="docker-compose.yml"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1"
    exit 1
}

cd "$REPO_DIR" || error "Failed to change to repository directory: $REPO_DIR"

log "Fetching latest changes from origin..."
git fetch origin "$BRANCH"

# Check if there are updates
LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse "origin/$BRANCH")

if [ "$LOCAL" = "$REMOTE" ]; then
    log "Already up to date. No deployment needed."
    exit 0
fi

log "Updates found! Local: ${LOCAL:0:7} -> Remote: ${REMOTE:0:7}"

# Pull changes
log "Pulling latest changes..."
git pull origin "$BRANCH"

# Rebuild and restart container
log "Rebuilding Docker container..."
docker compose -f "$COMPOSE_FILE" build --no-cache

log "Restarting container..."
docker compose -f "$COMPOSE_FILE" up -d

# Cleanup old images
log "Cleaning up old Docker images..."
docker image prune -f

log "Deployment complete! Site updated to commit ${REMOTE:0:7}"

# Show container status
docker compose -f "$COMPOSE_FILE" ps
