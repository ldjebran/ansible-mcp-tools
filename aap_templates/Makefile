UV_ENV_FILE ?= .env
export UV_ENV_FILE
.PHONY: help install run dev clean test test-connection demo-pagination

# Default target
help:
	@echo "Ansible MCP Playbook Server - Available commands:"
	@echo "  install         Install dependencies with uv"
	@echo "  run             Run the MCP server"
	@echo "  dev             Run the server in development mode"
	@echo "  clean           Clean up cache files"
	@echo "  test            Test the server connection"
	@echo "  test-connection Test Ansible connection and list templates"
	@echo "  demo-pagination Demonstrate pagination with different page sizes"
	@echo "  deps            Check and install dependencies"
	@echo ""
	@echo "UV-specific commands:"
	@echo "  uv-sync    Sync dependencies with uv"
	@echo "  uv-sync-dev Sync dependencies with uv (including dev)"
	@echo "  uv-add     Show how to add new dependencies"
	@echo "  uv-add-dev Show how to add new dev dependencies"

# Install dependencies
install:
	@echo "📦 Installing dependencies with uv..."
	uv sync

# Install development dependencies
deps: install
	@echo "🔧 Installing development dependencies with uv..."
	uv sync --dev

# Run the server
run:
	@echo "🚀 Starting Ansible MCP server..."
	uv run python server.py

# Run with the startup script
start:
	@echo "🚀 Starting Ansible MCP server with startup script..."
	uv run python start_server.py

# Development mode (loads .env file)
dev: deps
	@echo "🔧 Starting server in development mode..."
	uv run python start_server.py

# Clean up cache files
clean:
	@echo "🧹 Cleaning up cache files..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name ".pytest_cache" -delete
	@echo "✅ Cleanup complete"

# Test connection to Ansible
test:
	@echo "🧪 Testing connection to Ansible..."
	uv run python test_connection.py

# Check environment configuration
check-env:
	@echo "🔍 Checking environment configuration..."
	@uv run python -c "import os; print('ANSIBLE_BASE_URL:', os.getenv('ANSIBLE_BASE_URL', 'NOT SET')); print('ANSIBLE_TOKEN:', 'SET' if os.getenv('ANSIBLE_TOKEN') else 'NOT SET')"

# Show server status
status:
	@echo "📊 Server status:"
	@ps aux | grep "server.py" | grep -v grep || echo "Server not running"

# Add uv-specific commands
uv-sync:
	@echo "🔄 Syncing dependencies with uv..."
	uv sync

uv-sync-dev:
	@echo "🔄 Syncing dependencies with uv (including dev dependencies)..."
	uv sync --dev

uv-add:
	@echo "➕ Add a new dependency with: uv add <package>"
	@echo "Example: uv add requests"

uv-add-dev:
	@echo "➕ Add a new dev dependency with: uv add --dev <package>"
	@echo "Example: uv add --dev pytest"

# Create example environment file
setup-env:
	@echo "⚙️ Creating example environment file..."
	@if [ ! -f .env ]; then \
		cp env.example .env; \
		echo "✅ Created .env file from env.example"; \
		echo "📝 Please edit .env with your Ansible details"; \
	else \
		echo "⚠️ .env file already exists"; \
	fi

# Test Ansible connection
test-connection:
	@echo "🔍 Testing Ansible connection..."
	@if [ ! -f .env ]; then \
		echo "⚠️  No .env file found. Creating from env.example..."; \
		cp env.example .env; \
		echo "📝 Please edit .env with your Ansible details before running this command again."; \
		exit 1; \
	fi
	@echo "📡 Testing connection with environment variables from .env..."
	uv run python test_connection.py

# Demonstrate pagination functionality
demo-pagination:
	@echo "📑 Demonstrating pagination functionality..."
	@if [ ! -f .env ]; then \
		echo "⚠️  No .env file found. Creating from env.example..."; \
		cp env.example .env; \
		echo "📝 Please edit .env with your Ansible details before running this command again."; \
		exit 1; \
	fi
	@echo "🔄 Testing different page sizes to show pagination in action..."
	uv run python demo_pagination.py 
