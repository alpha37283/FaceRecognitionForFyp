# main.py
# Edge Recognition Service - Live Camera Feed with Face Recognition
import os
import sys

project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.append(project_root)

import argparse
from modules.detection.face_detection_live import live_face_detection

def main():
    parser = argparse.ArgumentParser(description="Live Camera Face Detection and Recognition")
    parser.add_argument("--method", type=str, default="mtcnn", choices=["mtcnn", "retinaface"],
                       help="Face detection method")
    parser.add_argument("--embed", action="store_true", 
                       help="Generate ArcFace embeddings for detected faces")
    parser.add_argument("--recognize", action="store_true",
                       help="Enable face recognition - compare live faces with synced embeddings")
    parser.add_argument("--similarity-threshold", type=float, default=0.6,
                       help="Minimum cosine similarity for recognition match (default: 0.6)")
    parser.add_argument("--detection-interval", type=int, default=60,
                       help="Run face detection every N frames (default: 60)")
    parser.add_argument("--iou-threshold", type=float, default=0.5,
                       help="IoU threshold for face tracking (default: 0.5)")
    args = parser.parse_args()

    print("[INFO] Starting live camera face detection...")
    live_face_detection(
        method=args.method,
        detection_interval=args.detection_interval,
        iou_threshold=args.iou_threshold,
        generate_embeddings=args.embed or args.recognize,  # Auto-enable embeddings if recognition is on
        enable_recognition=args.recognize,
        similarity_threshold=args.similarity_threshold
    )

if __name__ == "__main__":
    main()
