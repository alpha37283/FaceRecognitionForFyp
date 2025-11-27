# modules/recognition/live_embedding.py
"""
Live camera embedding generation module.
Generates ArcFace embeddings for faces detected in live camera feed
using the same preprocessing pipeline as static images.
"""
import os
import cv2
import numpy as np
from PIL import Image
from datetime import datetime
from modules.recognition.arcface_embedding import ArcFaceEmbeddingGenerator


class LiveEmbeddingGenerator:
    """Handles embedding generation for live camera feed with same preprocessing as static images."""
    
    def __init__(self, output_dir="data/embeddings", save_preprocessed=True):
        """
        Initialize live embedding generator.
        
        Args:
            output_dir: Directory to save embeddings (default: "data/embeddings")
            save_preprocessed: Whether to save preprocessed 112×112 images (default: True)
        """
        print("[INFO] Initializing ArcFace embedding generator for live feed...")
        self.embedding_generator = ArcFaceEmbeddingGenerator()
        print("[INFO] ArcFace embedding generator ready.")
        
        self.output_dir = output_dir
        self.save_preprocessed = save_preprocessed
        
        # Create output directories
        os.makedirs(output_dir, exist_ok=True)
        if save_preprocessed:
            self.preprocessed_dir = os.path.join(output_dir, "preprocessed")
            os.makedirs(self.preprocessed_dir, exist_ok=True)
        else:
            self.preprocessed_dir = None
    
    def generate_embedding_for_face(self, face_image, base_name=None):
        """
        Generate embedding for a single face from live camera feed.
        Uses the same preprocessing pipeline as static images:
        1. Face Detection (already done)
        2. Landmark Detection (5-point alignment)
        3. Face Alignment (affine transformation)
        4. Resize to 112×112
        5. Pixel Normalization to [-1, 1]
        6. Embedding Generation
        
        Args:
            face_image: Face image as PIL Image or numpy array (RGB format)
            base_name: Base name for output files (if None, generates timestamp-based name)
        
        Returns:
            dict: {
                'embedding': numpy array (512-dim) or None if failed,
                'embedding_path': path to saved .npy file or None,
                'preprocessed_path': path to saved preprocessed image or None,
                'landmarks': landmark coordinates or None,
                'success': bool
            }
        """
        # Generate base name if not provided
        if base_name is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            base_name = f"live_face_{timestamp}"
        
        try:
            # Use the same preprocessing pipeline as static images
            # This automatically handles: landmark detection, alignment, resize, normalization
            embedding, preprocessed_img, landmarks = self.embedding_generator.generate_embedding(face_image)
            
            if embedding is None:
                return {
                    'embedding': None,
                    'embedding_path': None,
                    'preprocessed_path': None,
                    'landmarks': None,
                    'success': False
                }
            
            # Save embedding
            embedding_path = os.path.join(self.output_dir, f"{base_name}_embedding.npy")
            np.save(embedding_path, embedding)
            
            # Save preprocessed 112×112 image if enabled
            preprocessed_path = None
            if self.save_preprocessed and preprocessed_img is not None:
                preprocessed_path = os.path.join(self.preprocessed_dir, f"{base_name}_preprocessed_112x112.jpg")
                
                # Ensure correct format for saving
                if preprocessed_img.dtype != np.uint8:
                    if preprocessed_img.min() < 0:
                        preprocessed_img = ((preprocessed_img + 1) * 127.5).astype(np.uint8)
                    else:
                        preprocessed_img = (preprocessed_img * 255).astype(np.uint8)
                
                if preprocessed_img.shape != (112, 112, 3):
                    preprocessed_img = cv2.resize(preprocessed_img, (112, 112))
                
                Image.fromarray(preprocessed_img).save(preprocessed_path)
            
            return {
                'embedding': embedding,
                'embedding_path': embedding_path,
                'preprocessed_path': preprocessed_path,
                'landmarks': landmarks,
                'success': True
            }
            
        except Exception as e:
            print(f"[-] Error generating embedding: {str(e)}")
            return {
                'embedding': None,
                'embedding_path': None,
                'preprocessed_path': None,
                'landmarks': None,
                'success': False,
                'error': str(e)
            }

