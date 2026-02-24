#!/usr/bin/env python3
"""
Simple test script for MLBB AI Coach API
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import requests
import json


API_BASE = "http://localhost:8000"


def test_health():
    """Test health endpoint."""
    print("Testing health endpoint...")
    try:
        response = requests.get(f"{API_BASE}/health")
        if response.status_code == 200:
            print("✓ Health check passed")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"✗ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"✗ Error: {e}")
    print()


def test_chat():
    """Test chat endpoint."""
    print("Testing chat endpoint...")
    test_messages = [
        "Tell me about Layla",
        "What items should I build on Miya?",
        "How do I play Moskov vs Natalia?"
    ]

    for message in test_messages:
        print(f"\nUser: {message}")
        try:
            response = requests.post(
                f"{API_BASE}/api/chat",
                json={
                    "message": message,
                    "llm_provider": "claude"
                }
            )

            if response.status_code == 200:
                data = response.json()
                print(f"Assistant: {data['response'][:200]}...")
                if data.get('suggestions'):
                    print(f"Suggestions: {data['suggestions']}")
            else:
                print(f"✗ Error: {response.status_code}")
                print(response.text)

        except Exception as e:
            print(f"✗ Error: {e}")

    print()


def test_providers():
    """Test available providers endpoint."""
    print("Testing providers endpoint...")
    try:
        response = requests.get(f"{API_BASE}/api/providers")
        if response.status_code == 200:
            providers = response.json()
            print(f"✓ Available providers: {providers}")
        else:
            print(f"✗ Error: {response.status_code}")
    except Exception as e:
        print(f"✗ Error: {e}")
    print()


def test_heroes():
    """Test heroes list endpoint."""
    print("Testing heroes endpoint...")
    try:
        response = requests.get(f"{API_BASE}/api/heroes")
        if response.status_code == 200:
            heroes = response.json()
            print(f"✓ Available heroes: {heroes}")
        else:
            print(f"✗ Error: {response.status_code}")
    except Exception as e:
        print(f"✗ Error: {e}")
    print()


if __name__ == "__main__":
    print("=" * 50)
    print("MLBB AI Coach API Test Suite")
    print("=" * 50)
    print()

    test_health()
    test_providers()
    test_heroes()

    # Only test chat if health check passes
    print("Testing chat functionality...")
    print("Note: This requires API keys to be configured")
    print()

    choice = input("Run chat tests? (y/n): ")
    if choice.lower() == 'y':
        test_chat()
    else:
        print("Skipping chat tests")

    print()
    print("=" * 50)
    print("Tests complete!")
    print("=" * 50)
