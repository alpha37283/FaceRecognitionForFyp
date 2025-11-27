# modules/recognition/embedding_sync_service.py
"""
Background service for automatically syncing embeddings from backend.
Runs in background and triggers sync when new embeddings are detected.
"""
import time
import threading
from modules.recognition.sync_embeddings import EmbeddingSyncClient


class EmbeddingSyncService:
    """
    Background service that automatically syncs embeddings from backend.
    Uses trigger-based approach - only fetches when new embeddings are added.
    """
    
    def __init__(self, api_base_url: str = "http://localhost:8001", 
                 local_cache_dir: str = "data/local_embeddings",
                 sync_interval: float = 5.0):
        """
        Initialize sync service.
        
        Args:
            api_base_url: Backend API URL
            local_cache_dir: Local directory to cache embeddings
            sync_interval: How often to check for new embeddings (seconds)
        """
        self.sync_client = EmbeddingSyncClient(api_base_url, local_cache_dir)
        self.sync_interval = sync_interval
        self.running = False
        self.sync_thread = None
        self._last_sync_count = 0
    
    def start(self):
        """Start the background sync service."""
        if self.running:
            print("[WARNING] Sync service is already running")
            return
        
        self.running = True
        self.sync_thread = threading.Thread(target=self._sync_loop, daemon=True)
        self.sync_thread.start()
        print(f"[INFO] Embedding sync service started (checking every {self.sync_interval}s)")
    
    def stop(self):
        """Stop the background sync service."""
        self.running = False
        if self.sync_thread:
            self.sync_thread.join(timeout=2.0)
        print("[INFO] Embedding sync service stopped")
    
    def _sync_loop(self):
        """Background loop that periodically checks for new embeddings."""
        while self.running:
            try:
                # Trigger sync - only fetches new embeddings
                result = self.sync_client.sync_new_embeddings()
                
                if result['fetched_count'] > 0:
                    print(f"[SYNC] Fetched {result['fetched_count']} new embedding(s), "
                          f"stored {result['stored_count']}, failed {result['failed_count']}")
                    self._last_sync_count = result['fetched_count']
                
            except Exception as e:
                print(f"[-] Error in sync loop: {e}")
            
            # Wait before next check
            time.sleep(self.sync_interval)
    
    def sync_now(self) -> dict:
        """
        Manually trigger sync immediately (useful for testing).
        
        Returns:
            Sync result dictionary
        """
        return self.sync_client.sync_new_embeddings()
    
    def get_local_embeddings(self):
        """Get all locally cached embeddings for face comparison."""
        return self.sync_client.get_local_embeddings()
    
    def get_embedding_count(self) -> int:
        """Get count of locally cached embeddings."""
        return self.sync_client.get_embedding_count()

