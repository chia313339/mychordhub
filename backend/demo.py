#!/usr/bin/env python3
"""
Demo script to showcase MyChordHub Backend API functionality.

This script demonstrates the main features of the API including:
- User registration and authentication
- Song creation and management
- Chord transposition
- Collections management
- Music theory utilities

Run with: python demo.py
"""

import asyncio
import json
from typing import Dict, Any

import httpx

# API base URL
BASE_URL = "http://localhost:8000/api/v1"


class MyChordHubDemo:
    """Demo client for MyChordHub API."""
    
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.client = httpx.AsyncClient()
        self.access_token: str = None
        
    def _auth_headers(self) -> Dict[str, str]:
        """Get authentication headers."""
        if not self.access_token:
            return {}
        return {"Authorization": f"Bearer {self.access_token}"}
    
    async def register_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Register a new user."""
        response = await self.client.post(
            f"{self.base_url}/auth/register",
            json=user_data
        )
        response.raise_for_status()
        return response.json()
    
    async def login_user(self, email: str, password: str) -> Dict[str, Any]:
        """Login user and get access token."""
        response = await self.client.post(
            f"{self.base_url}/auth/login",
            data={"username": email, "password": password}
        )
        response.raise_for_status()
        token_data = response.json()
        self.access_token = token_data["access_token"]
        return token_data
    
    async def create_song(self, song_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new song."""
        response = await self.client.post(
            f"{self.base_url}/songs/",
            json=song_data,
            headers=self._auth_headers()
        )
        response.raise_for_status()
        return response.json()
    
    async def search_songs(self, query: str) -> Dict[str, Any]:
        """Search for songs."""
        response = await self.client.get(
            f"{self.base_url}/songs/search",
            params={"q": query},
            headers=self._auth_headers()
        )
        response.raise_for_status()
        return response.json()
    
    async def transpose_chords(self, chords: list, semitones: int) -> Dict[str, Any]:
        """Transpose a list of chords."""
        response = await self.client.post(
            f"{self.base_url}/music/transpose",
            json={"chords": chords, "semitones": semitones},
            headers=self._auth_headers()
        )
        response.raise_for_status()
        return response.json()
    
    async def get_capo_suggestion(self, original_key: str, target_key: str) -> Dict[str, Any]:
        """Get capo suggestion for key change."""
        response = await self.client.post(
            f"{self.base_url}/music/capo-suggestion",
            json={"original_key": original_key, "target_key": target_key},
            headers=self._auth_headers()
        )
        response.raise_for_status()
        return response.json()
    
    async def create_collection(self, name: str, description: str) -> Dict[str, Any]:
        """Create a new collection."""
        response = await self.client.post(
            f"{self.base_url}/collections/",
            json={"name": name, "description": description, "is_public": True},
            headers=self._auth_headers()
        )
        response.raise_for_status()
        return response.json()
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


async def run_demo():
    """Run the complete demo."""
    demo = MyChordHubDemo()
    
    try:
        print("🎸 MyChordHub Backend API Demo")
        print("=" * 40)
        
        # Test user data
        user_data = {
            "email": "demo@example.com",
            "username": "demouser",
            "password": "demopassword123",
            "first_name": "Demo",
            "last_name": "User"
        }
        
        print("\n1. 👤 User Registration")
        try:
            user = await demo.register_user(user_data)
            print(f"✅ User registered: {user['username']} ({user['email']})")
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 400:
                print("ℹ️  User already exists, proceeding with login...")
            else:
                raise
        
        print("\n2. 🔐 User Authentication")
        token_data = await demo.login_user(user_data["email"], user_data["password"])
        print(f"✅ Login successful! Token expires in {token_data.get('expires_in', 'N/A')} minutes")
        
        print("\n3. 🎵 Creating a Song")
        song_data = {
            "title": "Amazing Grace",
            "artist": "Traditional",
            "genre": "Hymn",
            "key": "G",
            "bpm": 90,
            "difficulty": "Beginner",
            "lyrics_and_chords": """
G               C        G
Amazing grace how sweet the sound
                D        G
That saved a wretch like me
G               C        G
I once was lost but now am found
                D        G
Was blind but now I see
""",
            "tags": ["traditional", "hymn", "beginner"],
            "is_public": True
        }
        
        song = await demo.create_song(song_data)
        print(f"✅ Song created: '{song['title']}' by {song['artist']}")
        print(f"   Song ID: {song['id']}, Key: {song['key']}, Difficulty: {song['difficulty']}")
        
        print("\n4. 🔍 Searching Songs")
        search_results = await demo.search_songs("Amazing")
        print(f"✅ Found {len(search_results)} songs matching 'Amazing'")
        for result in search_results[:3]:  # Show first 3 results
            print(f"   - {result['title']} by {result['artist']}")
        
        print("\n5. 🎼 Chord Transposition")
        original_chords = ["G", "C", "D", "Em"]
        transposed = await demo.transpose_chords(original_chords, 2)  # Transpose up 2 semitones
        print(f"✅ Original chords: {original_chords}")
        print(f"   Transposed (+2): {transposed['transposed_chords']}")
        
        print("\n6. 🎪 Capo Suggestions")
        capo_suggestion = await demo.get_capo_suggestion("G", "A")
        print(f"✅ To play in A from G:")
        if capo_suggestion['capo_fret']:
            print(f"   Use capo on fret {capo_suggestion['capo_fret']}")
            print(f"   Effective key: {capo_suggestion['effective_key']}")
        else:
            print("   No capo suggestion available")
        
        print("\n7. 📚 Creating a Collection")
        collection = await demo.create_collection(
            "My Favorite Hymns",
            "A collection of traditional hymns and spiritual songs"
        )
        print(f"✅ Collection created: '{collection['name']}'")
        print(f"   Description: {collection['description']}")
        
        print("\n8. 🎯 More Chord Transposition Examples")
        test_chords = [
            (["C", "Am", "F", "G"], "Classic progression"),
            (["D", "A", "Bm", "G"], "Popular progression"),
            (["Em", "C", "G", "D"], "Emotional progression")
        ]
        
        for chords, description in test_chords:
            result = await demo.transpose_chords(chords, -3)  # Transpose down 3 semitones
            print(f"   {description}:")
            print(f"     Original: {chords}")
            print(f"     Transposed (-3): {result['transposed_chords']}")
        
        print("\n" + "=" * 40)
        print("🎉 Demo completed successfully!")
        print("   You can now explore the API at: http://localhost:8000/api/v1/docs")
        
    except httpx.ConnectError:
        print("❌ Connection Error: Make sure the API server is running at http://localhost:8000")
        print("   Start the server with: poetry run uvicorn app.main:app --reload")
    
    except httpx.HTTPStatusError as e:
        print(f"❌ HTTP Error {e.response.status_code}: {e.response.text}")
    
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    
    finally:
        await demo.close()


if __name__ == "__main__":
    print("Starting MyChordHub API Demo...")
    print("Make sure the API server is running first!")
    print("Run: poetry run uvicorn app.main:app --reload")
    print("\nPress Enter to continue or Ctrl+C to cancel...")
    input()
    
    asyncio.run(run_demo())