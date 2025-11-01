# modules/detection/detectors/mtcnn_detector.py
from facenet_pytorch import MTCNN
from PIL import Image
import numpy as np
from modules.detection.face_detection_base import FaceDetectorBase

class MTCNNDetector(FaceDetectorBase):
    def __init__(self, keep_all=True, device='cpu'):
        self.mtcnn = MTCNN(keep_all=keep_all, device=device)

    def detect_faces(self, image):
        """Detect and crop faces using MTCNN."""
        # Support both file paths and PIL images
        if isinstance(image, str):
            image = Image.open(image).convert("RGB")

        faces = self.mtcnn(image)
        if faces is None:
            return []

        # Convert from Torch tensors to NumPy arrays (HWC)
        cropped_faces = [np.uint8(face.permute(1, 2, 0).cpu().numpy()) for face in faces]
        return cropped_faces
    
    def detect_faces_with_boxes(self, image):
        """Detect faces and return bounding boxes for visualization."""
        # Support both file paths and PIL images
        if isinstance(image, str):
            image = Image.open(image).convert("RGB")
        
        # Get bounding boxes and probabilities
        boxes, probs = self.mtcnn.detect(image)
        
        if boxes is None:
            return []
        
        # Return list of (box, probability) tuples
        return [(box, prob) for box, prob in zip(boxes, probs)]