# modules/recognition/arcface_embedding.py
"""
ArcFace Embedding Generation Module

This module handles the complete ArcFace preprocessing pipeline:
1. Face Detection (already done - cropped faces provided)
2. Landmark Detection (5-point: left eye, right eye, nose tip, left mouth corner, right mouth corner)
3. Face Alignment (affine transformation to 112×112 template)
4. Resize to 112×112
5. Normalize pixel values to [-1, 1] range
6. Generate embeddings

All preprocessing steps (2-5) are handled automatically by InsightFace.
"""
import os
import cv2
import numpy as np
from PIL import Image
from insightface.app import FaceAnalysis
from datetime import datetime


class ArcFaceEmbeddingGenerator:
    """Generates ArcFace embeddings with automatic preprocessing."""
    
    def __init__(self, provider='CPUExecutionProvider'):
        """
        Initialize ArcFace embedding generator.
        
        Args:
            provider: ONNX runtime provider ('CPUExecutionProvider' or 'CUDAExecutionProvider')
        """
        print("[INFO] Initializing ArcFace embedding generator...")
        # Initialize FaceAnalysis with recognition model
        # This automatically handles all preprocessing steps
        self.app = FaceAnalysis(providers=[provider])
        self.app.prepare(ctx_id=0, det_size=(640, 640))
        print("[INFO] ArcFace model loaded successfully.")
    
    def _pad_cropped_face(self, img, padding_ratio=0.3):
        """
        Pad a cropped face image to give context for better landmark detection.
        
        Args:
            img: BGR image (numpy array)
            padding_ratio: Ratio of padding to add (0.3 = 30% padding on each side)
            
        Returns:
            Padded BGR image
        """
        h, w = img.shape[:2]
        
        # Calculate padding
        pad_h = int(h * padding_ratio)
        pad_w = int(w * padding_ratio)
        
        # Create padded image with black background
        padded = np.zeros((h + 2*pad_h, w + 2*pad_w, 3), dtype=img.dtype)
        
        # Place original image in center
        padded[pad_h:pad_h+h, pad_w:pad_w+w] = img
        
        return padded
    
    def generate_embedding(self, face_image):
        """
        Generate embedding for a single face image.
        
        ArcFace preprocessing pipeline (automatic via InsightFace):
        1. Landmark Detection (5-point: left eye, right eye, nose tip, left mouth, right mouth)
        2. Face Alignment (affine transformation to 112×112 template)
        3. Resize to 112×112
        4. Normalize to [-1, 1]: (pixel - 127.5) / 128
        5. Generate embedding
        
        Args:
            face_image: PIL Image or numpy array or file path (can be cropped face)
            
        Returns:
            tuple: (embedding, preprocessed_image, landmarks)
                - embedding: numpy array of shape (512,) or (256,) depending on model
                - preprocessed_image: numpy array of shape (112, 112, 3) - aligned and normalized
                - landmarks: 5-point landmarks if available, None otherwise
        """
        # Convert input to numpy array (BGR format for OpenCV/InsightFace)
        if isinstance(face_image, str):
            # Load from file path
            img = cv2.imread(face_image)
            if img is None:
                raise ValueError(f"Could not load image: {face_image}")
        elif isinstance(face_image, Image.Image):
            # Convert PIL to numpy (RGB -> BGR for InsightFace)
            img = np.array(face_image)
            if len(img.shape) == 2:
                img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
            else:
                img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        elif isinstance(face_image, np.ndarray):
            img = face_image.copy()
            # Ensure BGR format
            if len(img.shape) == 2:
                img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
            elif img.shape[2] == 3:
                # Assume RGB, convert to BGR
                img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        else:
            raise TypeError(f"Unsupported image type: {type(face_image)}")
        
        # For cropped faces, pad the image to give context for better landmark detection
        # This helps InsightFace detect landmarks more accurately
        h, w = img.shape[:2]
        original_img = img.copy()
        
        # Try detection first without padding
        faces = self.app.get(img)
        
        # If no face detected, try with padding (cropped faces often need context)
        if not faces:
            # Pad the image to give context
            img = self._pad_cropped_face(original_img, padding_ratio=0.3)
            faces = self.app.get(img)
            
            # If still no face, try with more padding
            if not faces:
                img = self._pad_cropped_face(original_img, padding_ratio=0.5)
                faces = self.app.get(img)
            
            # If still no face, try with even more padding
            if not faces:
                img = self._pad_cropped_face(original_img, padding_ratio=0.8)
                faces = self.app.get(img)
            
            if not faces:
                return None, None, None
        
        # InsightFace automatically performs all preprocessing steps:
        # 1. Landmark detection (5-point or 106-point, extracts 5 key points)
        # 2. Face alignment (affine transformation based on landmarks)
        # 3. Resize to 112×112
        # 4. Normalization to [-1, 1] range
        # 5. Embedding generation
        
        # Get the first (most confident) face
        face = faces[0]
        
        # Extract normalized embedding (already preprocessed)
        # This is the final embedding vector ready for comparison
        embedding = face.normed_embedding  # Shape: (512,) or (256,) depending on model
        
        # Get landmarks (106-point or 5-point depending on model)
        landmarks = None
        if hasattr(face, 'landmark_2d_106'):
            landmarks = face.landmark_2d_106
        elif hasattr(face, 'kps'):  # 5-point landmarks
            landmarks = face.kps
        
        # Get preprocessed/aligned face image (112×112)
        # InsightFace provides norm_crop which is the aligned and preprocessed face
        preprocessed_img = None
        if hasattr(face, 'norm_crop') and face.norm_crop is not None:
            # norm_crop is the aligned 112×112 face (BGR format, [0, 255] range)
            preprocessed_img = face.norm_crop.copy()
            # Convert BGR to RGB for saving
            preprocessed_img = cv2.cvtColor(preprocessed_img, cv2.COLOR_BGR2RGB)
        elif hasattr(face, 'bbox'):
            # Fallback: use bbox to crop and resize (but this won't be aligned)
            # This is a fallback if norm_crop is not available
            x1, y1, x2, y2 = map(int, face.bbox)
            # Ensure bbox is within image bounds
            h_img, w_img = img.shape[:2]
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(w_img, x2), min(h_img, y2)
            
            if x2 > x1 and y2 > y1:
                preprocessed_img = img[y1:y2, x1:x2]
                preprocessed_img = cv2.resize(preprocessed_img, (112, 112))
                preprocessed_img = cv2.cvtColor(preprocessed_img, cv2.COLOR_BGR2RGB)
            else:
                # If bbox is invalid, create a placeholder
                preprocessed_img = np.zeros((112, 112, 3), dtype=np.uint8)
        else:
            # Last resort: create a placeholder
            preprocessed_img = np.zeros((112, 112, 3), dtype=np.uint8)
        
        return embedding, preprocessed_img, landmarks
    
    def generate_embeddings_from_files(self, face_file_paths, output_dir="data/embeddings", save_preprocessed=True):
        """
        Generate embeddings for multiple cropped face images.
        
        Args:
            face_file_paths: List of file paths to cropped face images
            output_dir: Directory to save embeddings and preprocessed images
            save_preprocessed: Whether to save preprocessed 112×112 images
            
        Returns:
            dict: Mapping of face file path to embedding data
                {
                    'face_path': {
                        'embedding': np.array,
                        'preprocessed_path': str or None,
                        'landmarks': np.array or None
                    }
                }
        """
        os.makedirs(output_dir, exist_ok=True)
        
        if save_preprocessed:
            preprocessed_dir = os.path.join(output_dir, "preprocessed")
            os.makedirs(preprocessed_dir, exist_ok=True)
        
        results = {}
        successful = 0
        failed = 0
        
        print(f"[INFO] Generating embeddings for {len(face_file_paths)} face(s)...")
        
        for face_path in face_file_paths:
            try:
                embedding, preprocessed_img, landmarks = self.generate_embedding(face_path)
                
                if embedding is None:
                    print(f"[-] Failed to generate embedding for: {os.path.basename(face_path)}")
                    failed += 1
                    continue
                
                # Save embedding as numpy file
                base_name = os.path.splitext(os.path.basename(face_path))[0]
                embedding_path = os.path.join(output_dir, f"{base_name}_embedding.npy")
                np.save(embedding_path, embedding)
                
                # Save preprocessed image if requested
                preprocessed_path = None
                if save_preprocessed and preprocessed_img is not None:
                    # Get base name from original face file
                    preprocessed_path = os.path.join(preprocessed_dir, f"{base_name}_preprocessed_112x112.jpg")
                    # preprocessed_img from InsightFace is already in [0, 255] uint8 format
                    # Just ensure it's the right type and save
                    if preprocessed_img.dtype != np.uint8:
                        if preprocessed_img.min() < 0:
                            # Normalized [-1, 1], convert back to [0, 255]
                            preprocessed_img = ((preprocessed_img + 1) * 127.5).astype(np.uint8)
                        else:
                            preprocessed_img = (preprocessed_img * 255).astype(np.uint8)
                    # Ensure shape is (112, 112, 3)
                    if preprocessed_img.shape != (112, 112, 3):
                        preprocessed_img = cv2.resize(preprocessed_img, (112, 112))
                    Image.fromarray(preprocessed_img).save(preprocessed_path)
                
                results[face_path] = {
                    'embedding': embedding,
                    'embedding_path': embedding_path,
                    'preprocessed_path': preprocessed_path,
                    'landmarks': landmarks
                }
                
                successful += 1
                
            except Exception as e:
                import traceback
                print(f"[-] Error processing {os.path.basename(face_path)}: {str(e)}")
                print(f"    Details: {traceback.format_exc()}")
                failed += 1
                continue
        
        print(f"[+] Successfully generated {successful} embedding(s)")
        if failed > 0:
            print(f"[-] Failed to generate {failed} embedding(s)")
        
        return results


def generate_embeddings_for_cropped_faces(cropped_face_paths, output_dir="data/embeddings", save_preprocessed=True):
    """
    Convenience function to generate embeddings for cropped faces.
    
    Args:
        cropped_face_paths: List of paths to cropped face images
        output_dir: Directory to save embeddings
        save_preprocessed: Whether to save preprocessed images
        
    Returns:
        dict: Results dictionary from generate_embeddings_from_files
    """
    generator = ArcFaceEmbeddingGenerator()
    return generator.generate_embeddings_from_files(
        cropped_face_paths,
        output_dir=output_dir,
        save_preprocessed=save_preprocessed
    )

