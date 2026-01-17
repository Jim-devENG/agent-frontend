#!/bin/bash
# Script to run database migration on Render
# This will be executed automatically on deployment

echo "Applying database migrations..."
cd /opt/render/project/src/backend || cd backend
alembic upgrade head
echo "✅ Migrations applied successfully!"

