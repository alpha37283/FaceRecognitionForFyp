# modules/detection/face_detection_image.py
import os
from modules.detectors.mtcnn_detector import MTCNNDetector

def detect_faces_from_image(image_path, method="mtcnn"):
    """Detect and save faces from a static image."""
    if not os.path.exists(image_path):
        print(f"[-] Image not found: {image_path}")
        return []

    if method.lower() != "mtcnn":
        raise ValueError(f"Unsupported method for now: {method}")

    detector = MTCNNDetector()
    faces = detector.detect_faces(image_path)

    if not faces:
        print("[-] No faces detected.")
        return []

    saved_paths = detector.save_faces(faces)
    print(f"[+] Saved {len(saved_paths)} face(s) to data/cropped_faces/")
    return saved_paths
