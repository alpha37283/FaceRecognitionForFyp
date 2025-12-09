# modules/detection/detectors/mtcnn_detector.py
from facenet_pytorch import MTCNN
from PIL import Image
import numpy as np
from modules.detection.face_detection_base import FaceDetectorBase

class MTCNNDetector(FaceDetectorBase):
    def __init__(self, keep_all=True, device='cpu', min_confidence=0.9, min_face_size=40):
        """Initialize MTCNN detector.
        
        Args:
            keep_all: Whether to return all detected faces
            device: 'cpu' or 'cuda'
            min_confidence: Minimum detection confidence (0-1), default 0.9
            min_face_size: Minimum face size in pixels (width or height), default 40
        """
        self.mtcnn = MTCNN(keep_all=keep_all, device=device, min_face_size=min_face_size)
        self.min_confidence = min_confidence
        self.min_face_size = min_face_size

    def detect_faces(self, image):
        """Detect and crop faces using MTCNN."""
        # Support both file paths and PIL images
        if isinstance(image, str):
            image = Image.open(image).convert("RGB")
        elif isinstance(image, np.ndarray):
            image = Image.fromarray(image)

        # Get both faces and detection info
        boxes, probs = self.mtcnn.detect(image)
        
        if boxes is None or probs is None:
            return []
        
        # Filter by confidence and extract faces
        cropped_faces = []
        for box, prob in zip(boxes, probs):
            # Skip low confidence detections
            if prob < self.min_confidence:
                continue
                
            # Extract face using bounding box
            x1, y1, x2, y2 = [int(coord) for coord in box]
            
            # Check face size (width and height)
            face_width = x2 - x1
            face_height = y2 - y1
            
            # Skip faces that are too small
            if face_width < self.min_face_size or face_height < self.min_face_size:
                continue
            
            # Ensure coordinates are within image bounds
            img_array = np.array(image)
            h, w = img_array.shape[:2]
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(w, x2), min(h, y2)
            
            # Crop face
            face_crop = img_array[y1:y2, x1:x2]
            
            if face_crop.size > 0:
                cropped_faces.append(Image.fromarray(face_crop))
        
        return cropped_faces
    
    def detect_faces_with_boxes(self, image):
        """Detect faces and return bounding boxes for visualization."""
        # Support both file paths and PIL images
        if isinstance(image, str):
            image = Image.open(image).convert("RGB")
        elif isinstance(image, np.ndarray):
            image = Image.fromarray(image)
        
        # Get bounding boxes and probabilities
        boxes, probs = self.mtcnn.detect(image)
        
        if boxes is None or probs is None:
            return []
        
        # Filter by confidence and face size, return list of (box, probability) tuples
        detections = []
        for box, prob in zip(boxes, probs):
            # Check confidence
            if prob < self.min_confidence:
                continue
            
            # Check face size
            x1, y1, x2, y2 = box
            face_width = x2 - x1
            face_height = y2 - y1
            
            if face_width >= self.min_face_size and face_height >= self.min_face_size:
                detections.append((box, prob))
        
        return detections