#!/usr/bin/env python3
"""
Test script for end-to-end sync system testing.
Tests: Static image upload → Database storage → Automatic sync → Local storage
"""
import os
import sys
import time
import requests

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.append(project_root)

from modules.recognition.sync_embeddings import EmbeddingSyncClient


def check_api_running(url, name):
    """Check if API is running."""
    try:
        response = requests.get(url, timeout=2)
        if response.status_code == 200:
            print(f"[✓] {name} is running at {url}")
            return True
        else:
            print(f"[-] {name} returned status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"[-] {name} is NOT running at {url}")
        print(f"    Error: {e}")
        return False


def test_sync_system():
    """Test the complete sync system."""
    print("=" * 70)
    print("  END-TO-END SYNC SYSTEM TEST")
    print("=" * 70)
    print()
    
    # Configuration
    ENROLLMENT_API_URL = "http://localhost:8000"
    SYNC_API_URL = "http://localhost:8001"
    
    # Step 1: Check APIs are running
    print("STEP 1: Checking API servers...")
    print("-" * 70)
    
    enrollment_running = check_api_running(ENROLLMENT_API_URL, "Enrollment API")
    sync_running = check_api_running(SYNC_API_URL, "Sync API")
    
    if not enrollment_running:
        print("\n[-] Enrollment API is not running!")
        print("    Please start it: ./run_backend.sh")
        return False
    
    if not sync_running:
        print("\n[-] Sync API is not running!")
        print("    Please start it: ./run_sync_api.sh")
        return False
    
    print()
    
    # Step 2: Initialize sync client
    print("STEP 2: Initializing sync client...")
    print("-" * 70)
    
    sync_client = EmbeddingSyncClient(
        api_base_url=SYNC_API_URL,
        local_cache_dir="data/local_embeddings"
    )
    
    initial_count = sync_client.get_embedding_count()
    print(f"[INFO] Current local embeddings: {initial_count}")
    print()
    
    # Step 3: Check for existing unsynced embeddings
    print("STEP 3: Checking for unsynced embeddings...")
    print("-" * 70)
    
    try:
        response = requests.get(f"{SYNC_API_URL}/api/sync-embeddings", timeout=5)
        if response.status_code == 200:
            data = response.json()
            unsynced_count = data.get('count', 0)
            print(f"[INFO] Found {unsynced_count} unsynced embedding(s) in database")
            
            if unsynced_count > 0:
                print("[INFO] These embeddings will be synced automatically")
                for update in data.get('updates', [])[:3]:  # Show first 3
                    print(f"  - Embedding ID {update['embedding_id']}: {update['person_name']}")
                if unsynced_count > 3:
                    print(f"  ... and {unsynced_count - 3} more")
        else:
            print(f"[-] Error checking unsynced embeddings: {response.status_code}")
    except Exception as e:
        print(f"[-] Error: {e}")
    
    print()
    
    # Step 4: Manual sync trigger
    print("STEP 4: Triggering sync...")
    print("-" * 70)
    
    result = sync_client.sync_new_embeddings()
    
    print(f"[INFO] Sync result:")
    print(f"  - Fetched: {result['fetched_count']}")
    print(f"  - Stored: {result['stored_count']}")
    print(f"  - Failed: {result['failed_count']}")
    
    if result['fetched_count'] > 0:
        print(f"\n[+] Successfully synced {result['fetched_count']} embedding(s)!")
    else:
        print("\n[INFO] No new embeddings to sync")
        print("       (This is normal if all embeddings are already synced)")
    
    print()
    
    # Step 5: Verify local storage
    print("STEP 5: Verifying local storage...")
    print("-" * 70)
    
    final_count = sync_client.get_embedding_count()
    print(f"[INFO] Local embeddings after sync: {final_count}")
    
    if final_count > initial_count:
        print(f"[+] Successfully stored {final_count - initial_count} new embedding(s) locally")
    
    # Get local embeddings
    local_embeddings = sync_client.get_local_embeddings()
    print(f"\n[INFO] Local cache contains {len(local_embeddings)} embedding(s):")
    
    for emb_id, emb_data in list(local_embeddings.items())[:5]:  # Show first 5
        print(f"  - ID {emb_id}: {emb_data.get('person_name', 'Unknown')}")
        print(f"    Age: {emb_data.get('person_age', 'N/A')}, "
              f"Gender: {emb_data.get('person_gender', 'N/A')}")
        print(f"    Vector shape: {emb_data.get('embedding_vector', []).shape if hasattr(emb_data.get('embedding_vector'), 'shape') else 'N/A'}")
    
    if len(local_embeddings) > 5:
        print(f"  ... and {len(local_embeddings) - 5} more")
    
    print()
    
    # Step 6: Summary
    print("=" * 70)
    print("  TEST SUMMARY")
    print("=" * 70)
    print(f"✓ Enrollment API: {'Running' if enrollment_running else 'Not Running'}")
    print(f"✓ Sync API: {'Running' if sync_running else 'Not Running'}")
    print(f"✓ Local embeddings: {final_count}")
    print(f"✓ Sync successful: {result['stored_count'] > 0}")
    print("=" * 70)
    
    return True


if __name__ == "__main__":
    test_sync_system()

