# modules/recognition/sync_embeddings.py
"""
Live feed embedding sync module.
Automatically fetches new embeddings from backend when they are added to database.
Stores embeddings locally for face recognition comparison.
"""
import os
import json
import numpy as np
import requests
from typing import List, Dict, Optional
from datetime import datetime


class EmbeddingSyncClient:
    """
    Client for syncing embeddings from main server to local device.
    Automatically fetches new embeddings when they are added to database.
    """
    
    def __init__(self, api_base_url: str = "http://localhost:8001", local_cache_dir: str = "data/local_embeddings"):
        """
        Initialize sync client.
        
        Args:
            api_base_url: Base URL of the backend API
            local_cache_dir: Directory to store synced embeddings locally
        """
        self.api_base_url = api_base_url.rstrip('/')
        self.sync_endpoint = f"{self.api_base_url}/api/sync-embeddings"
        self.mark_synced_endpoint = f"{self.api_base_url}/api/sync-embeddings/mark-synced"
        self.local_cache_dir = local_cache_dir
        
        # Create local cache directory
        os.makedirs(local_cache_dir, exist_ok=True)
        
        # Cache file to store synced embeddings metadata
        self.cache_metadata_file = os.path.join(local_cache_dir, "synced_embeddings.json")
        self.embeddings_cache = {}  # {embedding_id: embedding_data}
        
        # Load existing cache
        self._load_cache()
    
    def _load_cache(self):
        """Load existing synced embeddings from local cache."""
        if os.path.exists(self.cache_metadata_file):
            try:
                with open(self.cache_metadata_file, 'r') as f:
                    cache_data = json.load(f)
                    self.embeddings_cache = cache_data.get('embeddings', {})
                print(f"[INFO] Loaded {len(self.embeddings_cache)} cached embeddings from local storage")
            except Exception as e:
                print(f"[-] Error loading cache: {e}")
                self.embeddings_cache = {}
        else:
            self.embeddings_cache = {}
    
    def _save_cache(self):
        """Save synced embeddings to local cache."""
        try:
            cache_data = {
                'last_sync': datetime.now().isoformat(),
                'embeddings': self.embeddings_cache
            }
            with open(self.cache_metadata_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
        except Exception as e:
            print(f"[-] Error saving cache: {e}")
    
    def _save_embedding_file(self, embedding_id: int, embedding_vector: List[float]):
        """Save embedding vector to local .npy file."""
        embedding_path = os.path.join(self.local_cache_dir, f"embedding_{embedding_id}.npy")
        np.save(embedding_path, np.array(embedding_vector))
        return embedding_path
    
    def check_for_new_embeddings(self) -> List[Dict]:
        """
        Check backend for new unsynced embeddings.
        This is the trigger-based fetch - only gets new embeddings.
        
        Returns:
            List of new embedding data with person metadata
        """
        try:
            response = requests.get(self.sync_endpoint, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('success'):
                updates = data.get('updates', [])
                return updates
            else:
                print(f"[-] Sync endpoint returned error: {data}")
                return []
                
        except requests.exceptions.RequestException as e:
            print(f"[-] Error fetching unsynced embeddings: {e}")
            return []
        except Exception as e:
            print(f"[-] Unexpected error: {e}")
            return []
    
    def sync_new_embeddings(self) -> Dict:
        """
        Fetch and store new embeddings from backend.
        This is the main sync function - automatically triggered when new embeddings are added.
        
        Returns:
            Dict with sync results:
            {
                'success': bool,
                'fetched_count': int,
                'stored_count': int,
                'failed_count': int,
                'synced_ids': List[int]
            }
        """
        # Check for new embeddings
        new_embeddings = self.check_for_new_embeddings()
        
        if not new_embeddings:
            return {
                'success': True,
                'fetched_count': 0,
                'stored_count': 0,
                'failed_count': 0,
                'synced_ids': []
            }
        
        print(f"[INFO] Found {len(new_embeddings)} new embedding(s) to sync")
        
        synced_ids = []
        stored_count = 0
        failed_count = 0
        
        for embedding_data in new_embeddings:
            try:
                embedding_id = embedding_data['embedding_id']
                action = embedding_data['action']
                
                # Handle different actions
                if action == "INSERT":
                    # Store new embedding locally
                    embedding_vector = embedding_data['embedding_vector']
                    
                    # Save embedding vector to file
                    embedding_path = self._save_embedding_file(embedding_id, embedding_vector)
                    
                    # Store in cache with person metadata
                    self.embeddings_cache[embedding_id] = {
                        'embedding_id': embedding_id,
                        'person_id': embedding_data['person_id'],
                        'person_name': embedding_data['person_name'],
                        'person_age': embedding_data.get('person_age'),
                        'person_gender': embedding_data.get('person_gender'),
                        'person_notes': embedding_data.get('person_notes'),
                        'embedding_path': embedding_path,
                        'action': action,
                        'timestamp': embedding_data.get('timestamp'),
                        'synced_at': datetime.now().isoformat()
                    }
                    
                    stored_count += 1
                    synced_ids.append(embedding_data['sync_id'])
                    print(f"[+] Synced embedding ID {embedding_id} for person: {embedding_data['person_name']}")
                    
                elif action == "DELETE":
                    # Remove embedding from local cache
                    if embedding_id in self.embeddings_cache:
                        # Remove embedding file
                        embedding_path = self.embeddings_cache[embedding_id].get('embedding_path')
                        if embedding_path and os.path.exists(embedding_path):
                            os.remove(embedding_path)
                        
                        del self.embeddings_cache[embedding_id]
                        stored_count += 1
                        synced_ids.append(embedding_data['sync_id'])
                        print(f"[+] Removed embedding ID {embedding_id} from local cache")
                    else:
                        synced_ids.append(embedding_data['sync_id'])
                        print(f"[INFO] Embedding ID {embedding_id} not in local cache (already removed)")
                
                elif action == "UPDATE":
                    # Update existing embedding
                    embedding_vector = embedding_data['embedding_vector']
                    embedding_path = self._save_embedding_file(embedding_id, embedding_vector)
                    
                    if embedding_id in self.embeddings_cache:
                        self.embeddings_cache[embedding_id].update({
                            'embedding_path': embedding_path,
                            'person_name': embedding_data['person_name'],
                            'person_age': embedding_data.get('person_age'),
                            'person_gender': embedding_data.get('person_gender'),
                            'person_notes': embedding_data.get('person_notes'),
                            'updated_at': datetime.now().isoformat()
                        })
                    else:
                        # If not in cache, add it
                        self.embeddings_cache[embedding_id] = {
                            'embedding_id': embedding_id,
                            'person_id': embedding_data['person_id'],
                            'person_name': embedding_data['person_name'],
                            'person_age': embedding_data.get('person_age'),
                            'person_gender': embedding_data.get('person_gender'),
                            'person_notes': embedding_data.get('person_notes'),
                            'embedding_path': embedding_path,
                            'action': action,
                            'timestamp': embedding_data.get('timestamp'),
                            'synced_at': datetime.now().isoformat()
                        }
                    
                    stored_count += 1
                    synced_ids.append(embedding_data['sync_id'])
                    print(f"[+] Updated embedding ID {embedding_id} for person: {embedding_data['person_name']}")
                
            except Exception as e:
                failed_count += 1
                print(f"[-] Error syncing embedding ID {embedding_data.get('embedding_id', 'unknown')}: {e}")
                continue
        
        # Save cache to disk
        self._save_cache()
        
        # Mark embeddings as synced on server
        if synced_ids:
            self._mark_as_synced(synced_ids)
        
        return {
            'success': True,
            'fetched_count': len(new_embeddings),
            'stored_count': stored_count,
            'failed_count': failed_count,
            'synced_ids': synced_ids
        }
    
    def _mark_as_synced(self, sync_ids: List[int]):
        """Mark embeddings as synced on the server."""
        try:
            response = requests.post(
                self.mark_synced_endpoint,
                json={"sync_ids": sync_ids},
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            response.raise_for_status()
            print(f"[+] Marked {len(sync_ids)} embedding(s) as synced on server")
        except Exception as e:
            print(f"[-] Error marking embeddings as synced on server: {e}")
    
    def get_local_embeddings(self) -> Dict:
        """
        Get all locally cached embeddings for face comparison.
        
        Returns:
            Dict mapping embedding_id to embedding data with loaded vector
        """
        result = {}
        for embedding_id, metadata in self.embeddings_cache.items():
            try:
                embedding_path = metadata.get('embedding_path')
                if embedding_path and os.path.exists(embedding_path):
                    embedding_vector = np.load(embedding_path)
                    result[embedding_id] = {
                        **metadata,
                        'embedding_vector': embedding_vector
                    }
            except Exception as e:
                print(f"[-] Error loading embedding {embedding_id}: {e}")
                continue
        
        return result
    
    def get_embedding_count(self) -> int:
        """Get count of locally cached embeddings."""
        return len(self.embeddings_cache)

