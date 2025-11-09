#!/usr/bin/env python3
"""
Ngrok Setup Script for Alpha Crucible Quant

This script helps set up Ngrok for external access to the Docker services.
"""

import os
import subprocess
import sys
import time
import requests
from pathlib import Path

def check_ngrok_installed():
    """Check if Ngrok is installed."""
    try:
        result = subprocess.run(['ngrok', 'version'], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def install_ngrok():
    """Install Ngrok if not already installed."""
    print("Installing Ngrok...")
    
    # Download and install ngrok
    if sys.platform == "win32":
        # Windows installation
        subprocess.run([
            "powershell", "-Command", 
            "Invoke-WebRequest -Uri 'https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-windows-amd64.zip' -OutFile 'ngrok.zip'"
        ])
        subprocess.run(["powershell", "-Command", "Expand-Archive -Path ngrok.zip -DestinationPath ."])
        subprocess.run(["powershell", "-Command", "Move-Item ngrok.exe C:\\Windows\\System32\\"])
        subprocess.run(["powershell", "-Command", "Remove-Item ngrok.zip"])
    else:
        # Linux/Mac installation
        subprocess.run([
            "curl", "-s", "https://ngrok-agent.s3.amazonaws.com/ngrok.asc", "|", "sudo", "tee", "/etc/apt/trusted.gpg.d/ngrok.asc", ">", "/dev/null"
        ])
        subprocess.run([
            "echo", "'deb https://ngrok-agent.s3.amazonaws.com buster main'", "|", "sudo", "tee", "/etc/apt/sources.list.d/ngrok.list"
        ])
        subprocess.run(["sudo", "apt", "update"])
        subprocess.run(["sudo", "apt", "install", "ngrok"])

def setup_ngrok_auth():
    """Set up Ngrok authentication."""
    auth_token = os.getenv('NGROK_AUTHTOKEN')
    if not auth_token:
        print("Error: NGROK_AUTHTOKEN not found in environment variables")
        return False
    
    try:
        subprocess.run(['ngrok', 'config', 'add-authtoken', auth_token], check=True)
        print("Ngrok authentication configured successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error configuring Ngrok authentication: {e}")
        return False

def start_ngrok_tunnel(port=80):
    """Start Ngrok tunnel for the specified port."""
    print(f"Starting Ngrok tunnel on port {port}...")
    
    try:
        # Start ngrok in the background
        process = subprocess.Popen(['ngrok', 'http', str(port), '--log=stdout'], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE,
                                 text=True)
        
        # Wait a moment for ngrok to start
        time.sleep(3)
        
        # Get the public URL
        try:
            response = requests.get('http://localhost:4040/api/tunnels', timeout=5)
            if response.status_code == 200:
                tunnels = response.json()
                if tunnels.get('tunnels'):
                    public_url = tunnels['tunnels'][0]['public_url']
                    print(f"Ngrok tunnel started successfully!")
                    print(f"Public URL: {public_url}")
                    print(f"Local URL: http://localhost:{port}")
                    return public_url, process
        except requests.RequestException:
            print("Could not get tunnel URL from Ngrok API")
        
        print("Ngrok tunnel started (check http://localhost:4040 for details)")
        return None, process
        
    except Exception as e:
        print(f"Error starting Ngrok tunnel: {e}")
        return None, None

def update_cors_config(public_url):
    """Update CORS configuration with the public URL."""
    if not public_url:
        return
    
    env_file = Path('.env')
    if env_file.exists():
        # Read current .env file
        with open(env_file, 'r') as f:
            content = f.read()
        
        # Update CORS_ORIGINS with the public URL
        if 'CORS_ORIGINS=' in content:
            # Replace existing CORS_ORIGINS
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line.startswith('CORS_ORIGINS='):
                    lines[i] = f"CORS_ORIGINS={public_url},http://localhost:3000,http://localhost:3001,http://localhost:5173"
                    break
            content = '\n'.join(lines)
        else:
            # Add CORS_ORIGINS if not present
            content += f"\nCORS_ORIGINS={public_url},http://localhost:3000,http://localhost:3001,http://localhost:5173"
        
        # Write updated content
        with open(env_file, 'w') as f:
            f.write(content)
        
        print(f"Updated CORS configuration with public URL: {public_url}")

def main():
    """Main function."""
    print("Alpha Crucible Quant - Ngrok Setup")
    print("=" * 40)
    
    # Check if Ngrok is installed
    if not check_ngrok_installed():
        print("Ngrok not found. Installing...")
        install_ngrok()
    
    # Set up authentication
    if not setup_ngrok_auth():
        print("Failed to set up Ngrok authentication")
        return
    
    # Start tunnel
    public_url, process = start_ngrok_tunnel(80)
    
    if public_url:
        update_cors_config(public_url)
        print("\nNext steps:")
        print("1. Update your .env file with the public URL if needed")
        print("2. Restart your Docker containers: docker-compose up -d")
        print("3. Your app will be accessible at:", public_url)
    
    if process:
        print("\nNgrok is running. Press Ctrl+C to stop.")
        try:
            process.wait()
        except KeyboardInterrupt:
            print("\nStopping Ngrok...")
            process.terminate()

if __name__ == "__main__":
    main()
