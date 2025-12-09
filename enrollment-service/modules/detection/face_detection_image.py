# modules/detection/face_detection_image.py
import os
from modules.detectors.mtcnn_detector import MTCNNDetector
from modules.detectors.retinaface_detector import RetinaFaceDetector

def detect_faces_from_image(image_path, method="mtcnn", generate_embeddings=False):
    """
    Detect and save faces from a static image.
    
    Args:
        image_path: Path to input image
        method: Detection method ('mtcnn' or 'retinaface')
        generate_embeddings: If True, generate ArcFace embeddings after detection
        
    Returns:
        list: Paths to saved cropped faces
    """
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
    
    # Generate embeddings if requested
    if generate_embeddings:
        print("\n[INFO] Generating ArcFace embeddings...")
        try:
            from modules.recognition.arcface_embedding import generate_embeddings_for_cropped_faces
            
            # Generate embeddings for all cropped faces
            embedding_results = generate_embeddings_for_cropped_faces(
                saved_paths,
                output_dir="data/embeddings",
                save_preprocessed=True
            )
            
            print(f"[+] Generated {len(embedding_results)} embedding(s)")
            print(f"[+] Embeddings saved to: data/embeddings/")
            print(f"[+] Preprocessed images saved to: data/embeddings/preprocessed/")
            
        except Exception as e:
            print(f"[-] Error generating embeddings: {str(e)}")
            print("[-] Continuing without embeddings...")
    
    return saved_paths
