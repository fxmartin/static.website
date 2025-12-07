#!/bin/bash
# setup-vm.sh - Initial setup script for Hetzner VM
# Run this once on a fresh Ubuntu/Debian VM

set -e

# Configuration
REPO_URL="${REPO_URL:-https://github.com/YOUR_USERNAME/static.website.git}"
REPO_DIR="/opt/static.website"
BRANCH="${BRANCH:-main}"
CRON_SCHEDULE="${CRON_SCHEDULE:-*/15 * * * *}"  # Every 15 minutes

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[SETUP]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[SETUP]${NC} $1"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root (sudo ./setup-vm.sh)"
    exit 1
fi

log "Updating system packages..."
apt-get update
apt-get upgrade -y

log "Installing Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com | sh
    systemctl enable docker
    systemctl start docker
else
    log "Docker already installed"
fi

log "Installing Docker Compose plugin..."
apt-get install -y docker-compose-plugin

log "Installing Git..."
apt-get install -y git

log "Cloning repository..."
if [ -d "$REPO_DIR" ]; then
    warn "Repository directory exists, pulling latest..."
    cd "$REPO_DIR"
    git pull origin "$BRANCH"
else
    git clone -b "$BRANCH" "$REPO_URL" "$REPO_DIR"
fi

cd "$REPO_DIR"

log "Making scripts executable..."
chmod +x scripts/*.sh

log "Building and starting Docker container..."
docker compose up -d --build

log "Setting up cron job for auto-updates..."
CRON_CMD="cd $REPO_DIR && ./scripts/deploy.sh >> /var/log/website-deploy.log 2>&1"
CRON_LINE="$CRON_SCHEDULE $CRON_CMD"

# Add cron job if not exists
(crontab -l 2>/dev/null | grep -v "deploy.sh"; echo "$CRON_LINE") | crontab -

log "Creating log file..."
touch /var/log/website-deploy.log
chmod 644 /var/log/website-deploy.log

log "Setup complete!"
echo ""
echo "=========================================="
echo "Website is now running on port 80"
echo "Auto-update cron: $CRON_SCHEDULE"
echo "Logs: /var/log/website-deploy.log"
echo ""
echo "To manually trigger deployment:"
echo "  cd $REPO_DIR && ./scripts/deploy.sh"
echo ""
echo "To view container logs:"
echo "  docker compose logs -f"
echo "=========================================="
