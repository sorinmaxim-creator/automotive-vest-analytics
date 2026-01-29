#!/bin/bash
set -e

SERVER="serveradrvesta1"
REMOTE_DIR="/home/sorin/automotive-vest-analytics"

echo "=== Deploying to $SERVER ==="

# 1. Create directory on server
echo "Creating remote directory..."
ssh $SERVER "mkdir -p $REMOTE_DIR/nginx"

# 2. Sync Files
echo "Syncing files..."
# We use rsync to copy specific files/folders
rsync -avz --progress \
    --exclude 'venv' \
    --exclude '__pycache__' \
    --exclude '.git' \
    --exclude '.env' \
    docker-compose.yml \
    docker-compose.prod.yml \
    Dockerfile \
    Dockerfile.frontend \
    requirements.txt \
    .env.example \
    app \
    frontend \
    scripts \
    data \
    nginx \
    nginx/host_adr_nginx.conf \
    $SERVER:$REMOTE_DIR

# 3. Create .env on server if not exists
echo "Configuring environment..."
ssh $SERVER "if [ ! -f $REMOTE_DIR/.env ]; then cp $REMOTE_DIR/.env.example $REMOTE_DIR/.env; fi"
ssh $SERVER "grep -q 'DB_PORT=' $REMOTE_DIR/.env || echo 'DB_PORT=5433' >> $REMOTE_DIR/.env"
ssh $SERVER "grep -q 'API_PORT=' $REMOTE_DIR/.env || echo 'API_PORT=8001' >> $REMOTE_DIR/.env"
ssh $SERVER "grep -q 'FRONTEND_PORT=' $REMOTE_DIR/.env || echo 'FRONTEND_PORT=8502' >> $REMOTE_DIR/.env"
ssh $SERVER "grep -q 'NGINX_PORT=' $REMOTE_DIR/.env || echo 'NGINX_PORT=8080' >> $REMOTE_DIR/.env"


# 4. Run Docker Compose
echo "Starting services..."
ssh $SERVER "cd $REMOTE_DIR && docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build"

# 5. Run Migrations
echo "Running database migrations..."
# Update: Use the right path and set PYTHONPATH
ssh $SERVER "cd $REMOTE_DIR && docker compose -f docker-compose.yml -f docker-compose.prod.yml exec -T api bash -c 'export PYTHONPATH=/app && python scripts/seed_database.py'"

echo "=== Deployment Complete ==="
echo "Check status: ssh $SERVER 'cd automotive-vest-analytics && docker compose ps'"
echo "App should be available at: http://adr.vestpolicylab.org (if NGINX_PORT is 80) or http://adr.vestpolicylab.org:NGINX_PORT"
