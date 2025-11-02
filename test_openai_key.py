#!/usr/bin/env python3
"""
Test script to verify OpenAI API key is valid and working.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load .env file (override any existing env vars)
env_path = Path('.env')
if env_path.exists():
    load_dotenv(env_path, override=True)  # Override existing env vars
    print(f"✅ Loaded .env from: {env_path.absolute()}")
else:
    print("❌ .env file not found in current directory")
    sys.exit(1)

# Get the key
key = os.getenv('OPENAI_API_KEY')

if not key:
    print("\n❌ OPENAI_API_KEY NOT found in environment!")
    print("   Make sure it's in your .env file as: OPENAI_API_KEY=sk-...")
    sys.exit(1)

# Analyze the key
print(f"\n📋 API Key Analysis:")
print(f"   Length: {len(key)} characters")
print(f"   Starts with: {key[:15]}...")
print(f"   Ends with: ...{key[-10:]}")
print(f"   Has leading/trailing whitespace: {key != key.strip()}")

# Check for common issues
issues = []
if key.startswith('"') or key.startswith("'"):
    issues.append("⚠️  Key starts with quotes - remove them!")
if key.endswith('"') or key.endswith("'"):
    issues.append("⚠️  Key ends with quotes - remove them!")
if ' ' in key.strip():
    issues.append("⚠️  Key contains spaces!")
if len(key.strip()) < 20:
    issues.append("⚠️  Key seems too short (should be 50+ characters)!")
if not key.startswith('sk-'):
    issues.append("⚠️  Key doesn't start with 'sk-' or 'sk-proj-'")

if issues:
    print(f"\n⚠️  Potential Issues Found:")
    for issue in issues:
        print(f"   {issue}")
else:
    print("\n✅ Key format looks good!")

# Strip whitespace for testing
key_stripped = key.strip()

# Test the API key
print(f"\n🔍 Testing API key with OpenAI...")
try:
    from openai import OpenAI
    
    client = OpenAI(api_key=key_stripped)
    
    # Make a simple test request
    print("   Making test API call...")
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # Use cheaper model for testing
        messages=[
            {"role": "user", "content": "Say 'Hello' if you can read this."}
        ],
        max_tokens=10
    )
    
    result = response.choices[0].message.content
    print(f"\n✅ SUCCESS! API key is valid!")
    print(f"   Test response: {result}")
    print(f"\n✅ You can use this API key for the news analysis feature.")
    
except ImportError:
    print("\n❌ OpenAI package not installed!")
    print("   Install it with: pip install openai")
    sys.exit(1)
    
except Exception as e:
    error_msg = str(e)
    print(f"\n❌ API Key Test FAILED!")
    print(f"   Error: {error_msg}")
    
    if "401" in error_msg or "invalid_api_key" in error_msg.lower() or "authentication" in error_msg.lower():
        print(f"\n🔴 The API key is INVALID or EXPIRED!")
        print(f"   Please:")
        print(f"   1. Go to https://platform.openai.com/account/api-keys")
        print(f"   2. Check if your key is active")
        print(f"   3. Create a new key if needed")
        print(f"   4. Update your .env file")
        print(f"   5. Restart your backend server")
    elif "rate_limit" in error_msg.lower():
        print(f"\n⚠️  Rate limit hit, but key is valid!")
    else:
        print(f"\n⚠️  Unexpected error - may be a network issue")
    
    sys.exit(1)

