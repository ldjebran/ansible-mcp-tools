#!/bin/bash

# Ansible MCP Playbook Server Setup Script
# This script helps you set up the project with uv

set -e

echo "🚀 Setting up Ansible MCP Playbook Server with uv..."

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ uv is not installed. Please install uv first:"
    echo "   curl -LsSf https://astral.sh/uv/install.sh | sh"
    echo "   or visit: https://docs.astral.sh/uv/getting-started/installation/"
    exit 1
fi

echo "✅ uv is installed"

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo "❌ pyproject.toml not found. Please run this script from the project root directory."
    exit 1
fi

echo "✅ Project structure looks good"

# Install dependencies
echo "📦 Installing dependencies with uv..."
uv sync

echo "✅ Dependencies installed"

# Setup environment file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "⚙️ Creating .env file from template..."
    cp env.example .env
    echo "✅ Created .env file"
    echo "📝 Please edit .env with your Ansible configuration:"
    echo "   - ANSIBLE_BASE_URL: Your Ansible instance URL"
    echo "   - ANSIBLE_TOKEN: Your bearer token"
    echo "   - AAP_VERSION: Your AAP version (2.4 or other)"
else
    echo "✅ .env file already exists"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env with your Ansible details"
echo "2. Test connection: make test"
echo "3. Start server: make start"
echo ""
echo "Available commands:"
echo "  make help     - Show all available commands"
echo "  make test     - Test connection to Ansible"
echo "  make start    - Start the server"
echo "  make dev      - Start in development mode" 
