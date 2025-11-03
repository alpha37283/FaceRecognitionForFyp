# modules/detection/face_detection_image.py
import os
from modules.detectors.mtcnn_detector import MTCNNDetector
from modules.detectors.retinaface_detector import RetinaFaceDetector

def detect_faces_from_image(image_path, method="mtcnn"):
    """Detect and save faces from a static image."""
    if not os.path.exists(image_path):
        print(f"[-] Image not found: {image_path}")
        return []

    # Initialize the appropriate detector
    if method.lower() == "mtcnn":
        detector = MTCNNDetector()
    elif method.lower() == "retinaface":
        detector = RetinaFaceDetector()
    else:
        raise ValueError(f"Unsupported method: {method}. Use 'mtcnn' or 'retinaface'")

    faces = detector.detect_faces(image_path)

    if not faces:
        print("[-] No faces detected.")
        return []

    # Pass source image name for unique filenames
    saved_paths = detector.save_faces(faces, source_name=image_path)
    print(f"[+] Saved {len(saved_paths)} face(s) to data/cropped_faces/")
    
    # Show saved filenames
    for path in saved_paths:
        print(f"    - {os.path.basename(path)}")
    
    return saved_paths
