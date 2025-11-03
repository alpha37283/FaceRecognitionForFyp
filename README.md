# Face Detection System

A complete face detection system with live camera and static image support, featuring MTCNN and RetinaFace detectors with intelligent face tracking.

---

## Quick Start

### 1. Setup Environment
```bash
# Activate virtual environment
source myenv/bin/activate

# Install dependencies (if needed)
pip install -r req.txt
```

### 2. Run Live Camera
```bash
# MTCNN (fast)
./run_live.sh

# RetinaFace (accurate)
./run_live_retinaface.sh
```

### 3. Detect Faces in Image
```bash
# Quick detection
./detect_image.sh data/input_images/img1.jpeg

# With specific method
./detect_image.sh path/to/image.jpg mtcnn
./detect_image.sh path/to/image.jpg retinaface
```

---

## Commands Reference

### Live Camera Detection

**MTCNN (Default):**
```bash
./run_live.sh
```

**RetinaFace:**
```bash
./run_live_retinaface.sh
```

**Manual (with options):**
```bash
source myenv/bin/activate
python main.py --mode live --method mtcnn
python main.py --mode live --method retinaface
```

**Controls:**
- Press `q` to quit

---

### Static Image Detection

**Using Script (Recommended):**
```bash
# Show help
./detect_image.sh

# Detect with MTCNN (default)
./detect_image.sh data/input_images/img1.jpeg

# Detect with RetinaFace
./detect_image.sh data/input_images/img1.jpeg retinaface

# Use full path
./detect_image.sh /home/user/Pictures/photo.jpg mtcnn
```

**Manual Command:**
```bash
source myenv/bin/activate
python main.py --mode image --input <image_path> --method <mtcnn|retinaface>
```

**Examples:**
```bash
# MTCNN
python main.py --mode image --input data/input_images/img1.jpeg --method mtcnn

# RetinaFace
python main.py --mode image --input /path/to/photo.jpg --method retinaface
```

---

## Command Options

### Main Entry Point
```bash
python main.py --mode <MODE> --method <METHOD> [--input INPUT]
```

**Parameters:**
- `--mode` (required): `image` or `live`
- `--method` (optional): `mtcnn` or `retinaface` (default: `mtcnn`)
- `--input` (required for image mode): Path to image file

---

## Detection Methods

### MTCNN (Multi-task Cascaded CNN)
- **Speed:** ⚡ Fast (15-20 FPS)
- **Best for:** Frontal faces, controlled environments
- **Command:** `--method mtcnn`

**Use when:**
- Speed is important
- People face camera directly
- Good lighting conditions
- Limited hardware

### RetinaFace
- **Accuracy:** 🎯 State-of-the-art
- **Best for:** Varied angles, challenging conditions
- **Command:** `--method retinaface`

**Use when:**
- Accuracy is critical
- Various face angles
- Poor lighting
- Distant or small faces

---

## Output

### Location
All detected faces are saved to:
```
data/cropped_faces/
```

### File Naming

**Live Camera:**
```
tracked_face_ID{N}_{timestamp}.jpg
```
Example: `tracked_face_ID1_20251102_223045.jpg`

**Static Images:**
```
{source_name}_{timestamp}_face{N}.jpg
```
Examples:
- `img1_20251103_211254_face1.jpg`
- `img2_20251103_211313_face1.jpg`
- `img2_20251103_211313_face2.jpg`

**Benefits:**
- No overwrites - each run creates unique files
- Easy to identify source image
- Timestamp shows when detection was run

---

## Usage Examples

### Example 1: Quick Live Detection
```bash
cd /home/alpha/Desktop/FYP/faceSystem
./run_live.sh
# Press 'q' to quit
```

### Example 2: Detect Face in Photo
```bash
# Copy image to input folder
cp ~/Desktop/photo.jpg data/input_images/

# Detect faces
./detect_image.sh data/input_images/photo.jpg

# View results
ls data/cropped_faces/
```

### Example 3: Batch Process Multiple Images
```bash
source myenv/bin/activate

for img in data/input_images/*.jpg; do
    python main.py --mode image --input "$img" --method mtcnn
done
```

### Example 4: Use RetinaFace for Accuracy
```bash
# Live camera
./run_live_retinaface.sh

# Static image
./detect_image.sh data/input_images/img1.jpeg retinaface
```

### Example 5: Process Image from Any Location
```bash
./detect_image.sh ~/Pictures/family_photo.jpg mtcnn
./detect_image.sh /home/user/Downloads/image.png retinaface
```

---

## Features

### Live Camera
- ✅ Real-time face detection
- ✅ Automatic face tracking with unique IDs
- ✅ Auto-save when new face appears
- ✅ Duplicate prevention (IoU + time filtering)
- ✅ Multi-person support
- ✅ On-screen statistics

**What you see:**
- 🟢 Green boxes = NEW face detected
- 🟠 Orange boxes = Face being tracked
- Stats = "Active Tracks: 2 | Saved: 5"

### Static Images
- ✅ Batch processing support
- ✅ Multiple faces per image
- ✅ Confidence filtering
- ✅ Size filtering
- ✅ Automatic cropping

