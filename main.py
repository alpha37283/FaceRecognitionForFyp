# main.py
import os
import sys

project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.append(project_root)

import argparse
from modules.detection.face_detection_image import detect_faces_from_image
from modules.detection.face_detection_live import live_face_detection

def main():
    parser = argparse.ArgumentParser(description="Face Detection Module Runner")
    parser.add_argument("--mode", type=str, choices=["image", "live"], required=True)
    parser.add_argument("--method", type=str, default="mtcnn", choices=["mtcnn", "retinaface"])
    parser.add_argument("--input", type=str, default=None)
    parser.add_argument("--embed", action="store_true", 
                       help="Generate ArcFace embeddings after face detection (image mode only)")
    args = parser.parse_args()

    if args.mode == "image":
        if not args.input:
            print("[-] Please specify an input image path using --input")
            return
        print(f"[INFO] Running face detection on image: {args.input}")
        detect_faces_from_image(args.input, method=args.method, generate_embeddings=args.embed)

    elif args.mode == "live":
        print("[INFO] Starting live camera face detection...")
        live_face_detection(method=args.method)

if __name__ == "__main__":
    main()
