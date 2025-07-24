#!/usr/bin/env python3
"""
Startup script for the Ansible MCP Playbook Server.
This script loads environment variables from .env or env file and starts the server.
"""

import os
import sys
from pathlib import Path


def load_env_file(env_file_path: str):
    """Load environment variables from a file"""
    if not os.path.exists(env_file_path):
        return False
    
    with open(env_file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                if '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
    
    return True


def main():
    """Main startup function"""
    print("🚀 Starting Ansible MCP Playbook Server...")
    
    # Try to load environment variables from file
    env_files = ['.env', 'env', 'env.example']
    env_loaded = False
    
    for env_file in env_files:
        if load_env_file(env_file):
            print(f"✅ Loaded environment variables from: {env_file}")
            env_loaded = True
            break
    
    if not env_loaded:
        print("ℹ️  No environment file found. Using system environment variables.")
    
    # Check required environment variables
    required_vars = ['ANSIBLE_BASE_URL', 'ANSIBLE_TOKEN']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease set these environment variables or create an .env file.")
        print("See env.example for reference.")
        sys.exit(1)
    
    transport=os.getenv('MCP_TRANSPORT', "stdio")
    host=os.getenv('MCP_HOST', "0.0.0.0")
    port=int(os.getenv('MCP_PORT', "8200"))
    # Display configuration
    print("\n📋 Configuration:")
    print(f"   Ansible Base URL: {os.getenv('ANSIBLE_BASE_URL')}")
    aap_version = os.getenv('AAP_VERSION', '2.4')
    print(f"   AAP Version: {aap_version}")
    api_prefix = "/api" if aap_version == "2.4" else "/api/controller"
    print(f"   API Prefix: {api_prefix}")
    print(f"   MCP Transport: {transport}")
    if os.getenv('MCP_TRANSPORT', 'stdio').lower() in ['http', 'sse']:
        print(f"   MCP Host: {host}")
        print(f"   MCP Port: {port}")
    print(f"   Token: {'*' * len(os.getenv('ANSIBLE_TOKEN', '')[:8])}...")
    
    print("\n🎯 Starting server...")
    
    # Import and run the server
    from server import start
    try:
        start()
    except ImportError as e:
        print(f"❌ Failed to import server: {e}")
        print("Make sure you're running this from the correct directory.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 
