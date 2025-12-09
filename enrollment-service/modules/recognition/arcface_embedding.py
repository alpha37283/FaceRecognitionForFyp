# modules/recognition/arcface_embedding.py
import os
import cv2
import numpy as np
from PIL import Image
from insightface.app import FaceAnalysis
from datetime import datetime


class ArcFaceEmbeddingGenerator:
    def __init__(self, provider='CPUExecutionProvider'):
        print("[INFO] Initializing ArcFace embedding generator...")
        self.app = FaceAnalysis(providers=[provider])
        self.app.prepare(ctx_id=0, det_size=(640, 640))
        print("[INFO] ArcFace model loaded successfully.")
    
    def _pad_cropped_face(self, img, padding_ratio=0.3):
        h, w = img.shape[:2]
        pad_h = int(h * padding_ratio)
        pad_w = int(w * padding_ratio)
        padded = np.zeros((h + 2*pad_h, w + 2*pad_w, 3), dtype=img.dtype)
        padded[pad_h:pad_h+h, pad_w:pad_w+w] = img
        return padded
    
    def generate_embedding(self, face_image):
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
        
        h, w = img.shape[:2]
        original_img = img.copy()
        faces = self.app.get(img)
        
        if not faces:
            img = self._pad_cropped_face(original_img, padding_ratio=0.3)
            faces = self.app.get(img)
            if not faces:
                img = self._pad_cropped_face(original_img, padding_ratio=0.5)
                faces = self.app.get(img)
            if not faces:
                img = self._pad_cropped_face(original_img, padding_ratio=0.8)
                faces = self.app.get(img)
            if not faces:
                return None, None, None
        
        face = faces[0]
        embedding = face.normed_embedding
        
        landmarks = None
        if hasattr(face, 'landmark_2d_106'):
            landmarks = face.landmark_2d_106
        elif hasattr(face, 'kps'):
            landmarks = face.kps
        
        preprocessed_img = None
        if hasattr(face, 'norm_crop') and face.norm_crop is not None:
            preprocessed_img = face.norm_crop.copy()
            preprocessed_img = cv2.cvtColor(preprocessed_img, cv2.COLOR_BGR2RGB)
        elif hasattr(face, 'bbox'):
            x1, y1, x2, y2 = map(int, face.bbox)
            h_img, w_img = img.shape[:2]
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(w_img, x2), min(h_img, y2)
            if x2 > x1 and y2 > y1:
                preprocessed_img = img[y1:y2, x1:x2]
                preprocessed_img = cv2.resize(preprocessed_img, (112, 112))
                preprocessed_img = cv2.cvtColor(preprocessed_img, cv2.COLOR_BGR2RGB)
            else:
                preprocessed_img = np.zeros((112, 112, 3), dtype=np.uint8)
        else:
            preprocessed_img = np.zeros((112, 112, 3), dtype=np.uint8)
        
        return embedding, preprocessed_img, landmarks
    
    def generate_embeddings_from_files(self, face_file_paths, output_dir="data/embeddings", save_preprocessed=True):
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
                
                base_name = os.path.splitext(os.path.basename(face_path))[0]
                embedding_path = os.path.join(output_dir, f"{base_name}_embedding.npy")
                np.save(embedding_path, embedding)
                
                preprocessed_path = None
                if save_preprocessed and preprocessed_img is not None:
                    preprocessed_path = os.path.join(preprocessed_dir, f"{base_name}_preprocessed_112x112.jpg")
                    if preprocessed_img.dtype != np.uint8:
                        if preprocessed_img.min() < 0:
                            preprocessed_img = ((preprocessed_img + 1) * 127.5).astype(np.uint8)
                        else:
                            preprocessed_img = (preprocessed_img * 255).astype(np.uint8)
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
                print(f"[-] Error processing {os.path.basename(face_path)}: {str(e)}")
                failed += 1
                continue
        
        print(f"[+] Successfully generated {successful} embedding(s)")
        if failed > 0:
            print(f"[-] Failed to generate {failed} embedding(s)")
        
        return results


def generate_embeddings_for_cropped_faces(cropped_face_paths, output_dir="data/embeddings", save_preprocessed=True):
    generator = ArcFaceEmbeddingGenerator()
    return generator.generate_embeddings_from_files(
        cropped_face_paths,
        output_dir=output_dir,
        save_preprocessed=save_preprocessed
    )

