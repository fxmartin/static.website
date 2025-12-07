# Docker Deployment Guide for m4rt1n.eu

This guide covers deploying the static website to a Hetzner VM using Docker with automatic updates from the Git repository.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Hetzner VM                          │
│  ┌───────────────────────────────────────────────────┐  │
│  │              Docker Container                      │  │
│  │  ┌─────────────┐    ┌────────────────────────┐   │  │
│  │  │   nginx     │    │   Static Files (/out)  │   │  │
│  │  │   :80       │───▶│   - index.html         │   │  │
│  │  └─────────────┘    │   - CSS/JS/Images      │   │  │
│  │                     └────────────────────────┘   │  │
│  └───────────────────────────────────────────────────┘  │
│                           ▲                             │
│                           │ rebuild on changes          │
│  ┌───────────────────────────────────────────────────┐  │
│  │   Cron Job (every 15 min)                         │  │
│  │   └── deploy.sh (git pull → docker build)         │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

## Quick Start (Automated Setup)

### 1. Provision Hetzner VM

- Create a VM with Ubuntu 22.04 LTS
- Minimum specs: 1 vCPU, 2GB RAM, 20GB SSD
- Open port 80 (HTTP) and optionally 443 (HTTPS)

### 2. Run Setup Script

SSH into your VM and run:

```bash
# Download and run setup script
curl -fsSL https://raw.githubusercontent.com/YOUR_USERNAME/static.website/main/scripts/setup-vm.sh -o setup-vm.sh

# Edit the script to set your repository URL
nano setup-vm.sh
# Change REPO_URL to your actual repository

# Run setup
chmod +x setup-vm.sh
sudo REPO_URL="https://github.com/YOUR_USERNAME/static.website.git" ./setup-vm.sh
```

The script will:
- Install Docker and Docker Compose
- Clone your repository
- Build and start the container
- Set up a cron job for auto-updates every 15 minutes

## Manual Setup

### 1. Install Docker

```bash
# Install Docker
curl -fsSL https://get.docker.com | sh
systemctl enable docker
systemctl start docker

# Install Docker Compose plugin
apt-get install -y docker-compose-plugin
```

### 2. Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/static.website.git /opt/static.website
cd /opt/static.website
```

### 3. Build and Run

```bash
# Build the Docker image
docker compose build

# Start the container
docker compose up -d

# Check status
docker compose ps
docker compose logs -f
```

## Auto-Update Options

### Option A: Cron Job (Recommended)

Set up a cron job to check for updates periodically:

```bash
# Edit crontab
crontab -e

# Add this line (checks every 15 minutes)
*/15 * * * * cd /opt/static.website && ./scripts/deploy.sh >> /var/log/website-deploy.log 2>&1
```

### Option B: GitHub Webhook

For instant updates on push:

1. Start the webhook server:
```bash
# Install webhook tool
apt-get install -y webhook

# Set a secret for security
export WEBHOOK_SECRET="your-secret-here"

# Run webhook server (use systemd for production)
./scripts/webhook-server.sh 9000
```

2. Configure GitHub webhook:
   - Go to your repo → Settings → Webhooks → Add webhook
   - Payload URL: `http://your-server:9000/hooks/deploy`
   - Content type: `application/json`
   - Secret: your-secret-here
   - Events: Just the push event

### Option C: GitHub Actions (CI/CD)

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Hetzner

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Deploy via SSH
        uses: appleboy/ssh-action@v1
        with:
          host: ${{ secrets.HOST }}
          username: ${{ secrets.USERNAME }}
          key: ${{ secrets.SSH_KEY }}
          script: |
            cd /opt/static.website
            ./scripts/deploy.sh
```

## Commands Reference

```bash
# View running containers
docker compose ps

# View logs
docker compose logs -f

# Restart container
docker compose restart

# Rebuild and restart
docker compose up -d --build

# Stop container
docker compose down

# Manual deployment
./scripts/deploy.sh

# Check deployment logs
tail -f /var/log/website-deploy.log
```

## Adding HTTPS with Let's Encrypt

For production, add HTTPS using Caddy as a reverse proxy:

```bash
# Install Caddy
apt-get install -y debian-keyring debian-archive-keyring apt-transport-https
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | tee /etc/apt/sources.list.d/caddy-stable.list
apt-get update
apt-get install caddy

# Configure Caddy
cat > /etc/caddy/Caddyfile << EOF
m4rt1n.eu {
    reverse_proxy localhost:80
}
EOF

# Restart Caddy
systemctl restart caddy
```

Caddy automatically obtains and renews Let's Encrypt certificates.

## Troubleshooting

### Container won't start
```bash
# Check logs
docker compose logs

# Check if port 80 is in use
netstat -tlnp | grep :80
```

### Build fails
```bash
# Rebuild without cache
docker compose build --no-cache

# Check disk space
df -h
```

### Updates not working
```bash
# Check cron logs
grep CRON /var/log/syslog

# Run deploy manually to see errors
./scripts/deploy.sh
```

## Resource Usage

Expected resource consumption:
- **Disk**: ~500MB (image + node_modules during build)
- **RAM**: ~20MB (nginx is very lightweight)
- **CPU**: Minimal (static file serving)

This makes it suitable for the smallest Hetzner VM (CX11).
