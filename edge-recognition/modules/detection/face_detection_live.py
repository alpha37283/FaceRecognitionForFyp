# modules/detection/face_detection_live.py
import cv2
import os
from PIL import Image
from datetime import datetime
from modules.detectors.mtcnn_detector import MTCNNDetector
from modules.detectors.retinaface_detector import RetinaFaceDetector

class FaceTracker:
    """Represents a tracked face with unique ID."""
    
    def __init__(self, tracker_id, bbox, frame):
        self.id = tracker_id
        self.bbox = bbox
        self.saved = False
        self.recognized_name = None  # Store recognized name
        self.last_recognition_frame = 0  # Track when last recognized
        
        # Create OpenCV tracker (KCF is fast and reliable)
        self.tracker = cv2.TrackerKCF_create()
        
        # Initialize tracker with the bounding box
        self.tracker.init(frame, tuple(bbox))
    
    def update(self, frame):
        """Update tracker position. Returns (success, bbox)."""
        success, bbox = self.tracker.update(frame)
        if success:
            self.bbox = [int(v) for v in bbox]
        return success, self.bbox


def live_face_detection(method="mtcnn", detection_interval=60, iou_threshold=0.5, generate_embeddings=False, enable_recognition=False, similarity_threshold=0.6):
    """Live face detection with automatic tracking-based saving and optional embedding generation.
    
    Algorithm: Tracking + Save-on-New-Track
    - Detects faces periodically
    - Assigns unique tracker to each new face
    - Saves face once when first tracked
    - Generates ArcFace embeddings with same preprocessing as static images (if enabled)
    - Tracks continuously until face leaves frame
    - New detection when tracking is lost
    
    Args:
        method: Detection method ('mtcnn' or 'retinaface')
        detection_interval: Run face detection every N frames (default: 60, ~2 seconds)
        iou_threshold: Minimum overlap to consider same face (default: 0.5, range: 0.3-0.7)
        generate_embeddings: If True, generate ArcFace embeddings for detected faces (default: False)
        enable_recognition: If True, compare faces with synced embeddings and recognize (default: False)
        similarity_threshold: Minimum cosine similarity for recognition match (default: 0.6)
    """
    # Initialize the appropriate detector
    print(f"[INFO] Initializing {method.upper()} face detector...")
    
    if method.lower() == "mtcnn":
        detector = MTCNNDetector()
    elif method.lower() == "retinaface":
        detector = RetinaFaceDetector()
    else:
        raise ValueError(f"Unsupported method: {method}. Use 'mtcnn' or 'retinaface'")
    
    # Initialize live embedding generator (required for recognition)
    live_embedding_gen = None
    if generate_embeddings or enable_recognition:
        from modules.recognition.live_embedding import LiveEmbeddingGenerator
        live_embedding_gen = LiveEmbeddingGenerator(
            output_dir="data/embeddings",
            save_preprocessed=True
        )
    
    # Initialize face matcher for recognition
    face_matcher = None
    log_file = None
    if enable_recognition:
        from modules.recognition.face_matcher import FaceMatcher
        from modules.recognition.sync_embeddings import EmbeddingSyncClient
        
        face_matcher = FaceMatcher(similarity_threshold=similarity_threshold)
        
        # Load synced embeddings for comparison
        print("[INFO] Loading synced embeddings for recognition...")
        sync_client = EmbeddingSyncClient(
            api_base_url="http://localhost:8001",
            local_cache_dir="data/local_embeddings"
        )
        synced_embeddings = sync_client.get_local_embeddings()
        face_matcher.load_synced_embeddings(synced_embeddings)
        print(f"[INFO] Loaded {len(synced_embeddings)} synced embedding(s) for recognition")
        
        # Setup log file for recognition matches
        log_dir = "data/recognition_logs"
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, f"recognition_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
        print(f"[INFO] Recognition logs will be saved to: {log_file}")
    
    # Create output directory if it doesn't exist
    output_dir = "data/cropped_faces"
    os.makedirs(output_dir, exist_ok=True)

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[-] Could not access the webcam.")
        return

    print("\n" + "="*60)
    print("  🎯 FACE TRACKING & AUTO-SAVE SYSTEM")
    print("="*60)
    print("📹 How it works:")
    print("   ✅ Detects new faces automatically")
    print("   ✅ Tracks each face with unique ID")
    print("   ✅ Saves ONE image per person (when first detected)")
    if generate_embeddings:
        print("   ✅ Generates ArcFace embeddings with full preprocessing")
        print("   ✅ Saves preprocessed 112×112 images")
    print("   ✅ Continues tracking until face leaves frame")
    print("   ✅ New faces get new IDs and are saved")
    print(f"\n⚙️  Settings:")
    print(f"   - Detection method: {method.upper()}")
    print(f"   - Detection interval: {detection_interval} frames (~{detection_interval/30:.1f}s)")
    print(f"   - IoU threshold: {iou_threshold} (overlap matching)")
    print(f"   - Tracker: KCF (Fast & Reliable)")
    print(f"   - Embedding generation: {'ENABLED' if generate_embeddings else 'DISABLED'}")
    print(f"   - Face recognition: {'ENABLED' if enable_recognition else 'DISABLED'}")
    if enable_recognition:
        print(f"   - Similarity threshold: {similarity_threshold}")
    print("\n🎮 Controls:")
    print("   - Press 'q' to quit")
    print("="*60 + "\n")

    # Tracking state
    active_trackers = []  # List of FaceTracker objects
    next_tracker_id = 1
    frame_count = 0
    total_saved = 0
    total_embeddings = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1
        display_frame = frame.copy()

        # Update all active trackers
        trackers_to_remove = []
        for tracker in active_trackers:
            success, bbox = tracker.update(frame)
            
            if success:
                x, y, w, h = bbox
                
                # Draw tracking box (red if recognized, blue if unknown)
                if tracker.recognized_name:
                    cv2.rectangle(display_frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                    cv2.putText(display_frame, tracker.recognized_name, (x, y - 10),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                else:
                    cv2.rectangle(display_frame, (x, y), (x + w, y + h), (255, 165, 0), 2)
                    label = f"ID-{tracker.id} (Tracking)"
                    cv2.putText(display_frame, label, (x, y - 10),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 165, 0), 2)
            else:
                # Tracking lost, mark for removal
                trackers_to_remove.append(tracker)
                print(f"[INFO] Lost track of ID-{tracker.id}")
        
        # Remove lost trackers
        for tracker in trackers_to_remove:
            active_trackers.remove(tracker)

        # Run face detection periodically to find new faces
        if frame_count % detection_interval == 0:
            # Convert to RGB for MTCNN
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(frame_rgb)
            
            # Detect faces
            detections = detector.detect_faces_with_boxes(image)
            
            for box, prob in detections:
                x1, y1, x2, y2 = [int(coord) for coord in box]
                detected_bbox = [x1, y1, x2 - x1, y2 - y1]  # Convert to (x, y, w, h)
                
                # Check if this face is already being tracked
                is_tracked = False
                for tracker in active_trackers:
                    # Calculate overlap using IoU (Intersection over Union)
                    tx, ty, tw, th = tracker.bbox
                    
                    # Calculate intersection
                    ix1 = max(x1, tx)
                    iy1 = max(y1, ty)
                    ix2 = min(x2, tx + tw)
                    iy2 = min(y2, ty + th)
                    
                    if ix1 < ix2 and iy1 < iy2:
                        intersection = (ix2 - ix1) * (iy2 - iy1)
                        area1 = (x2 - x1) * (y2 - y1)
                        area2 = tw * th
                        union = area1 + area2 - intersection
                        iou = intersection / union if union > 0 else 0
                        
                        # Use configurable IoU threshold (higher = more strict matching)
                        if iou > iou_threshold:
                            is_tracked = True
                            break
                
                # If not tracked, create new tracker and save face
                if not is_tracked:
                    # Create new tracker
                    new_tracker = FaceTracker(next_tracker_id, detected_bbox, frame)
                    active_trackers.append(new_tracker)
                    
                    # Save the face image
                    face_crop = frame_rgb[y1:y2, x1:x2]
                    if face_crop.size > 0:
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"tracked_face_ID{next_tracker_id}_{timestamp}.jpg"
                        filepath = os.path.join(output_dir, filename)
                        
                        face_pil = Image.fromarray(face_crop)
                        face_pil.save(filepath)
                        
                        total_saved += 1
                        new_tracker.saved = True
                        
                        # Generate embedding and recognize IMMEDIATELY (if enabled)
                        recognized_name = None
                        recognized_age = None
                        similarity_score = None
                        
                        if (generate_embeddings or enable_recognition) and live_embedding_gen:
                            base_name = os.path.splitext(filename)[0]
                            result = live_embedding_gen.generate_embedding_for_face(face_pil, base_name=base_name)
                            
                            if result['success']:
                                total_embeddings += 1
                                embedding = result['embedding']
                                
                                if generate_embeddings:
                                    print(f"[+] Generated embedding for ID-{next_tracker_id} | Embedding: {os.path.basename(result['embedding_path'])}")
                                
                                # Recognize face IMMEDIATELY if enabled
                                if enable_recognition and face_matcher:
                                    match = face_matcher.match_face(embedding)
                                    if match:
                                        recognized_name = match['person_name']
                                        recognized_age = match['person_age']
                                        similarity_score = match['similarity']
                                        
                                        # Store recognized name in tracker for display
                                        new_tracker.recognized_name = recognized_name
                                        
                                        # Log to console (name + age)
                                        age_str = f", Age: {recognized_age}" if recognized_age else ""
                                        print(f"[RECOGNIZED] ID-{next_tracker_id}: {recognized_name}{age_str} (Similarity: {similarity_score:.3f})")
                                        
                                        # Save to log file (name + age)
                                        try:
                                            with open(log_file, 'a') as f:
                                                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                                age_log = f", Age: {recognized_age}" if recognized_age else ""
                                                f.write(f"[{timestamp}] ID-{next_tracker_id}: {recognized_name}{age_log}, Similarity: {similarity_score:.3f}\n")
                                        except Exception as e:
                                            print(f"[-] Error writing to log file: {e}")
                            else:
                                print(f"[-] Failed to generate embedding for ID-{next_tracker_id}")
                        
                        print(f"[+] NEW FACE DETECTED! Saved as ID-{next_tracker_id} | File: {filename} | Total: {total_saved}")
                    
                    # Draw detection box (green for newly detected, red if recognized)
                    if recognized_name:
                        # Recognized person - red box
                        cv2.rectangle(display_frame, (x1, y1), (x2, y2), (0, 0, 255), 3)
                        # Display name on overlay
                        label = recognized_name
                        cv2.putText(display_frame, label, (x1, y1 - 10),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    else:
                        # Unknown person - green box
                        cv2.rectangle(display_frame, (x1, y1), (x2, y2), (0, 255, 0), 3)
                        label = f"NEW: ID-{next_tracker_id}"
                        cv2.putText(display_frame, label, (x1, y1 - 30),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    
                    next_tracker_id += 1

        # Display info on screen
        status_text = f"Active Tracks: {len(active_trackers)} | Saved: {total_saved}"
        if generate_embeddings:
            status_text += f" | Embeddings: {total_embeddings}"
        cv2.putText(display_frame, status_text, 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        
        # Show detection status
        if frame_count % detection_interval == 0:
            cv2.putText(display_frame, "DETECTING...", (10, 70),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

        cv2.imshow(f"Face Tracking & Auto-Save ({method.upper()})", display_frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    
    print(f"\n{'='*60}")
    print(f"  SESSION COMPLETE")
    print(f"{'='*60}")
    print(f"✅ Total unique faces saved: {total_saved}")
    print(f"📁 Location: {output_dir}/")
    if generate_embeddings:
        print(f"✅ Total embeddings generated: {total_embeddings}")
        print(f"📁 Embeddings location: data/embeddings/")
        print(f"📁 Preprocessed images location: data/embeddings/preprocessed/")
    print(f"{'='*60}\n")
