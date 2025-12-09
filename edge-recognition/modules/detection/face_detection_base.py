# modules/detection/face_detection_base.py
from abc import ABC, abstractmethod
from PIL import Image
import os
from datetime import datetime

class FaceDetectorBase(ABC):
    """Abstract base class for all face detectors."""

    @abstractmethod
    def detect_faces(self, image):
        """Return list of cropped face images (PIL or ndarray)."""
        pass

    def save_faces(self, faces, output_dir="data/cropped_faces", source_name=None):
        """Save cropped faces to output directory with unique filenames.
        
        Args:
            faces: List of face images to save
            output_dir: Directory to save faces
            source_name: Optional source image name (for unique filenames)
        """
        os.makedirs(output_dir, exist_ok=True)
        saved_paths = []
        
        # Generate timestamp for this batch
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Extract base name from source if provided
        if source_name:
            # Get filename without path and extension
            base_name = os.path.splitext(os.path.basename(source_name))[0]
            prefix = f"{base_name}_{timestamp}"
        else:
            # Fallback to simple timestamp
            prefix = f"face_{timestamp}"
        
        for i, face in enumerate(faces):
            # Create unique filename: sourcename_timestamp_faceN.jpg
            face_path = os.path.join(output_dir, f"{prefix}_face{i+1}.jpg")
            
            if isinstance(face, Image.Image):
                face.save(face_path)
            else:
                Image.fromarray(face).save(face_path)
            
            saved_paths.append(face_path)
        
        return saved_paths
