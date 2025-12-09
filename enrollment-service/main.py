# main.py
# Enrollment Service - Static Image Face Detection and Embedding Generation
import os
import sys

project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.append(project_root)

import argparse
from modules.detection.face_detection_image import detect_faces_from_image

def main():
    parser = argparse.ArgumentParser(description="Static Image Face Detection and Embedding Generation")
    parser.add_argument("--input", type=str, required=True,
                       help="Path to input image file")
    parser.add_argument("--method", type=str, default="mtcnn", choices=["mtcnn", "retinaface"],
                       help="Face detection method")
    parser.add_argument("--embed", action="store_true",
                       help="Generate ArcFace embeddings after face detection")
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"[-] Error: Image file not found: {args.input}")
        return

    print(f"[INFO] Running face detection on image: {args.input}")
    detect_faces_from_image(args.input, method=args.method, generate_embeddings=args.embed)

if __name__ == "__main__":
    main()

