#!/usr/bin/env python3
import os
import sys

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.append(project_root)

from modules.detection.face_detection_image import detect_faces_from_image
from modules.recognition.arcface_embedding import generate_embeddings_for_cropped_faces
from modules.recognition.upload_to_backend import upload_embedding
from typing import Optional


def process_and_upload_image(
    image_path: str,
    person_name: str,
    detection_method: str = "mtcnn",
    age: Optional[int] = None,
    gender: Optional[str] = None,
    notes: Optional[str] = None,
    api_base_url: Optional[str] = None
):
    print(f"[INFO] Processing image: {image_path}")
    print(f"[INFO] Person: {person_name}")
    print(f"[INFO] Detection method: {detection_method}\n")
    
    print("[STEP 1] Detecting faces...")
    cropped_face_paths = detect_faces_from_image(image_path, method=detection_method, generate_embeddings=False)
    
    if not cropped_face_paths:
        print("[-] No faces detected. Cannot proceed.")
        return None
    
    print(f"[+] Detected {len(cropped_face_paths)} face(s)\n")
    
    print("[STEP 2] Generating embeddings...")
    embedding_results = generate_embeddings_for_cropped_faces(cropped_face_paths, output_dir="data/embeddings", save_preprocessed=True)
    
    if not embedding_results:
        print("[-] Failed to generate embeddings. Cannot proceed.")
        return None
    
    print(f"[+] Generated {len(embedding_results)} embedding(s)\n")
    
    print("[STEP 3] Uploading to backend API...")
    uploaded_results = []
    
    for face_path, result_data in embedding_results.items():
        try:
            base_name = os.path.splitext(os.path.basename(face_path))[0]
            source_url = face_path
            preprocessed_url = result_data.get('preprocessed_path')
            
            upload_result = upload_embedding(
                person_name=person_name,
                embedding_vector=result_data['embedding'].tolist(),
                age=age,
                gender=gender,
                notes=notes,
                source_image_url=source_url,
                preprocessed_image_url=preprocessed_url,
                detection_method=detection_method,
                api_base_url=api_base_url
            )
            
            uploaded_results.append(upload_result)
            print(f"[+] Uploaded embedding ID: {upload_result['embedding_id']}")
            
        except Exception as e:
            print(f"[-] Failed to upload embedding for {os.path.basename(face_path)}: {str(e)}")
            continue
    
    print()
    print(f"[+] Successfully uploaded {len(uploaded_results)} embedding(s) to backend")
    return uploaded_results


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Process image and upload embedding to backend")
    parser.add_argument("--image", required=True, help="Path to input image")
    parser.add_argument("--name", required=True, help="Person's name")
    parser.add_argument("--method", default="mtcnn", choices=["mtcnn", "retinaface"], help="Detection method")
    parser.add_argument("--age", type=int, help="Person's age")
    parser.add_argument("--gender", choices=["M", "F", "Other"], help="Person's gender")
    parser.add_argument("--notes", help="Additional notes")
    parser.add_argument("--api-url", help="Backend API URL (default: http://localhost:8000)")
    
    args = parser.parse_args()
    
    # Check if backend API is running
    import requests
    try:
        response = requests.get(args.api_url or "http://localhost:8000", timeout=2)
        print("[INFO] Backend API is running")
    except:
        print("[-] WARNING: Backend API is not running!")
        print("[-] Please start the backend API first: ./run_backend.sh")
        sys.exit(1)
    
    process_and_upload_image(
        image_path=args.image,
        person_name=args.name,
        detection_method=args.method,
        age=args.age,
        gender=args.gender,
        notes=args.notes,
        api_base_url=args.api_url
    )

