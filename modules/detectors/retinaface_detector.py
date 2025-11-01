 # modules/detection/detectors/retinaface_detector.py
from insightface.app import FaceAnalysis
import cv2
from PIL import Image
from modules.detection.face_detection_base import FaceDetectorBase

class RetinaFaceDetector(FaceDetectorBase):
    def __init__(self, provider='CPUExecutionProvider'):
        self.app = FaceAnalysis(providers=[provider])
        self.app.prepare(ctx_id=0)

    def detect_faces(self, image):
        """Detect and crop faces using RetinaFace."""
        if isinstance(image, str):
            image = cv2.imread(image)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        faces = self.app.get(image)
        cropped_faces = []
        for face in faces:
            x1, y1, x2, y2 = map(int, face.bbox)
            cropped = image[y1:y2, x1:x2]
            cropped_faces.append(Image.fromarray(cropped))
        return cropped_faces