---

## Directory Structure

```
faceSystem/
├── main.py                    # Entry point
├── modules/
│   ├── detection/
│   │   ├── face_detection_image.py
│   │   └── face_detection_live.py
│   └── detectors/
│       ├── mtcnn_detector.py
│       └── retinaface_detector.py
├── data/
│   ├── input_images/          # Put your images here
│   └── cropped_faces/         # Output faces here
├── run_live.sh                # Quick live MTCNN
├── run_live_retinaface.sh     # Quick live RetinaFace
├── detect_image.sh            # Quick image detection
└── req.txt                    # Dependencies
```

---

## Troubleshooting

### "Module not found"
```bash
source myenv/bin/activate
```

### "Image not found"
```bash
# Use absolute path
./detect_image.sh /full/path/to/image.jpg

# Or check file exists
ls -l data/input_images/
```

### "No faces detected"
```bash
# Try the other method
./detect_image.sh image.jpg retinaface  # if mtcnn failed
./detect_image.sh image.jpg mtcnn       # if retinaface failed
```

### "Webcam not working"
```bash
# Check webcam
ls /dev/video*

# Test with simple capture
python -c "import cv2; cap = cv2.VideoCapture(0); print(cap.isOpened())"
```

### Clear old results
```bash
rm data/cropped_faces/*.jpg
```

---

## Configuration

### Adjusting Detection Settings

Edit `modules/detectors/mtcnn_detector.py`:
```python
min_confidence=0.9    # Detection confidence (0.8-0.99)
min_face_size=40      # Minimum face size in pixels (20-60)
```

Edit `modules/detection/face_detection_live.py`:
```python
detection_interval=60  # Frames between detection (30-90)
iou_threshold=0.5      # Overlap threshold (0.3-0.7)
```

**Recommendations:**
- **Fewer duplicates:** Increase `detection_interval` to 90, `iou_threshold` to 0.6
- **Catch more faces:** Decrease `detection_interval` to 30, `iou_threshold` to 0.4
- **Higher confidence:** Increase `min_confidence` to 0.95
- **Smaller faces:** Decrease `min_face_size` to 20

---

## Performance Tips

### For Speed:
- Use MTCNN (not RetinaFace)
- Increase `detection_interval` to 90
- Close other applications

### For Accuracy:
- Use RetinaFace (not MTCNN)
- Ensure good lighting
- Clean camera lens
- Position face 0.5-2m from camera

### For Storage:
- Each face: ~1-5 KB
- 1000 faces ≈ 1-5 MB
- Very storage efficient

---

## System Requirements

**Minimum:**
- Python 3.11+
- 4GB RAM
- CPU: Intel i3 or equivalent
- Webcam (for live detection)

**Recommended:**
- Python 3.11+
- 8GB RAM
- CPU: Intel i5 or better
- Good lighting
- HD webcam

---

## File Format Support

### Input:
- ✅ JPEG/JPG
- ✅ PNG
- ✅ BMP
- ✅ TIFF

### Output:
- JPEG (default)

---

## Quick Reference Card

```bash
# LIVE DETECTION
./run_live.sh                               # MTCNN (fast)
./run_live_retinaface.sh                    # RetinaFace (accurate)

# IMAGE DETECTION
./detect_image.sh image.jpg                 # MTCNN (default)
./detect_image.sh image.jpg retinaface      # RetinaFace
./detect_image.sh /full/path/image.jpg      # Any location

# MANUAL COMMANDS
python main.py --mode live --method mtcnn
python main.py --mode image --input img.jpg --method retinaface

# VIEW RESULTS
ls -lh data/cropped_faces/

# CLEAR RESULTS
rm data/cropped_faces/*.jpg

# HELP
./detect_image.sh                           # Show help
python main.py --help                       # Show options
```

---

## Common Workflows

### Workflow 1: Attendance System
```bash
# Set up camera at entrance
./run_live.sh

# System automatically:
# - Detects faces
# - Assigns unique IDs
# - Saves each person once
# - Continues tracking

# Review saved faces
ls data/cropped_faces/
```

### Workflow 2: Photo Album Face Extraction
```bash
# Place photos in folder
cp ~/Pictures/*.jpg data/input_images/

# Process all images
for img in data/input_images/*.jpg; do
    ./detect_image.sh "$img" retinaface
done

# All faces now in data/cropped_faces/
```

### Workflow 3: Security Monitoring
```bash
# High accuracy mode
./run_live_retinaface.sh

# Monitors continuously
# Saves all unique visitors
# Each gets unique ID
```

---

## Support

### Check System Status
```bash
source myenv/bin/activate
python -c "from modules.detection.face_detection_live import live_face_detection; print('✅ System OK!')"
```

### View Dependencies
```bash
cat req.txt
```

### Test Webcam
```bash
source myenv/bin/activate
python -c "import cv2; cap = cv2.VideoCapture(0); print('Camera:', cap.isOpened()); cap.release()"
```

---

## Technical Documentation

For detailed technical information, architecture, and algorithms, see `PHASE1.md`.

---

**System is ready to use! 🚀**

