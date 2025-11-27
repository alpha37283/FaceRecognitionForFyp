# backend/sync_api.py
"""
Separate API for Live Feed Sync System (Jetson Nano/Surveillance Side).
This API handles embedding synchronization for live camera feed devices.
Completely separate from the enrollment API.
Automatically starts background sync service on startup.
"""
import os
import sys
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from backend.database import get_db, init_db
from backend.services import (
    get_unsynced_embeddings,
    mark_embeddings_as_synced
)

# Add project root to path for importing modules
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)

# Separate FastAPI app for sync operations
sync_app = FastAPI(
    title="Face Embedding Sync API",
    description="API for live feed devices to sync embeddings from main database",
    version="1.0.0"
)

sync_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@sync_app.on_event("startup")
async def startup_event():
    init_db()
    print("[INFO] Sync API database initialized")
    
    # Start automatic background sync service
    try:
        from modules.recognition.embedding_sync_service import EmbeddingSyncService
        
        # Get configuration from environment or use defaults
        sync_interval = float(os.getenv("SYNC_INTERVAL", "3.0"))
        local_cache_dir = os.getenv("LOCAL_CACHE_DIR", "data/local_embeddings")
        
        # Initialize and start sync service
        sync_service = EmbeddingSyncService(
            api_base_url="http://localhost:8001",  # This API's URL
            local_cache_dir=local_cache_dir,
            sync_interval=sync_interval
        )
        sync_service.start()
        
        # Store service instance in app state so it can be accessed
        sync_app.state.sync_service = sync_service
        
        print(f"[INFO] Automatic sync service started (checking every {sync_interval}s)")
        print(f"[INFO] Local cache directory: {local_cache_dir}")
    except Exception as e:
        print(f"[-] Warning: Could not start sync service: {e}")
        print("[-] Sync API will still work, but automatic syncing is disabled")


@sync_app.on_event("shutdown")
async def shutdown_event():
    """Stop sync service on shutdown."""
    if hasattr(sync_app.state, 'sync_service'):
        sync_app.state.sync_service.stop()
        print("[INFO] Sync service stopped")


@sync_app.get("/")
async def root():
    return {
        "message": "Face Embedding Sync API",
        "version": "1.0.0",
        "status": "running",
        "purpose": "Live feed device synchronization"
    }


@sync_app.get("/api/sync-embeddings")
async def sync_embeddings_endpoint(db: Session = Depends(get_db)):
    """
    Get all unsynced embeddings for live feed devices.
    This endpoint is called by live camera feed to fetch new embeddings
    when they are added to the database.
    
    This is a TRIGGER-BASED endpoint - only returns embeddings that haven't been synced yet.
    
    Returns:
        List of unsynced embeddings with person metadata
    """
    try:
        unsynced = get_unsynced_embeddings(db)
        return {
            "success": True,
            "count": len(unsynced),
            "updates": unsynced
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching unsynced embeddings: {str(e)}"
        )


@sync_app.post("/api/sync-embeddings/mark-synced")
async def mark_synced_endpoint(request: dict, db: Session = Depends(get_db)):
    """
    Mark embeddings as synced after they've been fetched by live feed device.
    
    Request body:
        {"sync_ids": [1, 2, 3, ...]}
    """
    try:
        sync_ids = request.get("sync_ids", [])
        if not sync_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="sync_ids list is required"
            )
        
        success = mark_embeddings_as_synced(db, sync_ids)
        if success:
            return {
                "success": True,
                "message": f"Marked {len(sync_ids)} embedding(s) as synced"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to mark embeddings as synced"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error marking embeddings as synced: {str(e)}"
        )

