# modules/detection/face_detection_live.py
import cv2
import os
from PIL import Image
from datetime import datetime
from modules.detectors.mtcnn_detector import MTCNNDetector

def live_face_detection(method="mtcnn", auto_save=False, save_interval=30):
    """Live face detection using webcam (MTCNN only).
    
    Args:
        method: Detection method (only 'mtcnn' supported)
        auto_save: If True, automatically saves faces every save_interval frames
        save_interval: Number of frames between auto-saves (default: 30 frames)
    """
    if method.lower() != "mtcnn":
        raise ValueError(f"Unsupported method for now: {method}")

    detector = MTCNNDetector()
    
    # Create output directory if it doesn't exist
    output_dir = "data/cropped_faces"
    os.makedirs(output_dir, exist_ok=True)

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[-] Could not access the webcam.")
        return

    print("[INFO] Live Face Detection Controls:")
    print("      - Press 's' to save current detected faces")
    print("      - Press 'q' to quit")
    if auto_save:
        print(f"      - Auto-save enabled (every {save_interval} frames)")
    
    frame_count = 0
    total_saved = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1

        # Convert to RGB (MTCNN expects RGB PIL image)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(frame_rgb)

        # Detect faces and get bounding boxes
        detections = detector.detect_faces_with_boxes(image)

        # Crop faces for potential saving
        cropped_faces = []
        if detections:
            for box, prob in detections:
                x1, y1, x2, y2 = [int(coord) for coord in box]
                # Crop face from frame
                face_crop = frame_rgb[y1:y2, x1:x2]
                if face_crop.size > 0:  # Make sure crop is valid
                    cropped_faces.append(Image.fromarray(face_crop))
                
                # Draw rectangle
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                # Draw confidence score
                label = f"Face: {prob:.2f}"
                cv2.putText(frame, label, (x1, y1 - 10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # Display face count and saved count
        face_count = len(detections)
        cv2.putText(frame, f"Faces: {face_count} | Saved: {total_saved}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, "Press 's' to save faces", (10, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        # Auto-save logic
        should_save = False
        if auto_save and cropped_faces and (frame_count % save_interval == 0):
            should_save = True

        # Check for key presses
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('q'):
            break
        elif key == ord('s') and cropped_faces:
            should_save = True

        # Save faces if triggered
        if should_save and cropped_faces:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            for i, face in enumerate(cropped_faces):
                filename = f"live_face_{timestamp}_{i+1}.jpg"
                filepath = os.path.join(output_dir, filename)
                face.save(filepath)
                total_saved += 1
            print(f"[+] Saved {len(cropped_faces)} face(s) - Total saved: {total_saved}")

        cv2.imshow("Live Face Detection (MTCNN)", frame)

    cap.release()
    cv2.destroyAllWindows()
    print(f"\n[INFO] Session complete. Total faces saved: {total_saved}")
