# modules/detection/face_detection_base.py
from abc import ABC, abstractmethod
from PIL import Image
import os

class FaceDetectorBase(ABC):
    """Abstract base class for all face detectors."""

    @abstractmethod
    def detect_faces(self, image):
        """Return list of cropped face images (PIL or ndarray)."""
        pass

    def save_faces(self, faces, output_dir="data/cropped_faces"):
        """Save cropped faces to output directory."""
        os.makedirs(output_dir, exist_ok=True)
        saved_paths = []
        for i, face in enumerate(faces):
            face_path = os.path.join(output_dir, f"face_{i+1}.jpg")
            if isinstance(face, Image.Image):
                face.save(face_path)
            else:
                Image.fromarray(face).save(face_path)
            saved_paths.append(face_path)
        return saved_paths
